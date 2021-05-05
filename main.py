from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import url

app = FastAPI()

app.include_router(url.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["OPTIONS", "POST", "GET"],
    allow_headers=["*"],
)
