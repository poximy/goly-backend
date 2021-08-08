from fastapi import APIRouter, Request

from src.data import models
from src.data.mongo import Database

router = APIRouter()


@router.post("/register", tags=["auth"])
async def register(request: Request, user: models.User):
    database: Database.User = request.state.db
    created = await database.create_user(user)
    return created
