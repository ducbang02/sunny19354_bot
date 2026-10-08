# Personal Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task. Steps use checkbox syntax.

**Goal:** Implement the small personal Telegram assistant defined in PROJECT.md.
**Architecture:** A Python package with config, SQLite storage and Telegram command/job handlers. SQLite is authoritative for pending reminders; JobQueue is rebuilt at startup. No external server or arbitrary PC commands.
**Tech Stack:** Python 3.13, python-telegram-bot 22.8 with JobQueue, sqlite3, python-dotenv, tzdata, pytest.
**Spec:** PROJECT.md (at repository root).

## Global Constraints
- Docs for roadmap/tasks live in docs/; AGENTS.md and SETUP.md remain at root.
- Only OWNER_TELEGRAM_ID in private chat may execute commands; ignore edited updates to avoid duplicate mutations.
- Token and local data never enter source, Git or logs. Default timezone Asia/Bangkok; due times stored UTC.
- Complete independent work autonomously; live Telegram validation requires a local .env, never a token in chat.
- Work in current user workspace on a feature branch after bootstrap. Native inline implementation; one independent final review.

## Review Focus
- Invalid/missing configuration fails before creating the DB or contacting Telegram (Task 1).
- Empty/oversized/multiline Unicode text, invalid IDs, pagination and SQL-like text remain safe (Tasks 2/3).
- Unauthorized, group, edited and unknown commands never mutate personal data (Task 3).
- Restart, overdue reminder, Telegram network/rate-limit failures and cancellation preserve correct pending state (Task 3).
- DST gaps/ambiguities are rejected; long messages fit Telegram UTF-16 limits; errors never include user data/token (Task 3).

### Task 1: Configuration and CLI
**Files:** sunny_bot/config.py, sunny_bot/__main__.py, tests/test_config.py, pyproject.toml.
**Interfaces:** load_config(env_file: Path | None) -> Config; Config(token: str, owner_id: int, timezone: ZoneInfo, database_path: Path). CLI main() -> int.
- [x] Write config tests: missing token/owner, malformed token, nonpositive/nonnumeric owner, invalid timezone, blank DB, env override, project-relative DB, token-free repr/errors.
- [x] Run python -m pytest tests/test_config.py -q. Expected: missing behavior fails.
- [x] Implement validation and dotenv loading without overriding process env; main catches startup errors and prints only safe messages. Support --check-config with no network/DB access.
- [x] Run config tests and CLI --check-config with missing .env. Expected: tests pass; CLI exits 2 with safe missing-config message.
- [x] Commit foundation checkpoint after verification.

### Task 2: Persistent notes and reminders
**Files:** sunny_bot/storage.py, tests/test_storage.py.
**Interfaces:** Storage(path: Path); add_note(text)->int; list_notes(page=1)->list[sqlite3.Row]; delete_note(id)->bool; add_reminder(text,due_at: datetime)->int; pending_reminders(page: int | None=None)->list[sqlite3.Row]; get_pending_reminder(id)->Row|None; finish_reminder(id,status)->bool.
- [x] Write SQLite tests for CRUD, parameterized SQL-like content, 20-item pagination, persistence across instances, cancel/sent exclusion, duplicate finalization and UTC timestamp.
- [x] Run python -m pytest tests/test_storage.py -q. Expected: missing behavior fails.
- [x] Implement direct parameterized SQLite operations, connection lifecycle per operation and atomic conditional state transitions; validate storage status.
- [x] Run whole suite. Expected: pass.
- [x] Commit persistence checkpoint.

### Task 3: Telegram commands and scheduling
**Files:** sunny_bot/bot.py, tests/test_bot.py, tests/fake_telegram.py, README.md, docs/TASKS.md.
**Interfaces:** build_application(config: Config, request: BaseRequest | None=None)->Application; restore_reminders(application)->None; deliver_reminder(context)->None; parse_reminder(text,tz,now)->tuple[datetime,str].
- [x] Write real Application/process_update tests with an in-memory BaseRequest transport and actual temp SQLite. Cover all commands, permissions, unknown commands, edited updates, validation and multiline text, pagination, private-only delivery, restart/overdue/cancel, retry on API failure/rate limit, UTF-16-safe messages and sanitized errors. Test the real JobQueue executes due callbacks.
- [x] Run python -m pytest tests/test_bot.py -q. Expected: missing behavior fails.
- [x] Implement command handlers with explicit authorization checks; preserve body text. Limit body to 1000 UTF-16 units, full list content in messages of at most 4000 UTF-16 units, 20 entries/page. Validate positive integer IDs/pages, strict dates, future time and DST validity.
- [x] Persist before scheduling, query pending state at delivery and mark sent only after success. Serialize delivery/cancellation with an asyncio lock. Retry Telegram/SQLite failures with delay >=60s or RetryAfter; remember successful sends in memory until SQLite commits to avoid in-process duplicate delivery. Restore all pending reminders at post_init including overdue; retain missed in-session jobs with misfire_grace_time=None.
- [x] Run whole suite, compile, pip check, config CLI failure and local fake Telegram flow. Expected: pass; missing real credentials remain explicitly pending.
- [x] Update docs and actual commands; secret scan before commit; independent final review and address important findings with regression tests.

## Execution record
Native execution authorized by user's request to install missing dependencies and continue. Existing PROJECT.md supplies scope; no extra product approval needed. Initial baseline: pip check and import/JobQueue smoke passed; no pre-existing application tests. Windows-specific adaptation: use Python/PowerShell and docs/TASKS.md as the durable ledger instead of Bash-only skill helpers. No shared worktree to protect; create a feature branch after initial commit.

Final verification: 61 tests passed; compileall and pip check passed. Missing-token CLI exit 2 verified directly. Gitleaks scanned staged data with no leaks. Implementation committed and pushed on feat/personal-assistant; live Telegram checks remain pending local .env as tracked in docs/TASKS.md.
