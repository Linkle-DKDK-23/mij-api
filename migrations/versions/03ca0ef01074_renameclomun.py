"""renameclomun

Revision ID: 03ca0ef01074
Revises: 14b797bf63c5
Create Date: 2025-08-15 21:25:01.716868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03ca0ef01074'
down_revision: Union[str, Sequence[str], None] = '14b797bf63c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- Extensions (id/ci-text等で使用) ---
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # --- creator_type: 複合PKへ変更 ---
    # 1) 既存PKを削除（名前差異に対応）
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS pk_creator_type")
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS creator_type_pkey")

    # 2) 複合PKを作成
    op.create_primary_key("pk_creator_type", "creator_type", ["user_id", "gender_id"])

    # --- creator_type: 外部キーを意図した ondelete で再作成（任意/必要時） ---
    # 既存FKを削除（名前の差異に対応して複数候補を落とす）
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS fk_creator_type_user_id_users")
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS creator_type_user_id_fkey")
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS fk_creator_type_gender_id_gender")
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS creator_type_gender_id_fkey")

    # 望ましい ondelete でFKを再作成
    op.execute("""
        ALTER TABLE creator_type
        ADD CONSTRAINT fk_creator_type_user_id_users
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    """)
    op.execute("""
        ALTER TABLE creator_type
        ADD CONSTRAINT fk_creator_type_gender_id_gender
        FOREIGN KEY (gender_id) REFERENCES gender(id) ON DELETE RESTRICT
    """)

    # --- creator_type: 片側検索用インデックス（IF NOT EXISTSで冪等） ---
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relkind='i' AND c.relname='ix_creator_type_user_id'
            ) THEN
                CREATE INDEX ix_creator_type_user_id ON creator_type(user_id);
            END IF;
        END$$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relkind='i' AND c.relname='ix_creator_type_gender_id'
            ) THEN
                CREATE INDEX ix_creator_type_gender_id ON creator_type(gender_id);
            END IF;
        END$$;
    """)

    # --- updated_at 自動更新トリガ (users / gender) ---
    # 関数（冪等に作成/更新）
    op.execute("""
    CREATE OR REPLACE FUNCTION set_updated_at_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # users テーブル用トリガ
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_trigger WHERE tgname = 'trg_users_set_updated_at'
        ) THEN
            CREATE TRIGGER trg_users_set_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE PROCEDURE set_updated_at_timestamp();
        END IF;
    END$$;
    """)

    # gender テーブル用トリガ
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_trigger WHERE tgname = 'trg_gender_set_updated_at'
        ) THEN
            CREATE TRIGGER trg_gender_set_updated_at
            BEFORE UPDATE ON gender
            FOR EACH ROW
            EXECUTE PROCEDURE set_updated_at_timestamp();
        END IF;
    END$$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # --- updated_at トリガ撤去 ---
    op.execute("DROP TRIGGER IF EXISTS trg_users_set_updated_at ON users")
    op.execute("DROP TRIGGER IF EXISTS trg_gender_set_updated_at ON gender")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at_timestamp()")

    # --- creator_type: インデックス削除 ---
    op.execute("DROP INDEX IF EXISTS ix_creator_type_gender_id")
    op.execute("DROP INDEX IF EXISTS ix_creator_type_user_id")

    # --- creator_type: FK を削除（作り直す場合に備え）
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS fk_creator_type_user_id_users")
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS fk_creator_type_gender_id_gender")
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS creator_type_user_id_fkey")
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS creator_type_gender_id_fkey")

    # --- creator_type: 複合PKを落として旧PK( user_id )に戻す（旧仕様へロールバックする想定） ---
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS pk_creator_type")
    op.execute("ALTER TABLE creator_type DROP CONSTRAINT IF EXISTS creator_type_pkey")
    op.create_primary_key("creator_type_pkey", "creator_type", ["user_id"])

    # 旧仕様のFK（on delete の挙動が不要なら適宜変更/削除）
    op.execute("""
        ALTER TABLE creator_type
        ADD CONSTRAINT creator_type_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id)
    """)
    op.execute("""
        ALTER TABLE creator_type
        ADD CONSTRAINT creator_type_gender_id_fkey
        FOREIGN KEY (gender_id) REFERENCES gender(id)
    """)

    # ※ Extensions は残してOK（他リビジョンで使うため）
