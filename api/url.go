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
)

var ctx = context.Background()

func UrlRouter() http.Handler {
	r := chi.NewRouter()

	r.Get("/{id}", getUrl)
	r.Post("/", postUrl)

	return r
}

// Redirects to original url
func getUrl(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")

	rdb := database.RedisClient()
	url, err := rdb.Get(ctx, id).Result()

	switch {
	case err == redis.Nil:
		http.Error(w, "error: id does not exist", http.StatusInternalServerError)
		return
	case err != nil:
		http.Error(w, "error: something went wrong", http.StatusInternalServerError)
		return
	case url == "":
		http.Error(w, "error: url not found", http.StatusInternalServerError)
		return
	}

	http.Redirect(w, r, url, http.StatusMovedPermanently)
}

type PostBody struct {
	ID  string `json:"id"`
	Url string `json:"url"`
}

// Creates a shortend url & saves it to redis
func postUrl(w http.ResponseWriter, r *http.Request) {
	body, err := verifyPostBody(r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	err = cachePost(body)
	if err != nil {
		http.Error(w, "error: something went wrong while saving", http.StatusInternalServerError)
		return
	}

	w.Header().Add("Content-Type", "application/json")
	err = json.NewEncoder(w).Encode(body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func cachePost(data PostBody) error {
	rdb := database.RedisClient()
	err := rdb.Set(ctx, data.ID, data.Url, 120*time.Second).Err()

	if err != nil {
		fmt.Println(err)
		return errors.New("error: something went wrong")
	}
	return nil
}

// Verifies request data is valid
func verifyPostBody(data io.Reader) (PostBody, error) {
	var body PostBody
	err := json.NewDecoder(data).Decode(&body)
	if err != nil {
		return PostBody{}, errors.New("error: unable to parse json")
	}

	if body.Url == "" {
		return PostBody{}, errors.New("error: missing field url")
	}

	body.ID = idGen()

	return body, nil
}

const choice = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

func idGen() string {
	var id string

	length := len(choice)
	rand.Seed(time.Now().UnixNano())

	for i := 0; i < 6; i++ {
		char := choice[rand.Intn(length)]
		id += string(char)
	}

	return id
}
