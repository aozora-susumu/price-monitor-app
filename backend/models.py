from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, model_validator


class PricePoint(BaseModel):
    timestamp: datetime
    price: int


class WatchItem(BaseModel):
    item_code: str
    keyword: str
    title: str
    url: str
    image: str | None = None
    current_price: int
    price_history: list[PricePoint] = Field(default_factory=list)
    notify: bool = True
    drop_rate_threshold: float = 0.05
    notify_to: EmailStr | None = None
    last_checked: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_fields(cls, data: Any):
        if isinstance(data, dict):
            if "item_code" not in data and "asin" in data:
                data["item_code"] = data["asin"]
            if "keyword" not in data:
                data["keyword"] = data.get("title", "")
            if "url" not in data:
                data["url"] = ""
            if "drop_rate_threshold" not in data:
                data["drop_rate_threshold"] = 0.05
            if data.get("current_price") is None:
                data["current_price"] = 0
        return data


class AddWatchItemRequest(BaseModel):
    keyword: str
    notify: bool = True
    drop_rate_threshold: float = Field(default=0.05, gt=0, le=1)
    notify_to: EmailStr | None = None


class UpdateWatchItemRequest(BaseModel):
    notify: bool | None = None
    drop_rate_threshold: float | None = Field(default=None, gt=0, le=1)
    notify_to: EmailStr | None = None


class RakutenProduct(BaseModel):
    item_code: str
    url: str
    title: str
    image: str | None
    current_price: int
    price_history: list[PricePoint]


class CheckResult(BaseModel):
    item_code: str
    checked: bool
    notified: bool
    message: str


class CheckSummary(BaseModel):
    checked_at: datetime
    checked_count: int
    notified_count: int
    results: list[CheckResult]


class NotificationLog(BaseModel):
    id: int
    item_code: str
    notified_at: datetime
    recipient: EmailStr | None = None
    previous_price: int
    current_price: int
    drop_rate: float
    success: bool
    message: str | None = None


class RakutenRawResponse(BaseModel):
    products: list[dict[str, Any]] = Field(default_factory=list)
