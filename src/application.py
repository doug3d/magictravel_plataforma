from fastapi import FastAPI
from src.configuration import configure_db, configure_routes


def create_application(fake_db=False):
    app = FastAPI()

    configure_db(app, fake_db)
    configure_routes(app)

    return app

app = create_application()
