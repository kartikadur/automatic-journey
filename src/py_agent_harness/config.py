import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ.get("BASE_URL")
API_KEY = os.environ.get("API_KEY")
API_MODEL = os.environ.get("API_MODEL")

