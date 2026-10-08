import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest
from telegram import Update

from sunny_bot.bot import build_application, deliver_reminder, parse_reminder, restore_reminders
from sunny_bot.config import Config
from sunny_bot.storage import Storage
from tests.fake_telegram import FakeTelegram

UTC = timezone.utc
TZ = ZoneInfo("Asia/Bangkok")


@asynccontextmanager
async def session(tmp_path, start=False):
    request = FakeTelegram()
    config = Config("123456:" + "a" * 35, 42, TZ, tmp_path / "bot.db")
    app = build_application(config, request=request)
    async with app:
        await app.post_init(app)
        if start:
            await app.start()
        try:
            yield app, request
        finally:
            if app.running:
                await app.stop()


async def command(app, text, user=42, chat=42, kind="private", edited=False):
    name = text.split()[0]
    data = {"message_id": 1, "date": 1900000000, "from": {"id": user, "is_bot": False, "first_name": "Owner"},
            "chat": {"id": chat, "type": kind}, "text": text,
            "entities": [{"type": "bot_command", "offset": 0, "length": len(name)}]}
    key = "edited_message" if edited else "message"
    await app.process_update(Update.de_json({"update_id": 1, key: data}, app.bot))


def test_private_note_crud_preserves_full_text_and_survives_restart(tmp_path):
    async def flow():
        async with session(tmp_path) as (app, api):
            await command(app, "/note@sunny19354_bot Mua sữa\nDòng hai <b>literal</b> 😀")
            assert "#1" in api.sent[-1]["text"]
            await command(app, "/notes")
            assert "Mua sữa\nDòng hai <b>literal</b> 😀" in api.sent[-1]["text"]
            assert not api.sent[-1].get("parse_mode")
        async with session(tmp_path) as (app, api):
            await command(app, "/notes")
            assert "Dòng hai" in api.sent[-1]["text"]
            await command(app, "/delnote 1")
            await command(app, "/notes")
            assert app.bot_data["storage"].list_notes() == []
            assert "Chưa có" in api.sent[-1]["text"]
    asyncio.run(flow())


@pytest.mark.parametrize("kwargs", [{"user": 99, "chat": 99}, {"kind": "group", "chat": -42},
                                      {"edited": True}, {"user": 42, "chat": 99}])
def test_untrusted_updates_cannot_read_or_mutate(tmp_path, kwargs):
    async def flow():
        async with session(tmp_path) as (app, api):
            for text in ["/note secret", "/notes", "/delnote 1", "/remind 2035-01-01 10:00 secret", "/reminders", "/cancel 1", "/help", "/unknown"]:
                await command(app, text, **kwargs)
            assert api.sent == []
            assert app.bot_data["storage"].list_notes() == []
            assert app.bot_data["storage"].pending_reminders() == []
    asyncio.run(flow())


@pytest.mark.parametrize("text", ["/note", "/note " + "a" * 1001, "/note " + "😀" * 501,
    "/delnote -1", "/delnote 0", "/delnote abc", "/delnote 1 extra", "/delnote " + "9" * 100,
    "/notes 0", "/notes abc", "/notes 1 extra", "/reminders -1", "/cancel xyz",
    "/remind 2035-02-30 10:00 x", "/remind 2000-01-01 10:00 x", "/remind 2035-01-01 10:00",
    "/remind 2035-01-01 10:00 " + "a" * 1001, "/remind 2035-1-1 1:00 x"])
def test_invalid_commands_reply_without_mutation(tmp_path, text):
    async def flow():
        async with session(tmp_path) as (app, api):
            await command(app, text)
            assert api.sent
            assert app.bot_data["storage"].list_notes() == []
            assert app.bot_data["storage"].pending_reminders() == []
    asyncio.run(flow())


def test_help_and_unknown_commands(tmp_path):
    async def flow():
        async with session(tmp_path) as (app, api):
            for text in ["/start", "/help", "/unknown"]:
                await command(app, text)
                assert "/note" in api.sent[-1]["text"] or "/help" in api.sent[-1]["text"]
    asyncio.run(flow())


def test_note_lists_paginate_and_fit_telegram_without_losing_content(tmp_path):
    async def flow():
        async with session(tmp_path) as (app, api):
            for n in range(21):
                app.bot_data["storage"].add_note(str(n) + "😀" * 490)
            await command(app, "/notes")
            combined = "\n".join(p["text"] for p in api.sent)
            assert "20" + "😀" * 490 in combined
            assert "1" + "😀" * 490 in combined
            assert "#1: 0" + "😀" * 490 not in combined
            assert all(len(p["text"].encode("utf-16-le")) // 2 <= 4096 for p in api.sent)
            await command(app, "/notes 2")
            assert "0" + "😀" * 490 in api.sent[-1]["text"]
    asyncio.run(flow())


def test_reminder_create_list_cancel_and_missing_id(tmp_path):
    async def flow():
        async with session(tmp_path) as (app, api):
            await command(app, "/remind 2035-01-01 10:30 Họp\nDòng hai")
            row = app.bot_data["storage"].pending_reminders()[0]
            assert row["text"] == "Họp\nDòng hai"
            assert row["due_at"] == datetime(2035, 1, 1, 3, 30, tzinfo=UTC).timestamp()
            assert len(app.job_queue.get_jobs_by_name("reminder:1")) == 1
            await command(app, "/reminders")
            assert "2035-01-01 10:30" in api.sent[-1]["text"]
            await command(app, "/cancel 1")
            assert app.bot_data["storage"].pending_reminders() == []
            assert not app.job_queue.get_jobs_by_name("reminder:1")
            await command(app, "/cancel 1")
            assert "Không tìm thấy" in api.sent[-1]["text"]
            await command(app, "/delnote 99")
            assert "Không tìm thấy" in api.sent[-1]["text"]
    asyncio.run(flow())


def test_future_and_overdue_reminders_restore_and_real_jobqueue_delivers(tmp_path):
    store = Storage(tmp_path / "bot.db")
    overdue = store.add_reminder("Overdue", datetime.now(UTC) - timedelta(minutes=1))
    future = store.add_reminder("Future", datetime(2035, 1, 1, tzinfo=UTC))
    async def flow():
        async with session(tmp_path, start=True) as (app, api):
            async def wait_sent():
                while not api.sent:
                    await asyncio.sleep(0.01)
            await asyncio.wait_for(wait_sent(), timeout=3)
            assert api.sent[-1]["chat_id"] == 42
            assert "Overdue" in api.sent[-1]["text"]
            assert store.get_pending_reminder(overdue) is None
            assert store.get_pending_reminder(future) is not None
            assert len(app.job_queue.get_jobs_by_name("reminder:2")) == 1
            await restore_reminders(app)
            assert len(app.job_queue.get_jobs_by_name("reminder:2")) == 1
    asyncio.run(flow())


@pytest.mark.parametrize("failure", [(500, "temporary outage", {}), (429, "Too Many Requests", {"parameters": {"retry_after": 90}})])
def test_delivery_failure_keeps_pending_and_retries_then_sends_once(tmp_path, failure, monkeypatch):
    monkeypatch.setenv("PTB_TIMEDELTA", "1")
    async def flow():
        async with session(tmp_path, start=True) as (app, api):
            store = app.bot_data["storage"]
            rid = store.add_reminder("Retry me", datetime.now(UTC) + timedelta(hours=1))
            api.failure = failure
            context = SimpleNamespace(application=app, bot=app.bot, job=SimpleNamespace(data=rid))
            await deliver_reminder(context)
            assert store.get_pending_reminder(rid) is not None
            jobs = app.job_queue.get_jobs_by_name("reminder:1")
            assert len(jobs) == 1
            assert (jobs[0].next_t - datetime.now(UTC)).total_seconds() >= (85 if failure[0] == 429 else 55)
            await deliver_reminder(context)
            await deliver_reminder(context)
            assert store.get_pending_reminder(rid) is None
            assert len(api.sent) == 1
    asyncio.run(flow())


def test_cancelled_reminder_never_sends_even_if_stale_job_runs(tmp_path):
    async def flow():
        async with session(tmp_path) as (app, api):
            rid = app.bot_data["storage"].add_reminder("Never send", datetime(2035, 1, 1, tzinfo=UTC))
            await command(app, "/cancel 1")
            before = len(api.sent)
            await deliver_reminder(SimpleNamespace(application=app, bot=app.bot, job=SimpleNamespace(data=rid)))
            assert len(api.sent) == before
    asyncio.run(flow())


@pytest.mark.parametrize("local", ["2030-03-10 02:30 gap", "2030-11-03 01:30 ambiguous"])
def test_dst_gap_and_ambiguity_rejected(local):
    with pytest.raises(ValueError):
        parse_reminder(local, ZoneInfo("America/New_York"), datetime(2029, 1, 1, tzinfo=UTC))


def test_reminder_parser_converts_to_utc_and_preserves_body():
    due, body = parse_reminder("2035-01-01 10:30 content\nsecond", TZ, datetime(2030, 1, 1, tzinfo=UTC))
    assert due == datetime(2035, 1, 1, 3, 30, tzinfo=UTC)
    assert body == "content\nsecond"


def test_database_errors_have_safe_reply_and_logs(tmp_path, monkeypatch, caplog):
    import sqlite3
    async def flow():
        async with session(tmp_path) as (app, api):
            def broken(text):
                raise sqlite3.OperationalError("private-note-and-token-secret")
            monkeypatch.setattr(app.bot_data["storage"], "add_note", broken)
            await command(app, "/note sensitive-content")
            assert api.sent
            assert "private-note-and-token-secret" not in caplog.text
            assert "sensitive-content" not in caplog.text
            assert "private-note-and-token-secret" not in api.sent[-1]["text"]
    asyncio.run(flow())


@pytest.mark.parametrize("stage", ["read", "finish"])
def test_database_failure_retries_without_resending_after_success(tmp_path, monkeypatch, caplog, stage):
    import sqlite3
    async def flow():
        async with session(tmp_path, start=True) as (app, api):
            store = app.bot_data["storage"]
            rid = store.add_reminder("Retry database", datetime.now(UTC) + timedelta(hours=1))
            method = "get_pending_reminder" if stage == "read" else "finish_reminder"
            original = getattr(store, method)
            calls = 0
            def fail_once(*args):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise sqlite3.OperationalError("private-database-error")
                return original(*args)
            monkeypatch.setattr(store, method, fail_once)
            context = SimpleNamespace(application=app, bot=app.bot, job=SimpleNamespace(data=rid))
            await deliver_reminder(context)
            assert store.get_pending_reminder(rid) is not None
            assert len(api.sent) == (0 if stage == "read" else 1)
            jobs = app.job_queue.get_jobs_by_name(f"reminder:{rid}")
            assert len(jobs) == 1
            assert (jobs[0].next_t - datetime.now(UTC)).total_seconds() >= 55
            await deliver_reminder(context)
            assert store.get_pending_reminder(rid) is None
            assert len(api.sent) == 1
            assert not app.job_queue.get_jobs_by_name(f"reminder:{rid}")
            assert "private-database-error" not in caplog.text
    asyncio.run(flow())


def test_cancel_waits_for_inflight_delivery_and_reports_already_sent(tmp_path, monkeypatch):
    async def flow():
        async with session(tmp_path) as (app, api):
            store = app.bot_data["storage"]
            rid = store.add_reminder("Already sending", datetime(2035, 1, 1, tzinfo=UTC))
            entered, release = asyncio.Event(), asyncio.Event()
            original = api.do_request
            async def blocked(url, method, *args, **kwargs):
                if url.endswith("/sendMessage") and not entered.is_set():
                    entered.set()
                    await release.wait()
                return await original(url, method, *args, **kwargs)
            monkeypatch.setattr(api, "do_request", blocked)
            delivery = asyncio.create_task(deliver_reminder(SimpleNamespace(application=app, bot=app.bot, job=SimpleNamespace(data=rid))))
            await asyncio.wait_for(entered.wait(), timeout=3)
            cancellation = asyncio.create_task(command(app, f"/cancel {rid}"))
            await asyncio.sleep(0)
            assert not cancellation.done()
            release.set()
            await asyncio.wait_for(asyncio.gather(delivery, cancellation), timeout=3)
            assert store.get_pending_reminder(rid) is None
            assert len(api.sent) == 2
            assert "Nhắc việc" in api.sent[0]["text"]
            assert "Không tìm thấy" in api.sent[1]["text"]
    asyncio.run(flow())


def test_cancel_after_send_with_failed_commit_does_not_claim_cancelled(tmp_path, monkeypatch):
    import sqlite3
    async def flow():
        async with session(tmp_path) as (app, api):
            store = app.bot_data["storage"]
            rid = store.add_reminder("Already delivered", datetime(2035, 1, 1, tzinfo=UTC))
            original = store.finish_reminder
            def fail(*args):
                raise sqlite3.OperationalError("temporary lock")
            monkeypatch.setattr(store, "finish_reminder", fail)
            context = SimpleNamespace(application=app, bot=app.bot, job=SimpleNamespace(data=rid))
            await deliver_reminder(context)
            monkeypatch.setattr(store, "finish_reminder", original)
            await command(app, f"/cancel {rid}")
            assert "Không tìm thấy" in api.sent[-1]["text"]
            assert store.get_pending_reminder(rid) is None
            assert not app.bot_data["delivered_reminders"]
            assert not app.job_queue.get_jobs_by_name(f"reminder:{rid}")
            await deliver_reminder(context)
            assert len(api.sent) == 2
    asyncio.run(flow())
