from fastapi import FastAPI
from api import url

app = FastAPI()

app.include_router(url.router)


@app.get('/')
def root():
    return
