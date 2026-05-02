import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from models import CheckResult, CheckSummary, WatchItem
from notifiers import send_email_notification
from rakuten_client import get_product_by_item_code
from storage import apply_monitor_update, load_watch_items

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

    for item in items:
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
            checked_at = datetime.now(UTC)
            history_point = product.price_history[-1]

            notified = False
            recipient: str | None = None
            notify_message = "No notification needed"
            if previous_price > 0:
                drop_rate = (previous_price - product.current_price) / previous_price
            else:
                drop_rate = 0

            should_log = drop_rate >= item.drop_rate_threshold
            if should_log:
                notified, recipient = _notify(item)
                notify_message = "Sent" if notified else "Notification sending failed"
                if notified:
                    notified_count += 1

            applied = apply_monitor_update(
                item=item,
                title=product.title,
                url=product.url,
                image=product.image,
                current_price=product.current_price,
                checked_at=checked_at,
                history_checked_at=history_point.timestamp,
                should_log=should_log,
                recipient=recipient,
                previous_price=previous_price,
                drop_rate=drop_rate,
                notify_success=notified,
                notify_message=notify_message,
            )

            if not applied:
                results.append(
                    CheckResult(
                        item_code=item.item_code,
                        checked=False,
                        notified=False,
                        message=(
                            "Skipped due to concurrent update (optimistic lock conflict)"
                        ),
                    )
                )
                continue

            results.append(
                CheckResult(
                    item_code=item.item_code,
                    checked=True,
                    notified=notified,
                    message=(f"Checked successfully (drop_rate={drop_rate:.4f})"),
                )
            )
        except Exception as exc:  # pragma: no cover
            results.append(
                CheckResult(
                    item_code=item.item_code,
                    checked=False,
                    notified=False,
                    message=f"Check failed: {exc}",
                )
            )

    return CheckSummary(
        checked_at=datetime.now(UTC),
        checked_count=len(items),
        notified_count=notified_count,
        results=results,
    )
