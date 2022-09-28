package main

import (
	"net/http"
	"os"

	"github.com/poximy/goly-backend/api"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
)

func main() {
	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins: []string{"https://*", "http://*"},
		AllowedMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders: []string{"Accept", "Authorization", "Content-Type", "application/json"},
	}))

	r.Mount("/", api.URLRouter())

	err := http.ListenAndServe(port(), r)
	if err != nil {
		panic(err)
	}
}

func port() string {
	portNum := os.Getenv("PORT")
	if portNum == "" {
		portNum = "8080" // Default port if not specified
	}
	return ":" + portNum
}
