from fastapi import APIRouter, Request

from src.data import models, mongo

router = APIRouter()


@router.post("/register", tags=["auth"])
async def register(request: Request, user: models.User):
    database: mongo.UrlDB = request.state.db
    created = await database.create_user("user", user)
    return created
