

from fastapi import FastAPI
from app.core.db import Base, engine
from dotenv import load_dotenv
from app.api.v1.posts.router import router as post_router

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")
    Base.metadata.create_all(bind=engine)  # dev

    app.include_router(post_router)

    return app


app = create_app()
