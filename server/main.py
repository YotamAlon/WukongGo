from dotenv import load_dotenv

load_dotenv()

from server.endpoints import app

app = app
