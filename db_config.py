import os
from dotenv import load_dotenv


load_dotenv()


def _require(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing environment variable: {name}. "
            "Copy .env.example to .env and fill it in."
        )
    return value


def get_db_config():
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "5433")),
        "database": _require("POSTGRES_DB"),
        "user": _require("POSTGRES_USER"),
        "password": _require("POSTGRES_PASSWORD"),
    }