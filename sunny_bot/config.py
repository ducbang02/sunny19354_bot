"""Read and validate local configuration without exposing secrets."""
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Config:
    token: str = field(repr=False)
    owner_id: int
    timezone: ZoneInfo
    database_path: Path


def load_config(env_file: Path | None = None) -> Config:
    load_dotenv(env_file if env_file is not None else PROJECT_ROOT / ".env", override=False)
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not re.fullmatch(r"[0-9]{6,12}:[A-Za-z0-9_-]{30,}", token):
        raise ValueError("TELEGRAM_BOT_TOKEN is missing or invalid; configure it locally in .env.")
    owner = os.environ.get("OWNER_TELEGRAM_ID", "").strip()
    if not re.fullmatch(r"[0-9]{1,16}", owner) or not 0 < int(owner) < 2**52:
        raise ValueError("OWNER_TELEGRAM_ID must be a positive numeric Telegram user ID.")
    zone = os.environ.get("BOT_TIMEZONE", "Asia/Bangkok").strip()
    try:
        timezone = ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError("BOT_TIMEZONE must be a valid IANA timezone.") from None
    database = os.environ.get("DATABASE_PATH", "data/bot.sqlite3").strip()
    if not database or "\x00" in database:
        raise ValueError("DATABASE_PATH must be a nonempty local file path.")
    path = Path(database).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return Config(token, int(owner), timezone, path)
