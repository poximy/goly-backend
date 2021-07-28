from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Request
from fastapi.responses import RedirectResponse

from src.data import models
from src.data.mongo import UrlDB

router = APIRouter(tags=["url"])


@router.get("/{url_id}", status_code=301)
async def get_url(background_tasks: BackgroundTasks, request: Request,
                  url_id: str):
    database: UrlDB = request.state.db
    background_tasks.add_task(database.click, "metadata", url_id)

    result = await database.get_url("links", url_id)
    if result:
        return RedirectResponse(result["url"])
    detail = {"error": f"{url_id} does not exist"}
    raise HTTPException(status_code=404, detail=detail)


@router.post("/", response_model=models.UrlID, status_code=201)
async def post_url(background_tasks: BackgroundTasks, request: Request,
                   url: str = Body(..., embed=True)):
    database: UrlDB = request.state.db

    result = await database.post_url("links", url)
    background_tasks.add_task(database.add_metadata, "metadata", result.id)
    return result
