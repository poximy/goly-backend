package api

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"time"

	"github.com/poximy/url-shortener-backend/database"

	"github.com/go-chi/chi/v5"
	"github.com/go-redis/redis/v8"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

var ctx = context.Background()

var rdb = database.RedisClient()
var col = database.MongoClient().Database("goly").Collection("url")

const choice = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

func UrlRouter() http.Handler {
	r := chi.NewRouter()
	fmt.Println("Url router is running")

	r.Get("/{id}", getUrl)
	r.Post("/", postUrl)

	return r
}

type Goly struct {
	ID       string `json:"id" bson:"_id"`
	Redirect string `json:"redirect" bson:"redirect"`
}

func (g *Goly) IdGen() {
	var id string

	length := len(choice)
	rand.Seed(time.Now().UnixNano())

	for i := 0; i < 6; i++ {
		char := choice[rand.Intn(length)]
		id += string(char)
	}

	g.ID = id
}

func (g Goly) CacheAndSave() error {
	err := rdb.Set(ctx, g.ID, g.Redirect, 120*time.Second).Err()
	if err != nil {
		return errors.New("error: something went wrong while caching")
	}

	_, err = col.InsertOne(ctx, g)
	if err != nil {
		return errors.New("error: something went wrong saving")
	}

	return nil
}

// Redirects to original url
func getUrl(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	url, err := rdb.Get(ctx, id).Result()

	switch {
	case err == redis.Nil:
		url, err := findAndCache(id)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		http.Redirect(w, r, url, http.StatusMovedPermanently)
		return
	case err != nil:
		http.Error(w, "error: something went wrong", http.StatusInternalServerError)
		return
	}

	http.Redirect(w, r, url, http.StatusMovedPermanently)
}

func findAndCache(id string) (string, error) {
	var res Goly
	filterQuery := bson.D{{Key: "_id", Value: id}}

	err := col.FindOne(ctx, filterQuery).Decode(&res)
	if err == mongo.ErrNoDocuments {
		return "", errors.New("error: id does not exist")
	} else if err != nil {
		return "", errors.New("error: something went wrong")
	}

	err = rdb.Set(ctx, res.ID, res.Redirect, 120*time.Second).Err()
	if err != nil {
		return "", errors.New("error: something went wrong while caching")
	}
	return res.Redirect, nil
}

// Creates a shortened url & saves it to redis
func postUrl(w http.ResponseWriter, r *http.Request) {
	body, err := verifyPostBody(r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err = body.CacheAndSave()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Add("Content-Type", "application/json")
	err = json.NewEncoder(w).Encode(body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

// Verifies request data is valid
func verifyPostBody(data io.Reader) (Goly, error) {
	var body Goly
	err := json.NewDecoder(data).Decode(&body)
	if err != nil {
		return Goly{}, errors.New("error: unable to parse json")
	}

	if body.Redirect == "" {
		return Goly{}, errors.New("error: missing field url")
	}

	body.IdGen()

	return body, nil
}
