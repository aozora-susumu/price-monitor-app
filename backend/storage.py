import json
from datetime import UTC, datetime
from pathlib import Path

from models import NotificationLog, WatchItem
from supabase_client import get_supabase_client

LEGACY_JSON_PATH = Path(__file__).parent / "data" / "watchlist.json"


def _as_bool(value: bool | int | None, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value == 1


def _watch_item_row(item: WatchItem) -> dict:
    return {
        "item_code": item.item_code,
        "keyword": item.keyword,
        "title": item.title,
        "url": item.url,
        "image": item.image,
        "current_price": item.current_price,
        "notify": item.notify,
        "drop_rate_threshold": item.drop_rate_threshold,
        "notify_to": item.notify_to,
        "last_checked": item.last_checked.isoformat() if item.last_checked else None,
        "updated_at": datetime.now(UTC).isoformat(),
    }


def _replace_price_history(item_code: str, item: WatchItem) -> None:
    client = get_supabase_client()
    client.table("price_history").delete().eq("item_code", item_code).execute()
    rows = [
        {
            "item_code": item_code,
            "checked_at": point.timestamp.isoformat(),
            "price": point.price,
        }
        for point in item.price_history
    ]
    if rows:
        client.table("price_history").insert(rows).execute()


def _hydrate_watch_items(items_data: list[dict]) -> list[WatchItem]:
    if not items_data:
        return []

    client = get_supabase_client()
    item_codes = [row["item_code"] for row in items_data]
    history_res = (
        client.table("price_history")
        .select("item_code, checked_at, price")
        .in_("item_code", item_codes)
        .order("checked_at")
        .execute()
    )

    history_map: dict[str, list[dict]] = {}
    for row in history_res.data or []:
        history_map.setdefault(row["item_code"], []).append(row)

    hydrated: list[WatchItem] = []
    for row in items_data:
        payload = {
            "item_code": row["item_code"],
            "keyword": row["keyword"],
            "title": row["title"],
            "url": row["url"],
            "image": row.get("image"),
            "current_price": row["current_price"],
            "notify": _as_bool(row.get("notify"), default=True),
            "drop_rate_threshold": row.get("drop_rate_threshold", 0.05),
            "notify_to": row.get("notify_to"),
            "last_checked": row.get("last_checked"),
            "updated_at": row.get("updated_at"),
            "price_history": [
                {"timestamp": h["checked_at"], "price": h["price"]}
                for h in history_map.get(row["item_code"], [])
            ],
        }
        hydrated.append(WatchItem.model_validate(payload))

    return hydrated


def _migrate_legacy_json() -> None:
    if not LEGACY_JSON_PATH.exists():
        return

    client = get_supabase_client()
    count_res = (
        client.table("watch_items")
        .select("item_code", count="exact")
        .limit(1)
        .execute()
    )
    if (count_res.count or 0) > 0:
        return

    try:
        raw = json.loads(LEGACY_JSON_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    for entry in raw:
        item = WatchItem.model_validate(entry)
        client.table("watch_items").upsert(
            _watch_item_row(item), on_conflict="item_code"
        ).execute()
        _replace_price_history(item.item_code, item)


def load_watch_items() -> list[WatchItem]:
    _migrate_legacy_json()
    client = get_supabase_client()
    result = (
        client.table("watch_items").select("*").order("updated_at", desc=True).execute()
    )
    return _hydrate_watch_items(result.data or [])


def save_watch_items(items: list[WatchItem]) -> None:
    client = get_supabase_client()
    for item in items:
        client.table("watch_items").upsert(
            _watch_item_row(item), on_conflict="item_code"
        ).execute()
        _replace_price_history(item.item_code, item)


def upsert_watch_item(item: WatchItem) -> WatchItem:
    client = get_supabase_client()
    client.table("watch_items").upsert(
        _watch_item_row(item), on_conflict="item_code"
    ).execute()
    _replace_price_history(item.item_code, item)
    return item


def get_watch_item(item_code: str) -> WatchItem | None:
    client = get_supabase_client()
    result = (
        client.table("watch_items")
        .select("*")
        .eq("item_code", item_code)
        .limit(1)
        .execute()
    )
    rows = result.data or []
    if not rows:
        return None
    return _hydrate_watch_items(rows)[0]


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
    client = get_supabase_client()
    client.table("notification_logs").insert(
        {
            "item_code": item_code,
            "notified_at": datetime.now(UTC).isoformat(),
            "recipient": recipient,
            "previous_price": previous_price,
            "current_price": current_price,
            "drop_rate": drop_rate,
            "success": success,
            "message": message,
        }
    ).execute()


def apply_monitor_update(
    *,
    item: WatchItem,
    title: str,
    url: str,
    image: str | None,
    current_price: int,
    checked_at: datetime,
    history_checked_at: datetime,
    should_log: bool,
    recipient: str | None,
    previous_price: int,
    drop_rate: float,
    notify_success: bool,
    notify_message: str,
) -> bool:
    client = get_supabase_client()

    result = client.rpc(
        "apply_monitor_check",
        {
            "p_item_code": item.item_code,
            "p_expected_updated_at": (
                item.updated_at.isoformat() if item.updated_at else None
            ),
            "p_title": title,
            "p_url": url,
            "p_image": image,
            "p_current_price": current_price,
            "p_last_checked": checked_at.isoformat(),
            "p_history_checked_at": history_checked_at.isoformat(),
            "p_should_log": should_log,
            "p_recipient": recipient,
            "p_previous_price": previous_price,
            "p_drop_rate": drop_rate,
            "p_notify_success": notify_success,
            "p_notify_message": notify_message,
        },
    ).execute()
    data = result.data
    if isinstance(data, bool):
        return data
    if isinstance(data, list) and data:
        row = data[0]
        if isinstance(row, bool):
            return row
        if isinstance(row, dict):
            if "apply_monitor_check" in row:
                return bool(row["apply_monitor_check"])
            if "result" in row:
                return bool(row["result"])
    return False


def delete_watch_item(item_code: str) -> bool:
    client = get_supabase_client()
    result = client.table("watch_items").delete().eq("item_code", item_code).execute()
    return len(result.data or []) > 0


def get_notification_logs(
    *, item_code: str | None = None, limit: int = 100
) -> list[NotificationLog]:
    client = get_supabase_client()
    normalized_limit = max(1, min(limit, 500))

    query = (
        client.table("notification_logs")
        .select(
            "id,item_code,notified_at,recipient,previous_price,current_price,drop_rate,success,message"
        )
        .order("notified_at", desc=True)
        .order("id", desc=True)
        .limit(normalized_limit)
    )
    if item_code:
        query = query.eq("item_code", item_code)

    rows = query.execute().data or []
    return [
        NotificationLog.model_validate(
            {
                "id": row["id"],
                "item_code": row["item_code"],
                "notified_at": row["notified_at"],
                "recipient": row.get("recipient"),
                "previous_price": row["previous_price"],
                "current_price": row["current_price"],
                "drop_rate": row["drop_rate"],
                "success": _as_bool(row.get("success"), default=False),
                "message": row.get("message"),
            }
        )
        for row in rows
    ]
