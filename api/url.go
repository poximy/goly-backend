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

	"github.com/poximy/goly-backend/database"

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

// URLRouter handles creation & redirects
func URLRouter() http.Handler {
	fmt.Println("Url router is running")
	r := chi.NewRouter()

	r.Get("/{id}", GetURL)
	r.Post("/", PostURL)

	return r
}

type goly struct {
	ID     string `json:"id" bson:"_id"`
	URL    string `json:"url" bson:"url"`
	Clicks int    `json:"clicks" bson:"clicks"`
}

// GetURL redirects to original url
func GetURL(w http.ResponseWriter, r *http.Request) {
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

	err = cache(id, goly["url"])
	if err != nil {
		return "", err
	}

	return goly["url"], nil
}

// PostURL Creates a shortened url & saves it to redis
func PostURL(w http.ResponseWriter, r *http.Request) {
	body, err := verifyPostBody(r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err = cacheAndSave(body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = json.NewEncoder(w).Encode(body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	w.Header().Add("Content-Type", "application/json")
}

// Verifies request data is valid
func verifyPostBody(data io.Reader) (goly, error) {
	var body goly
	err := json.NewDecoder(data).Decode(&body)
	if err != nil {
		return goly{}, errors.New("error: unable to parse json")
	}

	if body.URL == "" {
		return goly{}, errors.New("error: missing field url")
	}

	body.ID = generateID()
	body.Clicks = 0

	return body, nil
}

func generateID() string {
	var id string
	const idLength int = 6
	const choiceLength int = len(choice)

	rand.Seed(time.Now().UnixNano())

	for i := 0; i < idLength; i++ {
		char := choice[rand.Intn(choiceLength)]
		id += string(char)
	}

	return id
}

func cacheAndSave(g goly) error {
	c := make(chan error)
	const errAmount int = 2

	go func() {
		err := cache(g.ID, g.URL)
		c <- err
	}()

	go save(g, c)

	for i := 0; i < errAmount; i++ {
		err := <-c
		if err != nil {
			return err
		}
	}
	return nil
}

func cache(id string, url string) error {
	const cacheTime = 120 * time.Second

	err := rdb.Set(ctx, id, url, cacheTime).Err()
	if err != nil {
		return errors.New("error: something went wrong while caching")
	}

	return nil
}

func save(g goly, c chan<- error) {
	_, err := col.InsertOne(ctx, g)
	if err != nil {
		c <- errors.New("error: something went wrong saving")
		return
	}
	c <- nil
}
