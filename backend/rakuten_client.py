import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID")
BASE_URL = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"


def search_item(keyword: str):
    params = {"applicationId": RAKUTEN_APP_ID, "keyword": keyword, "hits": 1}

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    data = response.json()

    if "Items" not in data or len(data["Items"]) == 0:
        return None

    return data["Items"][0]["Item"]


if __name__ == "__main__":
    item = search_item("Fire TV Stick")
    print(item["itemName"], item["itemPrice"])
