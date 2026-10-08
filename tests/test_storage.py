from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from sunny_bot.storage import Storage


def test_notes_crud_and_persistence(tmp_path):
    path = tmp_path / "nested/bot.sqlite3"
    store = Storage(path)
    text = "Mua sữa\n'; DROP TABLE notes; -- 😀"
    note_id = store.add_note(text)
    reopened = Storage(path)
    assert [(r["id"], r["text"]) for r in reopened.list_notes()] == [(note_id, text)]
    assert reopened.delete_note(note_id)
    assert not reopened.delete_note(note_id)
    assert reopened.list_notes() == []


def test_notes_pagination_is_stable_and_bounded(tmp_path):
    store = Storage(tmp_path / "bot.db")
    for n in range(23):
        store.add_note(str(n))
    assert [r["text"] for r in store.list_notes(1)] == [str(n) for n in range(22, 2, -1)]
    assert [r["text"] for r in store.list_notes(2)] == ["2", "1", "0"]
    assert store.list_notes(3) == []


def test_reminders_store_utc_and_survive_restart(tmp_path):
    path = tmp_path / "bot.db"
    store = Storage(path)
    due = datetime(2030, 1, 1, 10, 30, tzinfo=ZoneInfo("Asia/Bangkok"))
    rid = store.add_reminder("Test reminder", due)
    row = Storage(path).get_pending_reminder(rid)
    assert row["due_at"] == datetime(2030, 1, 1, 3, 30, tzinfo=timezone.utc).timestamp()
    assert row["text"] == "Test reminder"


@pytest.mark.parametrize("status", ["sent", "cancelled"])
def test_finalization_is_conditional_and_excludes_pending(tmp_path, status):
    store = Storage(tmp_path / "bot.db")
    rid = store.add_reminder("content", datetime(2030, 1, 1, tzinfo=timezone.utc))
    assert store.finish_reminder(rid, status)
    assert not store.finish_reminder(rid, status)
    assert store.get_pending_reminder(rid) is None
    assert store.pending_reminders() == []


def test_invalid_status_does_not_mutate_reminder(tmp_path):
    store = Storage(tmp_path / "bot.db")
    rid = store.add_reminder("content", datetime(2030, 1, 1, tzinfo=timezone.utc))
    with pytest.raises(ValueError):
        store.finish_reminder(rid, "unknown")
    assert store.get_pending_reminder(rid) is not None


def test_pending_reminders_order_and_pagination(tmp_path):
    store = Storage(tmp_path / "bot.db")
    for n in range(22, -1, -1):
        store.add_reminder(str(n), datetime(2030, 1, 1, 0, n, tzinfo=timezone.utc))
    assert len(store.pending_reminders()) == 23
    assert [r["text"] for r in store.pending_reminders(2)] == ["20", "21", "22"]


def test_naive_reminder_time_is_rejected(tmp_path):
    store = Storage(tmp_path / "bot.db")
    with pytest.raises(ValueError):
        store.add_reminder("content", datetime(2030, 1, 1))
    assert store.pending_reminders() == []
