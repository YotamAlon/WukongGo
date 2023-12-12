from dotenv import load_dotenv

load_dotenv()

import os

import pytest
from starlette.testclient import TestClient

import config
from server.endpoints import app


@pytest.fixture(autouse=True)
def reset_db():
    if os.path.exists(os.environ[config.DB_FILE_NAME]):
        os.remove(os.environ[config.DB_FILE_NAME])


client = TestClient(app)
