from data import models, mongo
from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/register")
async def register(request: Request, user: models.User):
    database: mongo.UrlDB = request.state.db
    created = await database.create_user("user", user)
    return created
