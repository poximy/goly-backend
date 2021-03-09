import random

import aiofiles


def id_gen(length: int = 6) -> str:
    # Generates a Base62 id
    base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    url_id = ''
    for _ in range(length):
        url_id += random.choice(base)
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
