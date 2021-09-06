from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api import auth, metadata, url, user
from src.data.settings import Settings
from src.data.mongo import Database

app = FastAPI()

# values from .env file
config = Settings()

# Starts the Database
database = Database(config.mongo_uri)
# Database collection connections
url_collection = database.url(config.url_collection)
user_collection = database.user(config.user_collection)

JWT = config.jwt

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["OPTIONS", "POST", "GET", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def collections(request: Request, call_next):
    # Passes the database via request.state
    request.state.url = url_collection
    request.state.user = user_collection
    response = await call_next(request)
    return response


@app.middleware("http")
async def jwt(request: Request, call_next):
    request.state.jwt = JWT
    response = await call_next(request)
    return response


app.include_router(url.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(metadata.router)


@app.on_event("shutdown")
def shutdown_event():
    database.close()
