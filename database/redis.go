package database

import "github.com/go-redis/redis/v8"

func RedisClient() *redis.Client {
	opt, err := redis.ParseURL("")
	if err != nil {
		panic(err)
	}

	return redis.NewClient(opt)
}
