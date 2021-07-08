from typing import List

import jwt
from data import models
from data.mongo import UrlDB
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(
    tags=["metadata"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/user/{user_name}", response_model=List[models.UrlMetadata])
async def metadata(request: Request, user_name: str,
                   token: str = Depends(oauth2_scheme)):
    jwt_data = jwt.decode(token, request.state.jwt, algorithms=["HS256"])
    if user_name == jwt_data["user"]:
        database: UrlDB = request.state.db
        user_urls = await database.get_user_urls("user", user_name)
        data = await database.get_metadata("metadata", user_urls)
        return data
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Cannot access data from other accounts",
    )
