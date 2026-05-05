from datetime import UTC, datetime

import monitor_service
from models import PricePoint, RakutenProduct, WatchItem


def _make_watch_item(
    *,
    current_price: int,
    threshold: float,
    notify: bool = True,
) -> WatchItem:
    now = datetime.now(UTC)
    return WatchItem(
        item_code="test:item",
        keyword="test",
        title="Test Item",
        url="https://example.com/item",
        image=None,
        current_price=current_price,
        price_history=[PricePoint(timestamp=now, price=current_price)],
        notify=notify,
        drop_rate_threshold=threshold,
        notify_to=None,
        last_checked=now,
    )


def _make_product(*, item_code: str, price: int) -> RakutenProduct:
    now = datetime.now(UTC)
    return RakutenProduct(
        item_code=item_code,
        url="https://example.com/item",
        title="Test Item",
        image=None,
        current_price=price,
        price_history=[PricePoint(timestamp=now, price=price)],
    )


def test_check_all_prices_notifies_when_drop_rate_meets_threshold(monkeypatch):
    item = _make_watch_item(current_price=1000, threshold=0.1)
    product = _make_product(item_code=item.item_code, price=800)

    captured_apply_args: dict = {}

    monkeypatch.setattr(monitor_service, "load_watch_items", lambda: [item])
    monkeypatch.setattr(
        monitor_service,
        "get_product_by_item_code",
        lambda _: product,
    )
    monkeypatch.setattr(
        monitor_service,
        "_notify",
        lambda _: (True, "notify@example.com"),
    )

    def _fake_apply_monitor_update(**kwargs):
        captured_apply_args.update(kwargs)
        return True

    monkeypatch.setattr(
        monitor_service,
        "apply_monitor_update",
        _fake_apply_monitor_update,
    )

    summary = monitor_service.check_all_prices()

    assert summary.checked_count == 1
    assert summary.notified_count == 1
    assert len(summary.results) == 1
    assert summary.results[0].checked is True
    assert summary.results[0].notified is True
    assert captured_apply_args["should_log"] is True
    assert captured_apply_args["drop_rate"] == 0.2


def test_check_all_prices_does_not_notify_below_threshold(monkeypatch):
    item = _make_watch_item(current_price=1000, threshold=0.1)
    product = _make_product(item_code=item.item_code, price=950)

    captured_apply_args: dict = {}

    monkeypatch.setattr(monitor_service, "load_watch_items", lambda: [item])
    monkeypatch.setattr(
        monitor_service,
        "get_product_by_item_code",
        lambda _: product,
    )

    def _notify_should_not_be_called(_):
        raise AssertionError("_notify should not be called when threshold is not met")

    monkeypatch.setattr(monitor_service, "_notify", _notify_should_not_be_called)

    def _fake_apply_monitor_update(**kwargs):
        captured_apply_args.update(kwargs)
        return True

    monkeypatch.setattr(
        monitor_service,
        "apply_monitor_update",
        _fake_apply_monitor_update,
    )

    summary = monitor_service.check_all_prices()

    assert summary.checked_count == 1
    assert summary.notified_count == 0
    assert summary.results[0].checked is True
    assert summary.results[0].notified is False
    assert captured_apply_args["should_log"] is False


def test_check_all_prices_marks_conflict_when_optimistic_lock_fails(monkeypatch):
    item = _make_watch_item(current_price=1000, threshold=0.05)
    product = _make_product(item_code=item.item_code, price=900)

    monkeypatch.setattr(monitor_service, "load_watch_items", lambda: [item])
    monkeypatch.setattr(
        monitor_service,
        "get_product_by_item_code",
        lambda _: product,
    )
    monkeypatch.setattr(monitor_service, "_notify", lambda _: (False, None))
    monkeypatch.setattr(
        monitor_service,
        "apply_monitor_update",
        lambda **_: False,
    )

    summary = monitor_service.check_all_prices()

    assert summary.checked_count == 1
    assert summary.notified_count == 0
    assert summary.results[0].checked is False
    assert summary.results[0].notified is False
    assert "optimistic lock conflict" in summary.results[0].message
