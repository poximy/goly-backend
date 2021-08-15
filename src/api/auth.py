import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from src.data.mongo import Database

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenResponse(BaseModel):
    access_token: str


@router.post("/token", response_model=TokenResponse)
async def token(request: Request,
                form_data: OAuth2PasswordRequestForm = Depends()):
    user_collection: Database.User = request.state.user

    valid = await user_collection.login(form_data.username, form_data.password)
    if valid:
        token_data = {"user": form_data.username}
        jwt_token = jwt.encode(token_data, request.state.jwt)
        return {"access_token": jwt_token}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect user name or password",
    )
