from datetime import UTC, datetime

import pytest

import storage
from models import PricePoint, WatchItem


class _FakeRpcCall:
    def __init__(self, data):
        self._data = data

    def execute(self):
        return type("_Result", (), {"data": self._data})()


class _FakeClient:
    def __init__(self, data):
        self._data = data
        self.last_name = None
        self.last_params = None

    def rpc(self, name, params):
        self.last_name = name
        self.last_params = params
        return _FakeRpcCall(self._data)


def _make_item() -> WatchItem:
    now = datetime.now(UTC)
    return WatchItem(
        item_code="test:item",
        keyword="test",
        title="Test Item",
        url="https://example.com/item",
        image=None,
        current_price=1000,
        price_history=[PricePoint(timestamp=now, price=1000)],
        notify=True,
        drop_rate_threshold=0.1,
        notify_to=None,
        last_checked=now,
        updated_at=now,
    )


@pytest.mark.parametrize(
    ("rpc_data", "expected"),
    [
        (True, True),
        ([True], True),
        ([{"apply_monitor_check": True}], True),
        ([{"result": 1}], True),
        ([{"apply_monitor_check": False}], False),
        ([{"result": 0}], False),
        ([], False),
        (None, False),
    ],
)
def test_apply_monitor_update_parses_rpc_response(monkeypatch, rpc_data, expected):
    fake_client = _FakeClient(rpc_data)
    monkeypatch.setattr(storage, "get_supabase_client", lambda: fake_client)

    item = _make_item()
    result = storage.apply_monitor_update(
        item=item,
        title=item.title,
        url=item.url,
        image=item.image,
        current_price=900,
        checked_at=datetime.now(UTC),
        history_checked_at=datetime.now(UTC),
        should_log=True,
        recipient="notify@example.com",
        previous_price=1000,
        drop_rate=0.1,
        notify_success=True,
        notify_message="Sent",
    )

    assert result is expected


def test_apply_monitor_update_calls_expected_rpc(monkeypatch):
    fake_client = _FakeClient(True)
    monkeypatch.setattr(storage, "get_supabase_client", lambda: fake_client)

    item = _make_item()
    checked_at = datetime.now(UTC)
    history_checked_at = datetime.now(UTC)

    storage.apply_monitor_update(
        item=item,
        title="Updated Title",
        url="https://example.com/updated",
        image=None,
        current_price=900,
        checked_at=checked_at,
        history_checked_at=history_checked_at,
        should_log=False,
        recipient=None,
        previous_price=1000,
        drop_rate=0.1,
        notify_success=False,
        notify_message="No notification needed",
    )

    assert fake_client.last_name == "apply_monitor_check"
    assert fake_client.last_params is not None
    assert fake_client.last_params["p_item_code"] == item.item_code
    assert fake_client.last_params["p_title"] == "Updated Title"
    assert fake_client.last_params["p_current_price"] == 900
