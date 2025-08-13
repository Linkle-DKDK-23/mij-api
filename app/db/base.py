from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# DB接続用URL（.envから取得）
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# エンジン作成
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# セッション作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Naming convention helps Alembic autogenerate sensible constraint names
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Baseクラス（モデル用）
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# FastAPI用のDB依存関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
