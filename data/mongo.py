import random

import aiofiles

from . import models


async def url_id_gen(collection, length: int = 6) -> str:
    # Generates a valid Base62 url id that isn't in the DB
    base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    while True:
        url_id = ''.join(random.choices(base, k=length))
        available = await get_url(collection, url_id)
        if available is None:
            return url_id


async def get_uri():
    # Finds the uri key and returns a readable string
    async with aiofiles.open("uri.txt", mode='r', encoding='utf-8') as file:
        uri = await file.readline()
        return uri.rstrip("\n")


async def get_url(collection, url_id) -> dict:
    # Looks up the url id from the DB, if found return the url
    find = {'_id': url_id}
    result: dict = await collection.find_one(find)
    return result


async def post_url(collection, url: str) -> models.Url:
    if used := await collection.find_one({'url': url}):
        # Checks if the url is not in use
        # True if the there is data False otherwise
        return models.Url(**used)
    # Creates a new id and saves it to the DB
    url_id = await url_id_gen(collection)
    url_data = {'_id': url_id, 'url': url}
    await collection.insert_one(url_data)
    return models.Url(**url_data)
