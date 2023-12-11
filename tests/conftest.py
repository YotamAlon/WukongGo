import os

import pytest
from dotenv import load_dotenv

import config

load_dotenv()


@pytest.fixture(autouse=True)
def reset_db():
    os.remove(config.DB_FILE_NAME)
