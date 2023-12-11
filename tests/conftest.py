import os

import pytest
from dotenv import load_dotenv

import config

load_dotenv()


@pytest.fixture(autouse=True)
def reset_db():
    if os.path.exists(os.environ[config.DB_FILE_NAME]):
        os.remove(os.environ[config.DB_FILE_NAME])
