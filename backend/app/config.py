import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = REPO_ROOT / ".data" / "assets.sqlite3"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_DATABASE_URL,
)

DATABASE_KIND = DATABASE_URL.split(":", maxsplit=1)[0]
SKIP_DB_INIT = os.getenv("ASSETS_SKIP_DB_INIT", "").lower() in {"1", "true", "yes"}
