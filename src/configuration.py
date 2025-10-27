import os
from fastapi import FastAPI
from src.middlewares import BasicAuthBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from tortoise.contrib.fastapi import register_tortoise
from src.routes import seller, customer
from dotenv import load_dotenv

load_dotenv()

TORTOISE_MODELS = [
    "src.models", 
    "aerich.models"
]

TORTOISE_ORM = {
    "connections": { "default": os.getenv('DATABASE_URL', 'sqlite://db.sqlite3') },
    "apps": {
        "models": {
            "models": TORTOISE_MODELS,
            "default_connection": "default",
        }
    },
}

def configure_db(application: FastAPI, fake_db=False):
    if fake_db:
        TORTOISE_ORM['connections']['default'] = "sqlite://:memory:"

    register_tortoise(
        application,
        generate_schemas=True,
        add_exception_handlers=True,
        config=TORTOISE_ORM,
    )

def configure_routes(application: FastAPI):
    application.include_router(seller.router)
    application.include_router(customer.router)

def configure_middlewares(application: FastAPI):
    application.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())