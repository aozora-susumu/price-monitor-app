import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from models import CheckResult, CheckSummary, WatchItem
from notifiers import send_email_notification
from rakuten_client import get_product_by_item_code
from storage import load_watch_items, log_notification, save_watch_items

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
DEFAULT_NOTIFY_TO = os.getenv("NOTIFY_TO_EMAIL")


def _build_message(item: WatchItem) -> tuple[str, str]:
    subject = f"[Price Alert] {item.title}"
    body = (
        f"Item code: {item.item_code}\n"
        f"Title: {item.title}\n"
        f"URL: {item.url}\n"
        f"Current price: {item.current_price}\n"
    )
    return subject, body


def _notify(item: WatchItem) -> tuple[bool, str | None]:
    subject, body = _build_message(item)
    notify_to = item.notify_to or DEFAULT_NOTIFY_TO

    if notify_to:
        return send_email_notification(notify_to, subject, body), notify_to

    return False, None


def check_all_prices() -> CheckSummary:
    items = load_watch_items()
    results: list[CheckResult] = []
    notified_count = 0

    for index, item in enumerate(items):
        if not item.notify:
            results.append(
                CheckResult(
                    item_code=item.item_code,
                    checked=False,
                    notified=False,
                    message="Notification disabled",
                )
            )
            continue

        try:
            product = get_product_by_item_code(item.item_code)
            previous_price = item.current_price
            item.title = product.title
            item.url = product.url
            item.image = product.image
            item.current_price = product.current_price
            item.price_history.append(product.price_history[-1])
            item.last_checked = datetime.now(UTC)

            notified = False
            if previous_price > 0:
                drop_rate = (previous_price - item.current_price) / previous_price
            else:
                drop_rate = 0

            if drop_rate >= item.drop_rate_threshold:
                notified, recipient = _notify(item)
                log_notification(
                    item_code=item.item_code,
                    recipient=recipient,
                    previous_price=previous_price,
                    current_price=item.current_price,
                    drop_rate=drop_rate,
                    success=notified,
                    message=("Sent" if notified else "Notification sending failed"),
                )
                if notified:
                    notified_count += 1

            results.append(
                CheckResult(
                    item_code=item.item_code,
                    checked=True,
                    notified=notified,
                    message=(f"Checked successfully (drop_rate={drop_rate:.4f})"),
                )
            )
            items[index] = item
        except Exception as exc:  # pragma: no cover
            results.append(
                CheckResult(
                    item_code=item.item_code,
                    checked=False,
                    notified=False,
                    message=f"Check failed: {exc}",
                )
            )

    save_watch_items(items)

    return CheckSummary(
        checked_at=datetime.now(UTC),
        checked_count=len(items),
        notified_count=notified_count,
        results=results,
    )
