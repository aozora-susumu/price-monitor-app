from fastapi import FastAPI
from rakuten_client import search_item

app = FastAPI()


@app.get("/")
def root():
    return {"message": "FastAPI is running!"}


@app.get("/api/search")
def search(keyword: str):
    item = search_item(keyword)
    if item is None:
        return {"error": "No item found"}
    return {
        "name": item["itemName"],
        "price": item["itemPrice"],
        "url": item["itemUrl"],
        "image": item["mediumImageUrls"][0]["imageUrl"],
    }
