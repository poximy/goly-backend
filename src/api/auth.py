import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.data import models, mongo

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token")
async def token_gen(request: Request,
                    form_data: OAuth2PasswordRequestForm = Depends()):
    database: mongo.UrlDB = request.state.db
    data = {"user_name": form_data.username, "password": form_data.password}
    user = models.User(**data)
    valid = await database.user_login("user", user)
    if valid:
        token_data = {"user": form_data.username}
        token = jwt.encode(token_data, request.state.jwt)
        return {"access_token": token}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect user name or password",
    )
