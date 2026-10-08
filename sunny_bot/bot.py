"""Private Telegram commands and restart-safe one-shot reminders."""
import asyncio
from datetime import datetime, timedelta, timezone
import logging
import re
import sqlite3
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.error import RetryAfter, TelegramError
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.request import BaseRequest

from .config import Config
from .storage import Storage

UTC = timezone.utc
LOG = logging.getLogger(__name__)
HELP = """Sunny 2.0 — trợ lý cá nhân
/note <nội dung> — lưu ghi chú
/notes [trang] — xem ghi chú (20 mục/trang)
/delnote <id> — xóa ghi chú
/remind YYYY-MM-DD HH:MM <nội dung> — nhắc một lần
/reminders [trang] — xem lịch nhắc
/cancel <id> — hủy lịch nhắc
/help — hướng dẫn
Nội dung tối đa 1000 đơn vị UTF-16 (emoji thường tính là 2).
Máy cần bật và bot đang chạy để nhắc đúng giờ."""


def _body(text: str) -> str:
    text = text.strip()
    if not text or len(text.encode("utf-16-le")) // 2 > 1000:
        raise ValueError("Nội dung phải có từ 1 đến 1000 đơn vị UTF-16.")
    return text


def _positive_number(text: str) -> int:
    if not re.fullmatch(r"[0-9]{1,12}", text) or int(text) < 1:
        raise ValueError("ID/trang phải là một số nguyên dương.")
    return int(text)


def parse_reminder(text: str, tz: ZoneInfo, now: datetime) -> tuple[datetime, str]:
    parts = text.split(maxsplit=2)
    if len(parts) != 3 or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}", " ".join(parts[:2])):
        raise ValueError("Dùng: /remind YYYY-MM-DD HH:MM <nội dung>.")
    body = _body(parts[2])
    try:
        local = datetime.strptime(" ".join(parts[:2]), "%Y-%m-%d %H:%M")
        choices = {local.replace(tzinfo=tz, fold=fold).astimezone(UTC) for fold in (0, 1)
                   if local.replace(tzinfo=tz, fold=fold).astimezone(UTC).astimezone(tz).replace(tzinfo=None) == local}
    except (ValueError, OverflowError):
        raise ValueError("Ngày hoặc giờ không hợp lệ.") from None
    if len(choices) != 1:
        raise ValueError("Giờ này không tồn tại hoặc bị trùng do đổi giờ mùa hè; chọn giờ khác.")
    due = choices.pop()
    if due <= now:
        raise ValueError("Thời gian nhắc phải ở tương lai.")
    return due, body


def _authorized(update: object, app: Application) -> bool:
    config = app.bot_data["config"]
    return (isinstance(update, Update) and update.message is not None
            and update.effective_user is not None and update.effective_chat is not None
            and update.effective_user.id == config.owner_id
            and update.effective_chat.type == "private"
            and update.effective_chat.id == config.owner_id)


async def _reply_lines(message, lines: list[str]) -> None:
    chunk = ""
    for line in lines:
        candidate = chunk + ("\n" if chunk else "") + line
        if len(candidate.encode("utf-16-le")) // 2 > 4000:
            await message.reply_text(chunk, parse_mode=None)
            chunk = line
        else:
            chunk = candidate
    if chunk:
        await message.reply_text(chunk, parse_mode=None)


def _remove_jobs(app: Application, reminder_id: int) -> None:
    for job in app.job_queue.get_jobs_by_name(f"reminder:{reminder_id}"):
        job.schedule_removal()


def _schedule(app: Application, reminder_id: int, delay: float) -> None:
    _remove_jobs(app, reminder_id)
    app.job_queue.run_once(deliver_reminder, max(delay, 0), data=reminder_id,
                           name=f"reminder:{reminder_id}", job_kwargs={"misfire_grace_time": None})


async def restore_reminders(application: Application) -> None:
    for row in application.bot_data["storage"].pending_reminders():
        if not application.job_queue.get_jobs_by_name(f"reminder:{row['id']}"):
            _schedule(application, row["id"], row["due_at"] - datetime.now(UTC).timestamp())


async def _post_init(application: Application) -> None:
    await restore_reminders(application)
    await application.bot.set_my_commands([
        ("start", "Bắt đầu"), ("help", "Hướng dẫn"), ("note", "Lưu ghi chú"),
        ("notes", "Xem ghi chú"), ("delnote", "Xóa ghi chú"), ("remind", "Tạo lịch nhắc"),
        ("reminders", "Xem lịch nhắc"), ("cancel", "Hủy lịch nhắc"),
    ])


async def deliver_reminder(context) -> None:
    app = context.application
    store = app.bot_data["storage"]
    reminder_id = context.job.data
    # Remember successful sends until SQLite commits, avoiding duplicates on an in-process retry.
    delivered = app.bot_data["delivered_reminders"]
    # Serializes cancellation and delivery; a cancellation cannot overtake an in-flight send.
    async with app.bot_data["reminder_lock"]:
        try:
            row = store.get_pending_reminder(reminder_id)
            if row is None:
                delivered.discard(reminder_id)
                _remove_jobs(app, reminder_id)
                return
            if reminder_id not in delivered:
                await context.bot.send_message(chat_id=app.bot_data["config"].owner_id,
                                               text=f"Nhắc việc #{reminder_id}:\n{row['text']}", parse_mode=None)
                delivered.add(reminder_id)
            store.finish_reminder(reminder_id, "sent")
        except (TelegramError, sqlite3.Error) as error:
            delay = 60.0
            if isinstance(error, RetryAfter):
                retry = error.retry_after
                delay = max(delay, retry.total_seconds() if isinstance(retry, timedelta) else float(retry))
            LOG.warning("Reminder delivery deferred (%s).", type(error).__name__)
            _schedule(app, reminder_id, delay)
            return
        delivered.discard(reminder_id)
        _remove_jobs(app, reminder_id)


async def _command(update: Update, context) -> None:
    app = context.application
    if not _authorized(update, app):
        return
    message = update.message
    store = app.bot_data["storage"]
    config = app.bot_data["config"]
    parts = message.text.split(maxsplit=1)
    command = parts[0].split("@", 1)[0].lower()
    body = parts[1] if len(parts) == 2 else ""
    try:
        if command in ("/start", "/help"):
            await message.reply_text(HELP + f"\nMúi giờ: {config.timezone}", parse_mode=None)
        elif command == "/note":
            note_id = store.add_note(_body(body))
            await message.reply_text(f"Đã lưu ghi chú #{note_id}.")
        elif command == "/delnote":
            note_id = _positive_number(body.strip())
            deleted = store.delete_note(note_id)
            await message.reply_text(f"Đã xóa ghi chú #{note_id}." if deleted else "Không tìm thấy ghi chú.")
        elif command in ("/notes", "/reminders"):
            page = _positive_number(body.strip()) if body.strip() else 1
            if command == "/notes":
                rows = store.list_notes(page)
                lines = [f"#{r['id']}: {r['text']}" for r in rows]
            else:
                rows = store.pending_reminders(page)
                lines = [f"#{r['id']} — {datetime.fromtimestamp(r['due_at'], UTC).astimezone(config.timezone):%Y-%m-%d %H:%M}\n{r['text']}" for r in rows]
            if not rows:
                await message.reply_text("Chưa có mục nào ở trang này.")
            else:
                await _reply_lines(message, [f"Trang {page} (20 mục/trang)", *lines,
                                             f"Trang tiếp: {command} {page + 1}"])
        elif command == "/remind":
            due, text = parse_reminder(body, config.timezone, datetime.now(UTC))
            reminder_id = store.add_reminder(text, due)
            _schedule(app, reminder_id, due.timestamp() - datetime.now(UTC).timestamp())
            local = due.astimezone(config.timezone)
            await message.reply_text(f"Đã tạo nhắc việc #{reminder_id}: {local:%Y-%m-%d %H:%M} ({config.timezone}).")
        elif command == "/cancel":
            reminder_id = _positive_number(body.strip())
            async with app.bot_data["reminder_lock"]:
                cancelled = store.finish_reminder(reminder_id, "sent" if reminder_id in app.bot_data["delivered_reminders"] else "cancelled")
                if reminder_id in app.bot_data["delivered_reminders"]:
                    cancelled = False
                app.bot_data["delivered_reminders"].discard(reminder_id)
                _remove_jobs(app, reminder_id)
            await message.reply_text(f"Đã hủy nhắc việc #{reminder_id}." if cancelled else "Không tìm thấy lịch nhắc đang chờ.")
    except ValueError as error:
        await message.reply_text(str(error), parse_mode=None)


async def _unknown(update: Update, context) -> None:
    if _authorized(update, context.application):
        await update.message.reply_text("Lệnh chưa hỗ trợ. Gửi /help để xem hướng dẫn.")


async def _on_error(update: object, context) -> None:
    LOG.error("Bot operation failed (%s).", type(context.error).__name__)
    if _authorized(update, context.application):
        try:
            await update.message.reply_text("Có lỗi khi xử lý. Dùng /notes hoặc /reminders kiểm tra kết quả trước khi thử lại.")
        except TelegramError:
            LOG.warning("Could not send error reply.")


def build_application(config: Config, request: BaseRequest | None = None) -> Application:
    builder = Application.builder().token(config.token).concurrent_updates(False).post_init(_post_init)
    if request is not None:
        builder = builder.request(request)
    app = builder.build()
    if app.job_queue is None:
        raise RuntimeError("Install python-telegram-bot with the job-queue extra.")
    app.bot_data.update(config=config, storage=Storage(config.database_path), reminder_lock=asyncio.Lock(), delivered_reminders=set())
    trusted = filters.UpdateType.MESSAGE & filters.ChatType.PRIVATE & filters.User(config.owner_id)
    app.add_handler(CommandHandler(["start", "help", "note", "notes", "delnote", "remind", "reminders", "cancel"], _command, filters=trusted))
    app.add_handler(MessageHandler(trusted & filters.COMMAND, _unknown))
    app.add_error_handler(_on_error)
    return app
