import aiofiles
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from api import url

app = FastAPI()

app.include_router(url.router)
app.mount("/static", StaticFiles(directory="../url-shortener-frontend/build/static"), name="static")



@app.get('/', include_in_schema=False, response_class=HTMLResponse)
async def root():
    html_file_path = '../url-shortener-frontend/build/index.html'
    async with aiofiles.open(html_file_path, 'r') as file:
        # Opens the the html file and returns the file as a response
        html_content = await file.read()
        return HTMLResponse(html_content)
