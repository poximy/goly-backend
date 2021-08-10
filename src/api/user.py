from fastapi import APIRouter, Body, Request

from src.data.mongo import Database

router = APIRouter()


@router.post("/register", tags=["auth"])
async def register(request: Request,
                   username: str = Body(..., embed=True),
                   password: str = Body(..., embed=True)):
    # Returns true if exists else false
    user_collection: Database.User = request.state.user
    created = await user_collection.register(username, password)
    return created
