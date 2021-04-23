import aiofiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from api import url

app = FastAPI()

app.include_router(url.router)
app.mount("/static", StaticFiles(directory="../url-shortener-frontend/build/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["OPTIONS", "POST", "GET"],
    allow_headers=["*"],
)


@app.get('/', include_in_schema=False, response_class=HTMLResponse)
async def root():
    html_file_path = '../url-shortener-frontend/build/index.html'
    try:
        async with aiofiles.open(html_file_path, 'r') as file:
            # Opens the the html file and returns the file as a response
            html_content = await file.read()
            return HTMLResponse(html_content)
    except FileNotFoundError as err:
        print(f"No file with the name: {err.filename}")
