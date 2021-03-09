from fastapi import FastAPI
from api import url

app = FastAPI()

app.include_router(url.router)


@app.get('/', include_in_schema=False)
def root():
    return
