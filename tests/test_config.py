from pathlib import Path
import subprocess
import sys

import pytest

from sunny_bot.config import load_config

FAKE_TOKEN = "123456:" + "a" * 35
KEYS = ["TELEGRAM_BOT_TOKEN", "OWNER_TELEGRAM_ID", "BOT_TIMEZONE", "DATABASE_PATH"]


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    for key in KEYS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", FAKE_TOKEN)
    monkeypatch.setenv("OWNER_TELEGRAM_ID", "42")
    return tmp_path / "missing.env"


@pytest.mark.parametrize("key,value", [
    ("TELEGRAM_BOT_TOKEN", ""), ("TELEGRAM_BOT_TOKEN", "invalid-secret"),
    ("OWNER_TELEGRAM_ID", ""), ("OWNER_TELEGRAM_ID", "0"),
    ("OWNER_TELEGRAM_ID", "-1"), ("OWNER_TELEGRAM_ID", "abc"),
    ("OWNER_TELEGRAM_ID", "9" * 5000), ("OWNER_TELEGRAM_ID", str(2**52)),
    ("BOT_TIMEZONE", "Mars/Unknown"), ("BOT_TIMEZONE", ""),
    ("DATABASE_PATH", ""),
])
def test_invalid_config_fails_without_exposing_value(monkeypatch, clean_env, key, value):
    monkeypatch.setenv(key, value)
    with pytest.raises(ValueError) as exc:
        load_config(clean_env)
    assert key in str(exc.value)
    assert FAKE_TOKEN not in str(exc.value)
    assert "invalid-secret" not in str(exc.value)


def test_defaults_and_token_free_repr(clean_env):
    config = load_config(clean_env)
    assert config.owner_id == 42
    assert str(config.timezone) == "Asia/Bangkok"
    assert config.database_path == Path(__file__).resolve().parents[1] / "data/bot.sqlite3"
    assert FAKE_TOKEN not in repr(config)


def test_dotenv_does_not_override_process_env(clean_env):
    clean_env.write_text("OWNER_TELEGRAM_ID=99\nBOT_TIMEZONE=Asia/Ho_Chi_Minh\nDATABASE_PATH=custom/data.db\n")
    config = load_config(clean_env)
    assert config.owner_id == 42
    assert str(config.timezone) == "Asia/Ho_Chi_Minh"
    assert config.database_path.name == "data.db"


def test_check_config_does_not_create_database_or_call_network(monkeypatch, clean_env, tmp_path):
    db = tmp_path / "unused.sqlite3"
    monkeypatch.setenv("DATABASE_PATH", str(db))
    result = subprocess.run([sys.executable, "-m", "sunny_bot", "--check-config"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "OK" in result.stdout
    assert not db.exists()
    assert FAKE_TOKEN not in result.stdout + result.stderr


def test_cli_missing_owner_exits_safely(monkeypatch, clean_env):
    monkeypatch.delenv("OWNER_TELEGRAM_ID")
    result = subprocess.run([sys.executable, "-m", "sunny_bot", "--check-config"], capture_output=True, text=True)
    assert result.returncode == 2
    assert "OWNER_TELEGRAM_ID" in result.stderr
    assert FAKE_TOKEN not in result.stdout + result.stderr
