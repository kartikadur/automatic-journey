import os

from dotenv import load_dotenv

load_dotenv()


def get_runtime_config():
    """Return configured runtime values and fail fast when required settings are missing."""
    config = {
        "BASE_URL": os.environ.get("BASE_URL"),
        "API_KEY": os.environ.get("API_KEY"),
        "API_MODEL": os.environ.get("API_MODEL"),
    }
    missing = [name for name, value in config.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )
    return config

