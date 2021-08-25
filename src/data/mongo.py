import random
from datetime import date
from string import ascii_letters, digits
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

        async def get(self, url_id: str):
            # finds the given and its associated url
            find = {
                "_id": url_id
            }

            result: dict = await self.collection.find_one(find)
            return result

        async def post(self, url: str):
            # Creates a minified url and saves it to the DB
            base = ascii_letters + digits
            url_id = "".join(random.choices(base, k=self.size))

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
            # returns metadata for each id
            query = {
                "_id": {
                    "$in": url_ids
                }
            }

            return [document async for document in self.collection.find(query)]

    class User:
        def __init__(self, collection):
            self.collection = collection

        async def login(self, username: str, password: str) -> bool:
            find_data = {"user_name": username}

            if (user := await self.collection.find_one(find_data)) is not None:
                verify: bool = bcrypt.verify(password, user["password"])
                return verify
            return False

        async def add_url(self, url_id: str, username: str) -> None:
            # adds a url to a given user via a given id
            find = {"user_name": username}
            update = {
                "$push": {
                    "urls": url_id
                }
            }

            await self.collection.update_one(find, update)

        async def register(self, username: str, password: str) -> bool:
            find = {"user_name": username}

            if not await self.collection.find_one(find):
                await self.collection.insert_one(
                    {
                        "user_name": username,
                        "password": bcrypt.hash(password),
                        "urls": [],
                    }
                )
                return True
            return False

        async def get_urls(self, username: str) -> List[str]:
            # Returns all url ids the user has created
            url_ids: List[str] = []
            user_data = await self.collection.find_one({"user_name": username})

            if user_data is not None:
                url_ids = [url_id for url_id in user_data["urls"]]

            return url_ids

    def close(self) -> None:
        # Kills the connection with the database
        self.client.close()
