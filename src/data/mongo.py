import random
from datetime import date
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.hash import bcrypt


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

        def generator(self) -> str:
            # Generates a valid Base62 url id that isn't in the DB
            base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            return "".join(random.choices(base, k=self.size))

        async def get(self, url_id: str):
            find = {
                "_id": url_id
            }

            result: dict = await self.collection.find_one(find)
            return result

        async def post(self, url: str):
            # Creates a minified url and saves it to the DB
            url_id = self.generator()

            url_metadata = {
                "_id": url_id,
                "url": url,
                "created": str(date.today()),
                "clicks": 0,
            }

            await self.collection.insert_one(url_metadata)
            return url_metadata

        async def click(self, url_id: str) -> None:
            # Increments the click count
            update = {"_id": url_id}
            increment = {
                "$inc": {
                    "clicks": 1
                }
            }

            await self.collection.update_one(update, increment)

        async def metadata(self, url_ids: List[str]) -> List[dict]:
            query = {
                "_id": {
                    "$in": url_ids
                }
            }

            return [document async for document in self.collection.find(query)]

    class User:
        def __init__(self, collection):
            self.collection = collection

        async def login(self, user_name: str, password: str) -> bool:
            exists = await self.exists(user_name)

            if exists:
                find_data = {"user_name": user_name}
                data = await self.collection.find_one(find_data)
                verify: bool = bcrypt.verify(password, data["password"])
                return verify
            return False

        async def exists(self, user_name: str) -> bool:
            find = {"user_name": user_name}
            user = await self.collection.find_one(find)
            return True if user else False

        async def add_url(self, url_id: str, name: str) -> None:
            find = {"user_name": name}
            update = {
                "$push": {
                    "urls": url_id
                }
            }

            await self.collection.update_one(find, update)

        async def register(self, username: str, password: str) -> bool:
            find = {"user_name": username}
            exists = await self.collection.find_one(find)

            if not exists:
                await self.collection.insert_one(
                    {
                        "user_name": username,
                        "password": bcrypt.hash(password),
                        "urls": [],
                    }
                )
                return True
            return False

        async def get_urls(self, user: str) -> List[str]:
            # Returns all url ids the user has created
            user_data = await self.collection.find_one({"user_name": user})
            url_ids: List[str] = []

            if user_data is not None:
                url_ids = [url_id for url_id in user_data["urls"]]

            return url_ids

    def close(self) -> None:
        # Kills the connection with the database
        self.client.close()
