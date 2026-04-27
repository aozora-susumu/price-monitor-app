from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

# Always read backend/.env regardless of current working directory.
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

from models import (
    AddWatchItemRequest,
    NotificationLog,
    UpdateWatchItemRequest,
    WatchItem,
)
from monitor_service import check_all_prices
from rakuten_client import get_product_by_keyword
from storage import (
    delete_watch_item,
    get_notification_logs,
    get_watch_item,
    load_watch_items,
    upsert_watch_item,
)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Price monitor API is running"}


@app.get("/api/items")
def get_items():
    return load_watch_items()


@app.post("/api/items")
def add_item(payload: AddWatchItemRequest):
    product = get_product_by_keyword(payload.keyword)
    existing = get_watch_item(product.item_code)
    if existing:
        raise HTTPException(status_code=409, detail="itemCode already exists")

    item = WatchItem(
        item_code=product.item_code,
        keyword=payload.keyword,
        title=product.title,
        url=product.url,
        image=product.image,
        current_price=product.current_price,
        price_history=product.price_history,
        notify=payload.notify,
        drop_rate_threshold=payload.drop_rate_threshold,
        notify_to=payload.notify_to,
        last_checked=datetime.now(UTC),
    )
    upsert_watch_item(item)
    return item


@app.patch("/api/items/{item_code}")
def update_item(item_code: str, payload: UpdateWatchItemRequest):
    current = get_watch_item(item_code)
    if not current:
        raise HTTPException(status_code=404, detail="itemCode not found")

    if payload.notify is not None:
        current.notify = payload.notify
    if payload.drop_rate_threshold is not None:
        current.drop_rate_threshold = payload.drop_rate_threshold
    if payload.notify_to is not None:
        current.notify_to = payload.notify_to

    upsert_watch_item(current)
    return current


@app.post("/api/check-now")
def check_now():
    return check_all_prices()


@app.delete("/api/items/{item_code}")
def delete_item(item_code: str):
    deleted = delete_watch_item(item_code)
    if not deleted:
        raise HTTPException(status_code=404, detail="itemCode not found")
    return {"deleted": True, "item_code": item_code}


@app.get("/api/notifications", response_model=list[NotificationLog])
def list_notifications(item_code: str | None = None, limit: int = 100):
    return get_notification_logs(item_code=item_code, limit=limit)
