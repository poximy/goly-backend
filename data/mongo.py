import asyncio
import random
from typing import List, Tuple

import aiofiles

from . import models


async def url_id_gen(collection, length: int = 6):
    # Generates a valid Base62 url id that isn't in the DB
    base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    while True:
        url_id = ''.join(random.choices(base, k=length))
        available = await get_url(collection, url_id)
        if available is None:
            return url_id


async def get_uri():
    # Finds the uri key and returns a readable string
    try:
        async with aiofiles.open("uri.txt", mode='r', encoding='utf-8') as file:
            uri = await file.readline()
            uri_text = uri.rstrip("\n")
            if uri_text == "" or not uri_text.startswith("mongodb+srv://"):
                raise ValueError("File should contain a URI")
            return uri_text
    except FileNotFoundError as err:
        print(f"No file with the name: {err.filename}")
        print("Create a uri.txt file with a MongoDB URI")
    except ValueError as err:
        print(err)


async def get_url(collection, url_id):
    # Looks up the url id from the DB, if found return the url
    find = {'_id': url_id}
    result: dict = await collection.find_one(find)
    return result


async def post_url(collection, url: str):
    if used := await collection.find_one({'url': url}):
        # Checks if the url is not in use
        # True if the there is data False otherwise
        return models.UrlID(_id=used["_id"])
    # Creates a new id and saves it to the DB
    url_id = await url_id_gen(collection)
    url_data = {'_id': url_id, 'url': url}
    await collection.insert_one(url_data)
    return models.UrlID(_id=url_data["_id"])


async def get_user_urls(collection, user_name):
    user_data = await collection.find_one({"user_name": user_name})
    url_ids: List[models.UrlID] = []
    if user_data is not None:
        for url_id in user_data["urls"]:
            url = models.UrlID(_id=url_id)
            url_ids.append(url)
    return url_ids


async def get_metadata(collection, url_ids: List[models.UrlID]):
    url_metadata = []
    for url_id in url_ids:
        url = collection.find_one({"_id": url_id.id})
        url_metadata.append(url)
    values: Tuple[dict] = await asyncio.gather(*url_metadata)
    return [models.UrlMetadata(**value) for value in values]
