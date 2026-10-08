"""Run with python -m sunny_bot; secrets stay in the local environment."""
import argparse
import logging
import sys

from .config import load_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Sunny 2.0 personal Telegram bot")
    parser.add_argument("--check-config", action="store_true", help="Validate config without network or database access")
    args = parser.parse_args()
    try:
        config = load_config()
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.check_config:
        print("Configuration OK")
        return 0
    # HTTP clients can log URLs containing the token; keep their logs disabled.
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    for name in ("httpx", "httpcore", "telegram", "apscheduler"):
        logging.getLogger(name).setLevel(logging.CRITICAL)
    try:
        from .bot import build_application
        application = build_application(config)
        application.run_polling(allowed_updates=["message"], drop_pending_updates=False)
    except Exception as error:
        logging.getLogger(__name__).error("Bot stopped: %s. Check local config and connectivity.", type(error).__name__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
