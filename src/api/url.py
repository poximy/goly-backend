from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import RedirectResponse

from src.data import models
from src.data.mongo import Database

router = APIRouter(tags=["url"])


@router.get("/{url_id}", status_code=301)
async def get_url(background_tasks: BackgroundTasks, request: Request,
                  url_id: str):
    url: Database.Url = request.state.url
    background_tasks.add_task(url.click, url_id)

    result = await url.get(url_id)
    if result:
        return RedirectResponse(result["url"])
    detail = {"error": f"{url_id} does not exist"}
    raise HTTPException(status_code=404, detail=detail)


@router.post("/", response_model=models.UrlID, status_code=201)
async def post_url(request: Request,
                   background_tasks: BackgroundTasks,
                   body: models.UrlPOST):
    url_collection: Database.Url = request.state.url
    user_collection: Database.User = request.state.user

    result = await url_collection.post(body.url)

    if body.user is not None:
        background_tasks.add_task(user_collection.add_url, result.id,
                                  body.user)
    return result
