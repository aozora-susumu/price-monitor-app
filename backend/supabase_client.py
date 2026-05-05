import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))


@lru_cache
def get_supabase_client() -> Client:
    # lru_cache でインスタンスをプロセス内で再利用し、リクエストごとの接続オーバーヘッドを避ける。
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SECRET_API_KEY")

    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SECRET_API_KEY must be set in backend/.env"
        )

    return create_client(supabase_url, supabase_key)
