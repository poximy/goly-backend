import aiofiles


async def get_uri():
    async with aiofiles.open("uri.txt", mode='r', encoding='utf-8') as file:
        uri = await file.readline()
        return uri.rstrip("\n")


async def get_url(collection, url_id) -> dict:
    find = {'_id': url_id}
    result: dict = await collection.find_one(find)
    return result
