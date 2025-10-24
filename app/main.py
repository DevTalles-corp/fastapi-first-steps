
import os
from fastapi import FastAPI
from app.core.db import Base, engine
from dotenv import load_dotenv
from app.api.v1.posts.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.uploads.router import router as upload_router
from app.api.v1.tags.router import router as tag_router
from app.api.v1.categories.router import router as category_router
from fastapi.staticfiles import StaticFiles

from app.core.middleware import register_middleware

load_dotenv()

MEDIA_DIR = "app/media"


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog", swagger_ui_parameters={
                  "persistAuthorization": True})
    Base.metadata.create_all(bind=engine)  # dev
    register_middleware(app)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router)
    app.include_router(tag_router)
    app.include_router(upload_router)
    app.include_router(category_router)

    os.makedirs(MEDIA_DIR, exist_ok=True)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

    return app


app = create_app()
