import json
import sqlite3
from pathlib import Path
from typing import Iterable

from models import NotificationLog, WatchItem

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "price_monitor.db"
SCHEMA_PATH = DATA_DIR / "schema.sql"
LEGACY_JSON_PATH = DATA_DIR / "watchlist.json"


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _run_schema(conn: sqlite3.Connection) -> None:
    if not SCHEMA_PATH.exists():
        raise RuntimeError(f"Schema file not found: {SCHEMA_PATH}")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def _serialize_bool(value: bool) -> int:
    return 1 if value else 0


def _deserialize_bool(value: int) -> bool:
    return value == 1


def _insert_watch_item(conn: sqlite3.Connection, item: WatchItem) -> None:
    conn.execute(
        """
        INSERT INTO watch_items (
          item_code, keyword, title, url, image, current_price,
          notify, drop_rate_threshold, notify_to, last_checked, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(item_code) DO UPDATE SET
          keyword=excluded.keyword,
          title=excluded.title,
          url=excluded.url,
          image=excluded.image,
          current_price=excluded.current_price,
          notify=excluded.notify,
          drop_rate_threshold=excluded.drop_rate_threshold,
          notify_to=excluded.notify_to,
          last_checked=excluded.last_checked,
          updated_at=datetime('now')
        """,
        (
            item.item_code,
            item.keyword,
            item.title,
            item.url,
            item.image,
            item.current_price,
            _serialize_bool(item.notify),
            item.drop_rate_threshold,
            item.notify_to,
            item.last_checked.isoformat() if item.last_checked else None,
        ),
    )


def _replace_price_history(
    conn: sqlite3.Connection, item_code: str, history: Iterable
) -> None:
    conn.execute("DELETE FROM price_history WHERE item_code = ?", (item_code,))
    conn.executemany(
        """
        INSERT OR IGNORE INTO price_history (item_code, checked_at, price)
        VALUES (?, ?, ?)
        """,
        [(item_code, point.timestamp.isoformat(), point.price) for point in history],
    )


def _hydrate_watch_item(conn: sqlite3.Connection, row: sqlite3.Row) -> WatchItem:
    history_rows = conn.execute(
        """
        SELECT checked_at, price
        FROM price_history
        WHERE item_code = ?
        ORDER BY checked_at ASC
        """,
        (row["item_code"],),
    ).fetchall()

    payload = {
        "item_code": row["item_code"],
        "keyword": row["keyword"],
        "title": row["title"],
        "url": row["url"],
        "image": row["image"],
        "current_price": row["current_price"],
        "notify": _deserialize_bool(row["notify"]),
        "drop_rate_threshold": row["drop_rate_threshold"],
        "notify_to": row["notify_to"],
        "last_checked": row["last_checked"],
        "price_history": [
            {"timestamp": h["checked_at"], "price": h["price"]} for h in history_rows
        ],
    }
    return WatchItem.model_validate(payload)


def _migrate_legacy_json(conn: sqlite3.Connection) -> None:
    if not LEGACY_JSON_PATH.exists():
        return

    count = conn.execute("SELECT COUNT(*) AS count FROM watch_items").fetchone()[
        "count"
    ]
    if count > 0:
        return

    try:
        raw = json.loads(LEGACY_JSON_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    for entry in raw:
        item = WatchItem.model_validate(entry)
        _insert_watch_item(conn, item)
        _replace_price_history(conn, item.item_code, item.price_history)


def load_watch_items() -> list[WatchItem]:
    with _connect() as conn:
        _run_schema(conn)
        _migrate_legacy_json(conn)
        rows = conn.execute(
            "SELECT * FROM watch_items ORDER BY updated_at DESC"
        ).fetchall()
        return [_hydrate_watch_item(conn, row) for row in rows]


def save_watch_items(items: list[WatchItem]) -> None:
    with _connect() as conn:
        _run_schema(conn)
        for item in items:
            _insert_watch_item(conn, item)
            _replace_price_history(conn, item.item_code, item.price_history)
        conn.commit()


def upsert_watch_item(item: WatchItem) -> WatchItem:
    with _connect() as conn:
        _run_schema(conn)
        _insert_watch_item(conn, item)
        _replace_price_history(conn, item.item_code, item.price_history)
        conn.commit()
    return item


def get_watch_item(item_code: str) -> WatchItem | None:
    with _connect() as conn:
        _run_schema(conn)
        row = conn.execute(
            "SELECT * FROM watch_items WHERE item_code = ?", (item_code,)
        ).fetchone()
        if row is None:
            return None
        return _hydrate_watch_item(conn, row)


def log_notification(
    *,
    item_code: str,
    recipient: str | None,
    previous_price: int,
    current_price: int,
    drop_rate: float,
    success: bool,
    message: str,
) -> None:
    with _connect() as conn:
        _run_schema(conn)
        conn.execute(
            """
            INSERT INTO notification_logs (
              item_code, notified_at, recipient, previous_price,
              current_price, drop_rate, success, message
            )
                        VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?)
            """,
            (
                item_code,
                recipient,
                previous_price,
                current_price,
                drop_rate,
                _serialize_bool(success),
                message,
            ),
        )
        conn.commit()


def delete_watch_item(item_code: str) -> bool:
    with _connect() as conn:
        _run_schema(conn)
        result = conn.execute(
            "DELETE FROM watch_items WHERE item_code = ?", (item_code,)
        )
        conn.commit()
        return result.rowcount > 0


def get_notification_logs(
    *, item_code: str | None = None, limit: int = 100
) -> list[NotificationLog]:
    with _connect() as conn:
        _run_schema(conn)

        sql = """
            SELECT
              id,
              item_code,
              notified_at,
              recipient,
              previous_price,
              current_price,
              drop_rate,
              success,
              message
            FROM notification_logs
        """
        params: tuple = ()

        if item_code:
            sql += " WHERE item_code = ?"
            params = (item_code,)

        sql += " ORDER BY notified_at DESC, id DESC LIMIT ?"
        params = (*params, max(1, min(limit, 500)))

        rows = conn.execute(sql, params).fetchall()

        return [
            NotificationLog.model_validate(
                {
                    "id": row["id"],
                    "item_code": row["item_code"],
                    "notified_at": row["notified_at"],
                    "recipient": row["recipient"],
                    "previous_price": row["previous_price"],
                    "current_price": row["current_price"],
                    "drop_rate": row["drop_rate"],
                    "success": _deserialize_bool(row["success"]),
                    "message": row["message"],
                }
            )
            for row in rows
        ]
