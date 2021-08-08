from typing import List

import jwt
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer

from src.data import models
from src.data.mongo import Database

router = APIRouter(tags=["metadata"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/user/metadata", response_model=List[models.UrlMetadata])
async def metadata(request: Request, token: str = Depends(oauth2_scheme)):
    user_collection: Database.User = request.state.user

    jwt_data = jwt.decode(token, request.state.jwt, algorithms=["HS256"])
    user_urls = await user_collection.get_urls(jwt_data["user"])
    return user_urls
