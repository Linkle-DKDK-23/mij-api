from fastapi import FastAPI
from app.routers import api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ========================
# FastAPIアプリ定義
# ========================
origins = [
    # ローカル開発用
    "http://localhost:5173",
    # 開発環境用
    "https://stg-admin.linkle.group",
    # 本番環境用
    "https://prd-admin.linkle.group"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
