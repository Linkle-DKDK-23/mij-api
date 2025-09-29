import os
from dotenv import load_dotenv

# ========================
# ✅ .env スイッチング処理
# ========================
env = os.getenv("ENV", "staging")
env_file = f".env.{env}"
load_dotenv(dotenv_path=env_file)
print(f" Loaded FastAPI ENV: {env_file}")

from fastapi import FastAPI
from app.routers import api_router
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.csrf import CSRFMiddleware
app = FastAPI()

# ========================
# FastAPIアプリ定義
# ========================
origins = [
    # ローカル開発用
    "http://localhost:3000",

    "http://localhost:3001",

    # ステージング環境
    "https://stg.mijfans.jp",
    "https://stg-admin.mijfans.jp",


    # 本番環境用
    "https://prd-admin.linkle.group"
]

@app.get("/healthz")
def healthz(): return {"ok": True}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSRF ミドルウェアは CORS より後でOK
app.add_middleware(CSRFMiddleware)
app.include_router(api_router)
