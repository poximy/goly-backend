import asyncio
import random
from datetime import date
from typing import List, Tuple

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.hash import bcrypt

from . import models


class UrlDB:
    def __init__(self, uri: str) -> None:
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client.url

    def close(self) -> None:
        # Kills the connection with the database
        self.client.close()

    async def get_user_urls(self, collection: str, user: str):
        # Returns all url ids the user has created
        user_data = await self.db[collection].find_one({"user_name": user})
        url_ids: List[models.UrlID] = []
        if user_data is not None:
            for url_id in user_data["urls"]:
                url = models.UrlID(_id=url_id)
                url_ids.append(url)
        return url_ids

    async def get_metadata(self, collection: str, url_ids: List[models.UrlID]):
        # Gets the data from a specific url id
        url_metadata = []
        for url_id in url_ids:
            url = self.db[collection].find_one({"_id": url_id.id})
            url_metadata.append(url)
        values: Tuple[dict] = await asyncio.gather(*url_metadata)
        return [models.UrlMetadata(**value) for value in values]

    async def add_metadata(self, collection: str, url_id: str):
        used = await self.db[collection].find_one({"url": url_id})
        if used:
            return
        metadata = {
            "_id": url_id,
            "created": str(date.today()),
            "clicks": 0
        }
        await self.db[collection].insert_one(metadata)

    async def user_exists(self, collection: str, user_name: str):
        find = {"user_name": user_name}
        user = await self.db[collection].find_one(find)
        return True if user else False

    async def create_user(self, collection: str, user: models.User):
        exists = await self.user_exists(collection, user.user_name)

        if not exists:
            await self.db[collection].insert_one(
                {
                    "user_name": user.user_name,
                    "password": bcrypt.hash(user.password),
                    "urls": [],
                }
            )
            return True
        return False

    async def click(self, collection: str, url_id: str):
        # Increments the click count
        update = {"_id": url_id}
        increment = {
            "$inc": {
                "clicks": 1
            }
        }

        await self.db[collection].update_one(update, increment)

    async def user_url(self, collection: str, url_id: str, user: str):
        find = {"user_name": user}
        update = {
            "$push": {
                "urls": url_id
            }
        }

        await self.db[collection].update_one(find, update)


class Database:
    def __init__(self, mongo_uri: str):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client.url

    def url(self, collection: str):
        return self.Url(self.db[collection])

    def user(self, collection: str):
        return self.User(self.db[collection])

    class Url:
        def __init__(self, collection, size: int = 6):
            self.collection = collection
            self.size = size

        async def generator(self):
            # Generates a valid Base62 url id that isn't in the DB
            base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            return "".join(random.choices(base, k=self.size))

        async def get(self, url_id: str):
            find = {"_id": url_id}
            result: dict = await self.collection.find_one(find)
            return result

        async def post(self, url: str):
            if used := await self.collection.find_one({"url": url}):
                # Checks if the url is not in use
                # True if the there is data False otherwise
                return models.UrlID(_id=used["_id"])
            # Creates a new id and saves it to the DB
            url_id = await self.generator()

            url_data = {
                "_id": url_id,
                "url": url
            }

            await self.collection.insert_one(url_data)
            return models.UrlID(_id=url_data["_id"])

    class User:
        def __init__(self, collection):
            self.collection = collection

        async def login(self, user: models.User):
            exists = await self.exists(user.user_name)

            if exists:
                find_data = {"user_name": user.user_name}
                data = await self.collection.find_one(find_data)
                verify = bcrypt.verify(user.password, data["password"])
                return verify

        async def exists(self, user_name: str):
            find = {"user_name": user_name}
            user = await self.collection.find_one(find)
            return True if user else False

    def close(self) -> None:
        # Kills the connection with the database
        self.client.close()
