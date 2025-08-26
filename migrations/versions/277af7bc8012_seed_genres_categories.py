"""seed genres & categories

Revision ID: 277af7bc8012
Revises: ee6af6feb2fc
Create Date: 2025-08-26 14:38:58.400493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '277af7bc8012'
down_revision: Union[str, Sequence[str], None] = 'ee6af6feb2fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# --- Seed data (必要に応じて編集) ---
SEED_GENRES = [
    {"slug": "appearance", "name": "見た目", "sort_order": 100, "is_active": True},
    {"slug": "play", "name": "プレイ", "sort_order": 200, "is_active": True},
    {"slug": "type", "name": "タイプ", "sort_order": 300, "is_active": True},
    {"slug": "situation", "name": "シチュエーション", "sort_order": 400, "is_active": True},
    {"slug": "costume", "name": "コスチューム", "sort_order": 500, "is_active": True},
]

# 各ジャンル(slug)ごとのカテゴリ
SEED_CATEGORIES = {
    "appearance": [
        {"slug": "big-tits", "name": "巨乳", "sort_order": 10, "is_active": True},
        {"slug": "beauty", "name": "美女", "sort_order": 20, "is_active": True},
        {"slug": "big-breasts", "name": "美乳", "sort_order": 30, "is_active": True},
        {"slug": "nipples", "name": "乳首", "sort_order": 30, "is_active": True},
        {"slug": "ass", "name": "お尻", "sort_order": 30, "is_active": True},
        {"slug": "flat-tits", "name": "貧乳・微乳", "sort_order": 40, "is_active": True},
        {"slug": "chubby", "name": "ぽっちゃり", "sort_order": 50, "is_active": True},
        {"slug": "slim", "name": "スレンダー", "sort_order": 60, "is_active": True},
        {"slug": "no-hair", "name": "パイパン", "sort_order": 70, "is_active": True},
        {"slug": "cute", "name": "かわいい", "sort_order": 80, "is_active": True},
        {"slug": "pregnant", "name": "妊婦", "sort_order": 80, "is_active": True},
        {"slug": "small", "name": "小柄", "sort_order": 90, "is_active": True},
        {"slug": "muscle", "name": "筋肉", "sort_order": 100, "is_active": True},
        {"slug": "virgin", "name": "処女", "sort_order": 110, "is_active": True},
    ],
    "play": [
        {"slug": "masturbation", "name": "オナニー", "sort_order": 10, "is_active": True},
        {"slug": "fellatio", "name": "フェラ", "sort_order": 20, "is_active": True},
        {"slug": "deep-throat", "name": "中出し", "sort_order": 20, "is_active": True},
        {"slug": "hand-job", "name": "手コキ", "sort_order": 20, "is_active": True},
        {"slug": "sm", "name": "SM", "sort_order": 20, "is_active": True},
        {"slug": "toy", "name": "おもちゃ", "sort_order": 20, "is_active": True},
        {"slug": "multiple-play", "name": "複数プレイ", "sort_order": 20, "is_active": True},
        {"slug": "pee", "name": "おしっこ", "sort_order": 20, "is_active": True},
        {"slug": "ejaculation", "name": "潮吹き", "sort_order": 20, "is_active": True},
        {"slug": "riding", "name": "騎乗位", "sort_order": 20, "is_active": True},
        {"slug": "cum-in-vagina", "name": "生ハメ", "sort_order": 20, "is_active": True},
        {"slug": "lotion-oil", "name": "ローション・オイル", "sort_order": 20, "is_active": True},
        {"slug": "anal", "name": "アナル", "sort_order": 20, "is_active": True},
        {"slug": "cum-in-mouth", "name": "クンニ", "sort_order": 20, "is_active": True},
        {"slug": "cum-in-face", "name": "ごっくん", "sort_order": 20, "is_active": True},
        {"slug": "foot-job", "name": "足コキ", "sort_order": 20, "is_active": True},
        {"slug": "tickling", "name": "くすぐり", "sort_order": 20, "is_active": True},
        {"slug": "back", "name": "バック", "sort_order": 20, "is_active": True},
        {"slug": "pissing", "name": "パイズリ", "sort_order": 20, "is_active": True},
        {"slug": "spanking", "name": "ぶっかけ", "sort_order": 20, "is_active": True},
        {"slug": "dirty-talk", "name": "淫語", "sort_order": 20, "is_active": True},
        {"slug": "asmr", "name": "ASMR", "sort_order": 20, "is_active": True},
        {"slug": "soft", "name": "ソフト", "sort_order": 20, "is_active": True},
        {"slug": "sweat", "name": "汗だく", "sort_order": 20, "is_active": True},
    ],
    "type": [
        {"slug": "normal", "name": "素人", "sort_order": 10, "is_active": True},
        {"slug": "personal-shooting", "name": "個人撮影", "sort_order": 10, "is_active": True},
        {"slug": "wife", "name": "人妻", "sort_order": 10, "is_active": True},
        {"slug": "pervert", "name": "変態", "sort_order": 10, "is_active": True},
        {"slug": "mature", "name": "熟女", "sort_order": 10, "is_active": True},
        {"slug": "underground", "name": "裏垢", "sort_order": 10, "is_active": True},
        {"slug": "face-out", "name": "顔出し", "sort_order": 10, "is_active": True},
        {"slug": "selfie", "name": "自撮り", "sort_order": 10, "is_active": True},
        {"slug": "foot-fetish", "name": "脚フェチ", "sort_order": 10, "is_active": True},
        {"slug": "slut", "name": "痴女", "sort_order": 10, "is_active": True},
        {"slug": "pantyhose", "name": "パンチラ", "sort_order": 10, "is_active": True},
        {"slug": "erotic", "name": "着エロ", "sort_order": 10, "is_active": True},
        {"slug": "perverted", "name": "淫乱", "sort_order": 10, "is_active": True},
        {"slug": "pickup", "name": "ナンパ", "sort_order": 10, "is_active": True},
        {"slug": "lesbian", "name": "レズ", "sort_order": 10, "is_active": True},
        {"slug": "face-out", "name": "目出し", "sort_order": 10, "is_active": True},
        {"slug": "sports", "name": "スポーツ", "sort_order": 10, "is_active": True},
        {"slug": "female", "name": "女性向け", "sort_order": 10, "is_active": True},
    ],
    "situation": [
        {"slug": "hame-shooting", "name": "ハメ撮り", "sort_order": 10, "is_active": True},
        {"slug": "exposure", "name": "露出", "sort_order": 10, "is_active": True},
        {"slug": "ntr", "name": "NTR", "sort_order": 10, "is_active": True},
        {"slug": "m-man", "name": "M男", "sort_order": 10, "is_active": True},
        {"slug": "massage", "name": "マッサージ", "sort_order": 10, "is_active": True},
        {"slug": "couple", "name": "カップル・夫婦", "sort_order": 10, "is_active": True},
        {"slug": "gal", "name": "ギャル", "sort_order": 10, "is_active": True},
        {"slug": "m-woman", "name": "M女", "sort_order": 10, "is_active": True},
        {"slug": "orgasm", "name": "絶頂", "sort_order": 10, "is_active": True},
        {"slug": "est", "name": "エステ", "sort_order": 10, "is_active": True},
        {"slug": "bath", "name": "お風呂", "sort_order": 10, "is_active": True},
        {"slug": "subjective", "name": "主観", "sort_order": 10, "is_active": True},
        {"slug": "infidelity", "name": "不倫", "sort_order": 10, "is_active": True},
        {"slug": "no-panties", "name": "ノーパン", "sort_order": 10, "is_active": True},
        {"slug": "no-bra", "name": "ノーブラ", "sort_order": 10, "is_active": True},
        {"slug": "breast-peek", "name": "胸チラ", "sort_order": 10, "is_active": True},
        {"slug": "maiko", "name": "風俗", "sort_order": 10, "is_active": True}
    ],
    "costume": [
        {"slug": "cosplay", "name": "コスプレ", "sort_order": 10, "is_active": True},
        {"slug": "underwear", "name": "下着", "sort_order": 10, "is_active": True},
        {"slug": "lingerie", "name": "ランジェリー", "sort_order": 10, "is_active": True},
        {"slug": "swimwear", "name": "水着", "sort_order": 10, "is_active": True},
        {"slug": "pantyhose", "name": "パンスト・タイツ", "sort_order": 10, "is_active": True},
        {"slug": "miniskirt", "name": "ミニスカ", "sort_order": 10, "is_active": True},
        {"slug": "business-suit", "name": "ビジネススーツ", "sort_order": 10, "is_active": True},
        {"slug": "nylon-socks", "name": "ニーソックス", "sort_order": 10, "is_active": True},
        {"slug": "mask", "name": "覆面・マスク", "sort_order": 10, "is_active": True},
        {"slug": "maid", "name": "メイド", "sort_order": 10, "is_active": True},
        {"slug": "body-con", "name": "ボディコン", "sort_order": 10, "is_active": True},
        {"slug": "bikini", "name": "バニーガール", "sort_order": 10, "is_active": True},
        {"slug": "maid", "name": "巫女", "sort_order": 10, "is_active": True},
        {"slug": "kimono", "name": "和服・浴衣", "sort_order": 10, "is_active": True},
        {"slug": "glasses", "name": "めがね", "sort_order": 10, "is_active": True},
    ],
}

def upgrade():
    conn = op.get_bind()

    # 1) genres を UPSERT（slug 一意想定 / CITEXTでもOK）
    conn.execute(
        sa.text("""
            INSERT INTO genres (slug, name, is_active, sort_order)
            VALUES (:slug, :name, :is_active, :sort_order)
            ON CONFLICT (slug) DO NOTHING;
        """),
        SEED_GENRES
    )

    # 2) categories を UPSERT（親 genre は slug から id 取得）
    insert_cat_stmt = sa.text("""
        INSERT INTO categories (genre_id, slug, name, is_active, sort_order)
        VALUES (:genre_id, :slug, :name, :is_active, :sort_order)
        ON CONFLICT (slug) DO NOTHING;
    """)

    for genre_slug, cats in SEED_CATEGORIES.items():
        gid = conn.execute(
            sa.text("SELECT id FROM genres WHERE slug = :slug"),
            {"slug": genre_slug}
        ).scalar()
        if gid is None:
            # ジャンルが無い場合はスキップ（必要なら例外でもOK）
            continue

        rows = []
        for c in cats:
            rows.append({
                "genre_id": gid,
                "slug": c["slug"],
                "name": c["name"],
                "is_active": c.get("is_active", True),
                "sort_order": c.get("sort_order", 0),
            })
        if rows:
            conn.execute(insert_cat_stmt, rows)

def downgrade():
    conn = op.get_bind()

    # 先に categories を削除
    cat_slugs = [c["slug"] for cats in SEED_CATEGORIES.values() for c in cats]
    if cat_slugs:
        params = {f"s{i}": slug for i, slug in enumerate(cat_slugs)}
        placeholders = ", ".join([f":s{i}" for i in range(len(cat_slugs))])
        conn.execute(sa.text(f"DELETE FROM categories WHERE slug IN ({placeholders})"), params)

    # 次に genres を削除
    genre_slugs = [g["slug"] for g in SEED_GENRES]
    if genre_slugs:
        params = {f"g{i}": slug for i, slug in enumerate(genre_slugs)}
        placeholders = ", ".join([f":g{i}" for i in range(len(genre_slugs))])
        # 依存カテゴリが残っていると消せないので、categories を先に消すのがポイント
        conn.execute(sa.text(f"DELETE FROM genres WHERE slug IN ({placeholders})"), params)
