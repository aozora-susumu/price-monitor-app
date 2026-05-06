import logging
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
    subject = f"【価格下落通知】{item.title}"
    body = (
        f"監視中の商品の価格が下落しました。\n\n"
        f"商品名: {item.title}\n"
        f"現在価格: ¥{item.current_price:,}\n"
        f"商品ページ: {item.url}\n"
    )
    return subject, body


def _notify(item: WatchItem) -> tuple[bool, str | None]:
    subject, body = _build_message(item)
    notify_to = item.notify_to or DEFAULT_NOTIFY_TO

    if notify_to:
        try:
            return send_email_notification(notify_to, subject, body), notify_to
        except Exception:  # pragma: no cover
            logging.exception(
                "Notification send failed for item_code=%s", item.item_code
            )
            return False, notify_to

    return False, None


def check_all_prices() -> CheckSummary:
    items = load_watch_items()
    results: list[CheckResult] = []
    notified_count = 0

    for item in items:
        try:
            product = get_product_by_item_code(item.item_code)
            previous_price = item.current_price
            checked_at = datetime.now(UTC)
            history_point = product.price_history[-1]

            notified = False
            recipient: str | None = None
            notify_message = (
                "Notification disabled" if not item.notify else "No notification needed"
            )
            if previous_price > 0:
                drop_rate = (previous_price - product.current_price) / previous_price
            else:
                drop_rate = 0

            # should_log は「通知履歴に記録するか」、notified は「メールが実際に送信できたか」を表す。
            # 閾値を超えていても宛先が未設定の場合など、should_log=True・notified=False は起こり得る。
            # notify=False の場合は通知を行わないが、価格更新そのものは継続する。
            should_log = item.notify and drop_rate >= item.drop_rate_threshold
            if should_log:
                try:
                    notified, recipient = _notify(item)
                except Exception:
                    logging.exception(
                        "Notification process failed for item_code=%s", item.item_code
                    )
                    notified = False
                    recipient = item.notify_to or DEFAULT_NOTIFY_TO
                notify_message = "Sent" if notified else "Notification sending failed"
                if notified:
                    notified_count += 1

            # apply_monitor_update は楽観的ロックによる原子的書き込み。
            # False の場合は並行リクエストによる競合が発生したことを意味する。
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
            logging.exception("Price check failed for item_code=%s", item.item_code)
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
