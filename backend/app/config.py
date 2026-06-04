import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = REPO_ROOT / ".data" / "assets.sqlite3"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
DEFAULT_CORS_ORIGIN_REGEX = r"^http://(localhost|127\.0\.0\.1):\d+$"
DEFAULT_APP_VERSION = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def parse_csv_env(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name, "")
    if not value.strip():
        return default

    return [item.strip() for item in value.split(",") if item.strip()]


RAW_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_DATABASE_URL,
)
DATABASE_URL = normalize_database_url(RAW_DATABASE_URL)

DATABASE_KIND = RAW_DATABASE_URL.split(":", maxsplit=1)[0]
SKIP_DB_INIT = os.getenv("ASSETS_SKIP_DB_INIT", "").lower() in {"1", "true", "yes"}
CORS_ALLOWED_ORIGINS = parse_csv_env("ASSETS_CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
CORS_ALLOW_ORIGIN_REGEX = os.getenv("ASSETS_CORS_ORIGIN_REGEX", DEFAULT_CORS_ORIGIN_REGEX)
APP_VERSION = os.getenv("ASSETS_VERSION", DEFAULT_APP_VERSION)
