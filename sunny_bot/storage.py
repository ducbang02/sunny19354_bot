"""Small SQLite store; the database is the source of reminder state."""
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import sqlite3


class Storage:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    due_at REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'sent', 'cancelled'))
                );
            """)

    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def add_note(self, text: str) -> int:
        with self._connect() as db:
            return db.execute("INSERT INTO notes(text) VALUES (?)", (text,)).lastrowid

    def list_notes(self, page: int = 1) -> list[sqlite3.Row]:
        with self._connect() as db:
            return db.execute("SELECT id, text FROM notes ORDER BY id DESC LIMIT 20 OFFSET ?", ((page - 1) * 20,)).fetchall()

    def delete_note(self, note_id: int) -> bool:
        with self._connect() as db:
            return db.execute("DELETE FROM notes WHERE id = ?", (note_id,)).rowcount == 1

    def add_reminder(self, text: str, due_at: datetime) -> int:
        if due_at.tzinfo is None or due_at.utcoffset() is None:
            raise ValueError("Reminder time must include a timezone.")
        with self._connect() as db:
            return db.execute("INSERT INTO reminders(text, due_at) VALUES (?, ?)", (text, due_at.timestamp())).lastrowid

    def pending_reminders(self, page: int | None = None) -> list[sqlite3.Row]:
        query = "SELECT id, text, due_at FROM reminders WHERE status = 'pending' ORDER BY due_at, id"
        params = ()
        if page is not None:
            query += " LIMIT 20 OFFSET ?"
            params = ((page - 1) * 20,)
        with self._connect() as db:
            return db.execute(query, params).fetchall()

    def get_pending_reminder(self, reminder_id: int) -> sqlite3.Row | None:
        with self._connect() as db:
            return db.execute("SELECT id, text, due_at FROM reminders WHERE id = ? AND status = 'pending'", (reminder_id,)).fetchone()

    def finish_reminder(self, reminder_id: int, status: str) -> bool:
        if status not in ("sent", "cancelled"):
            raise ValueError("Invalid reminder status.")
        with self._connect() as db:
            return db.execute("UPDATE reminders SET status = ? WHERE id = ? AND status = 'pending'", (status, reminder_id)).rowcount == 1
