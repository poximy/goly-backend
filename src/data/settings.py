from pydantic import BaseSettings


class Settings(BaseSettings):
    # Environment variables (.env)
    jwt: str = "JWT_SECRET"

    mongo_uri: str = "MONGO_URI"
    url_collection: str = "URL_COLLECTION"
    user_collection: str = "USER_COLLECTION"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
