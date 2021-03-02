import aiofiles


async def get_uri():
    async with aiofiles.open("uri.txt", mode='r', encoding='utf-8') as file:
        uri = await file.readline()
        return uri.rstrip("\n")
