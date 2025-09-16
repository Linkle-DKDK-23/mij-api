from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.deps.auth import get_current_user
from app.schemas.post import PostCreateRequest, PostResponse
from app.constants.enums import PostVisibility, PostType
from app.crud.post_crud import create_post, get_post_detail_by_id
from app.crud.plan_crud import create_plan
from app.crud.price_crud import create_price
from app.constants.enums import PlanStatus, PriceType
from app.crud.post_plans_crud import create_post_plan
from app.crud.tags_crud import exit_tag, create_tag
from app.crud.post_tags_crud import create_post_tag
from app.crud.post_categories_crud import create_post_category
from app.models.tags import Tags
import os

router = APIRouter()

# PostTypeの文字列からenumへのマッピングを定義
POST_TYPE_MAPPING = {
    "video": PostType.VIDEO,
    "image": PostType.IMAGE,
}

@router.post("/create", response_model=PostResponse)
async def create_post_endpoint(
    post_create: PostCreateRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # 可視性判定
        if post_create.single and post_create.plan:
            visibility = PostVisibility.BOTH
        elif post_create.single:
            visibility = PostVisibility.SINGLE
        elif post_create.plan:
            visibility = PostVisibility.PLAN

        expiration_at = post_create.expirationDate if post_create.expiration else None
        scheduled_at = post_create.formattedScheduledDateTime if post_create.scheduled else None
        post_type = POST_TYPE_MAPPING.get(post_create.post_type)

        # postテーブル用にデータを整形
        post_data = {
            "creator_user_id": user.id,
            "description": post_create.description,
            "scheduled_at": scheduled_at,
            "expiration_at": expiration_at,
            "visibility": visibility,
            "post_type": post_type,
        }

        # 投稿作成
        post = create_post(db, post_data)

        # 変数の初期化
        plan = None
        price = None
        plan_post = None
        genre_post = None
        post_tag = None

        # 単品販売を設定している場合
        if post_create.single:
            # プランテーブルに登録
            plan_data = {
                "creator_user_id": user.id,
                "name": "単品販売",
                "description": "単品販売",
                "type": PriceType.SINGLE,
            }
            plan = create_plan(db, plan_data)

            # 価格テーブルに登録
            price_data = {
                "plan_id": plan.id,
                "type": PriceType.SINGLE,
                "currency": "JPY",
                "price": post_create.price,
            }
            price = create_price(db, price_data)

        # 投稿に紐づくプランを登録
        if post_create.plan:
            if post_create.single:
                post_create.plan_ids.append(plan.id)
            for plan_id in post_create.plan_ids:
                plan_post_data = {
                    "post_id": post.id,
                    "plan_id": plan_id,
                }
                plan_post = create_post_plan(db, plan_post_data)

        # カテゴリの登録
        category_posts = []
        if len(post_create.category_ids) > 0:
            for category_id in post_create.category_ids:
                category_data = {
                    "post_id": post.id,
                    "category_id": category_id,
                }
                category_post = create_post_category(db, category_data)
                category_posts.append(category_post)
        
        # タグの登録
        if post_create.tags:
            tag_name = post_create.tags
            # タグが存在するか確認
            existing_tag = exit_tag(db, tag_name)

            # タグが存在しない場合は作成
            if not existing_tag:
                tag_data = {
                    "slug": tag_name,
                    "name": tag_name,
                }
                tag = create_tag(db, tag_data)
            else:
                # 既存のタグを取得
                tag = db.query(Tags).filter(Tags.name == tag_name).first()

            # タグと投稿の中間テーブルに登録
            post_tag_data = {
                "post_id": post.id,
                "tag_id": tag.id,
            }
            post_tag = create_post_tag(db, post_tag_data)
             
        db.commit()
        db.refresh(post)
        
        # 条件付きでrefresh
        if post_create.single:
            db.refresh(plan)
            db.refresh(price)
        if post_create.plan and plan_post:
            db.refresh(plan_post)
        if post_create.tags and post_tag:
            db.refresh(post_tag)
        if len(post_create.category_ids) > 0 and category_posts:
            for category_post in category_posts:
                db.refresh(category_post)

        # レスポンスを整形
        return post
    except Exception as e:
        print("投稿作成エラーが発生しました", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def get_posts():
    return {"message": "Hello, World!"}

@router.get("/detail")
async def get_post_detail(
    post_id: str = Query(..., description="投稿ID"),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # CRUD関数を使用して投稿詳細を取得
        post_data = get_post_detail_by_id(db, post_id)
        
        if not post_data:
            raise HTTPException(status_code=404, detail="投稿が見つかりません")
        
        # 環境変数から設定を取得
        media_cdn_url = os.getenv("MEDIA_CDN_URL", "")
        cdn_base_url = os.getenv("CDN_BASE_URL", "")
        
        # レスポンス用のデータを構築
        video_url = None
        if post_data["video_rendition"]:
            video_url = f"{media_cdn_url}/{post_data['video_rendition']}"
        
        thumbnail_url = None
        if post_data["thumbnail_key"]:
            thumbnail_url = f"{cdn_base_url}/{post_data['thumbnail_key']}"
        
        creator_avatar = None
        if post_data["creator_profile"] and post_data["creator_profile"].avatar_url:
            creator_avatar = f"{cdn_base_url}/{post_data['creator_profile'].avatar_url}"
        
        # 時間フォーマット（秒から mm:ss 形式に変換）
        duration_formatted = "0:00"
        if post_data["duration"]:
            total_seconds = int(float(post_data["duration"]))
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            duration_formatted = f"{minutes}:{seconds:02d}"
        
        post_detail = {
            "id": str(post_data["post"].id),
            "title": post_data["post"].description or "無題",
            "description": post_data["post"].description,
            "video_url": video_url,
            "thumbnail": thumbnail_url,
            "duration": duration_formatted,
            "views": 0,  # 別途ビュー数管理が必要な場合は実装
            "likes": post_data["likes_count"],
            "creator": {
                "name": post_data["creator_profile"].display_name if post_data["creator_profile"] else post_data["creator"].email,
                "avatar": creator_avatar,
                "verified": True  # 必要に応じて検証ロジックを追加
            },
            "created_at": post_data["post"].created_at.isoformat(),
            "updated_at": post_data["post"].updated_at.isoformat()
        }
        
        return post_detail
        
    except HTTPException:
        raise
    except Exception as e:
        print("投稿詳細取得エラーが発生しました", e)
        raise HTTPException(status_code=500, detail=str(e))