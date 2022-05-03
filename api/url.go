package api

import (
	"net/http"

	"github.com/go-chi/chi/v5"
)

func UrlRouter() http.Handler {
	r := chi.NewRouter()
	return r
}
