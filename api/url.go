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
	"go.mongodb.org/mongo-driver/mongo/options"
)

var ctx = context.Background()

var rdb = database.RedisClient()
var col = database.MongoClient().Database("goly").Collection("url")

const choice = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

func UrlRouter() http.Handler {
	fmt.Println("Url router is running")
	r := chi.NewRouter()

	r.Get("/{id}", getUrl)
	r.Post("/", postUrl)

	return r
}

type Goly struct {
	ID     string `json:"id" bson:"_id"`
	Url    string `json:"url" bson:"url"`
	Clicks int    `json:"clicks" bson:"clicks"`
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

	filterQuery := bson.M{"_id": id}
	UpdateQuery := bson.M{"$inc": bson.M{"clicks": 1}}
	_, err = col.UpdateOne(ctx, filterQuery, UpdateQuery)
	if err != nil {
		http.Error(w, "error: something went wrong", http.StatusInternalServerError)
		return
	}

	http.Redirect(w, r, url, http.StatusMovedPermanently)
}

func findAndCache(id string) (string, error) {
	var goly map[string]string

	filterQuery := bson.M{"_id": id}
	UpdateQuery := bson.M{"$inc": bson.M{"clicks": 1}}
	optionsQuery := options.FindOneAndUpdate().SetProjection(bson.M{
		"_id": false,
		"url": true,
	})

	res := col.FindOneAndUpdate(ctx, filterQuery, UpdateQuery, optionsQuery)
	err := res.Err()
	if err == mongo.ErrNoDocuments {
		return "", errors.New("error: id does not exist")
	} else if err != nil {
		return "", errors.New("error: something went wrong")
	}

	err = res.Decode(&goly)
	if err != nil {
		return "", errors.New("error: something went wrong while caching")
	}

	err = rdb.Set(ctx, id, goly["url"], 120*time.Second).Err()
	if err != nil {
		return "", errors.New("error: something went wrong while caching")
	}
	return goly["url"], nil
}

// Creates a shortened url & saves it to redis
func postUrl(w http.ResponseWriter, r *http.Request) {
	body, err := verifyPostBody(r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err = CacheAndSave(body)
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

	if body.Url == "" {
		return Goly{}, errors.New("error: missing field url")
	}

	body.ID = generateID()
	body.Clicks = 0

	return body, nil
}

func generateID() string {
	var id string

	length := len(choice)
	rand.Seed(time.Now().UnixNano())

	for i := 0; i < 6; i++ {
		char := choice[rand.Intn(length)]
		id += string(char)
	}

	return id
}

func CacheAndSave(g Goly) error {
	err := rdb.Set(ctx, g.ID, g.Url, 120*time.Second).Err()
	if err != nil {
		return errors.New("error: something went wrong while caching")
	}

	_, err = col.InsertOne(ctx, g)
	if err != nil {
		return errors.New("error: something went wrong saving")
	}

	return nil
}
