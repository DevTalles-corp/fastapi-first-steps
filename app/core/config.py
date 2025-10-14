import os


class settings():
    JWT_SECRET: str = os.getenv("SECRET_KEY", "change-me-in-prod")
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
