package database

import (
	"os"

	"github.com/go-redis/redis/v8"
	"github.com/joho/godotenv"
)

// RedisClient creates a redis database connection
func RedisClient() *redis.Client {
	godotenv.Load()
	URI := os.Getenv("REDIS")

	opt, err := redis.ParseURL(URI)
	if err != nil {
		panic(err)
	}

	return redis.NewClient(opt)
}
