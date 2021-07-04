import asyncio
import random
from typing import List, Tuple

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.hash import bcrypt

from . import models


class UrlDB:
    def __init__(self, uri) -> None:
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client.url

    def close(self) -> None:
        # Kills the connection with the database
        self.client.close()

    async def get_url(self, collection: str, url_id: str):
        find = {'_id': url_id}
        result: dict = await self.db[collection].find_one(find)
        return result

    async def id_gen(self, collection: str, length: int = 6):
        # Generates a valid Base62 url id that isn't in the DB
        base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        while True:
            url_id = ''.join(random.choices(base, k=length))
            available = await self.get_url(collection, url_id)
            if available is None:
                return url_id

    async def post_url(self, collection: str, url: str):
        if used := await self.db[collection].find_one({'url': url}):
            # Checks if the url is not in use
            # True if the there is data False otherwise
            return models.UrlID(_id=used["_id"])
        # Creates a new id and saves it to the DB
        url_id = await self.id_gen(collection)
        url_data = {'_id': url_id, 'url': url}
        await self.db[collection].insert_one(url_data)
        return models.UrlID(_id=url_data["_id"])

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

    async def user_exists(self, collection: str, user_name: str):
        find = {"user_name": user_name}
        user = await self.db[collection].find_one(find)
        return True if user else False

    async def create_user(self, collection: str, user: models.User):
        exists = await self.user_exists(collection, user.user_name)

        if not exists:
            await self.db[collection].insert_one({
                "user_name": user.user_name,
                "password": bcrypt.hash(user.password),
                "urls": []
            })
            return True
        return False

    async def user_login(self, collection: str, user: models.User):
        exists = await self.user_exists(collection, user.user_name)

        if exists:
            find_data = {"user_name": user.user_name}
            data = await self.db[collection].find_one(find_data)
            verify = bcrypt.verify(user.password, data["password"])
            return verify
