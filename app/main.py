import os
from dotenv import load_dotenv
from fastapi import Request

# ========================
# ✅ .env スイッチング処理
# ========================
env = os.getenv("ENV", "development")
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

    "http://localhost:3003",

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

@app.get("/api/debug-cookies")
async def debug_cookies(request: Request):
    c = request.cookies
    return {
        "cognito": {
            "id_token": "present" if "cognito_id_token" in c else "missing",
            "access_token": "present" if "cognito_access_token" in c else "missing",
            "refresh_token": "present" if "cognito_refresh_token" in c else "missing",
        },
        "all_cookie_keys": list(c.keys()),  # 何が来てるか一覧
    }

# CSRF ミドルウェアは CORS より後でOK
app.add_middleware(CSRFMiddleware)
app.include_router(api_router)
