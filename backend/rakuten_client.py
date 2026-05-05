import os
from datetime import UTC, datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from models import PricePoint, RakutenProduct

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID")
RAKUTEN_ACCESS_KEY = os.getenv("RAKUTEN_ACCESS_KEY")
RAKUTEN_APP_URL = os.getenv("RAKUTEN_APP_URL", "")
BASE_URL = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401"


def _validate_app_id() -> None:
    if not RAKUTEN_APP_ID:
        raise RuntimeError("RAKUTEN_APP_ID is not set")
    if not RAKUTEN_ACCESS_KEY:
        raise RuntimeError("RAKUTEN_ACCESS_KEY is not set")
    if not RAKUTEN_APP_URL:
        raise RuntimeError("RAKUTEN_APP_URL is not set")


def _auth_headers() -> dict:
    # 楽天 API は applicationId 加えて Origin / Referer ヘッダーに
    # 登録済みアプリ URL が設定されていないと 403 を返す。
    return {
        "accessKey": RAKUTEN_ACCESS_KEY,
        "Origin": RAKUTEN_APP_URL,
        "Referer": RAKUTEN_APP_URL + "/",
    }


def _extract_image(item: dict) -> str | None:
    images = item.get("mediumImageUrls") or []
    if not images:
        return None
    return images[0].get("imageUrl")


def _to_product(item: dict) -> RakutenProduct:
    price = int(item["itemPrice"])
    return RakutenProduct(
        item_code=item["itemCode"],
        url=item["itemUrl"],
        title=item["itemName"],
        image=_extract_image(item),
        current_price=price,
        price_history=[PricePoint(timestamp=datetime.now(UTC), price=price)],
    )


def search_item(keyword: str) -> dict | None:
    _validate_app_id()
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "keyword": keyword,
        "hits": 1,
    }
    response = requests.get(
        BASE_URL, params=params, headers=_auth_headers(), timeout=30
    )
    response.raise_for_status()

    data = response.json()

    if "Items" not in data or len(data["Items"]) == 0:
        return None

    return data["Items"][0]["Item"]


def get_product_by_keyword(keyword: str) -> RakutenProduct:
    item = search_item(keyword)
    if item is None:
        raise ValueError(f"No product found for keyword: {keyword}")
    return _to_product(item)


def get_product_by_item_code(item_code: str) -> RakutenProduct:
    _validate_app_id()
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "itemCode": item_code,
        "hits": 1,
    }
    response = requests.get(
        BASE_URL, params=params, headers=_auth_headers(), timeout=30
    )
    response.raise_for_status()
    data = response.json()

    if "Items" not in data or len(data["Items"]) == 0:
        raise ValueError(f"No product found for itemCode: {item_code}")

    return _to_product(data["Items"][0]["Item"])
