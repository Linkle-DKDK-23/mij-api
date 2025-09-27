from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.deps.auth import get_current_user_optional
from app.schemas.post import PostCreateRequest, PostResponse, NewArrivalsResponse
from app.constants.enums import PostVisibility, PostType, PlanStatus, PriceType
from app.crud.post_crud import create_post, get_post_detail_by_id
from app.crud.plan_crud import create_plan
from app.crud.price_crud import create_price
from app.crud.post_plans_crud import create_post_plan
from app.crud.tags_crud import exit_tag, create_tag
from app.crud.post_tags_crud import create_post_tag
from app.crud.post_categories_crud import create_post_category
from app.crud.top_crud import get_recent_posts
from app.models.tags import Tags
from typing import List
import os
from os import getenv
from app.api.commons.utils import get_video_duration

router = APIRouter()

# PostTypeの文字列からenumへのマッピングを定義
POST_TYPE_MAPPING = {
    "video": PostType.VIDEO,
    "image": PostType.IMAGE,
}


BASE_URL = getenv("CDN_BASE_URL")

@router.post("/create", response_model=PostResponse)
async def create_post_endpoint(
    post_create: PostCreateRequest,
    user = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    try:
        # 可視性を判定
        visibility = _determine_visibility(post_create.single, post_create.plan)
        
        # 投稿データを準備
        post_data = {
            "creator_user_id": user.id,
            "description": post_create.description,
            "scheduled_at": post_create.formattedScheduledDateTime if post_create.scheduled else None,
            "expiration_at": post_create.expirationDate if post_create.expiration else None,
            "visibility": visibility,
            "post_type": POST_TYPE_MAPPING.get(post_create.post_type),
        }
        
        # 投稿を作成
        post = create_post(db, post_data)
        
        # 単品販売の設定
        individual_plan = None
        individual_price = None
        if post_create.single:
            individual_plan, individual_price = _create_individual_plan(
                db, user.id, post_create.price
            )
        
        # プランを投稿に紐づけ
        if post_create.plan or post_create.single:
            _link_plans_to_post(
                db, post.id, post_create.plan_ids, 
                individual_plan.id if individual_plan else None
            )
        
        # カテゴリを投稿に紐づけ
        category_posts = []
        if post_create.category_ids:
            category_posts = _create_post_categories(db, post.id, post_create.category_ids)
        
        # タグを投稿に紐づけ
        post_tag = None
        if post_create.tags:
            post_tag = _create_post_tag(db, post.id, post_create.tags)
        
        # データベースをコミット
        db.commit()
        db.refresh(post)
        
        # 必要に応じて他のオブジェクトもリフレッシュ
        if individual_plan:
            db.refresh(individual_plan)
        if individual_price:
            db.refresh(individual_price)
        if category_posts:
            for category_post in category_posts:
                db.refresh(category_post)
        if post_tag:
            db.refresh(post_tag)
        
        return post
        
    except Exception as e:
        print("投稿作成エラーが発生しました", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detail")
async def get_post_detail(
    post_id: str = Query(..., description="投稿ID"),
    user = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    try:
        # CRUD関数を使用して投稿詳細を取得
        user_id = user.id if user else None
        post_data = get_post_detail_by_id(db, post_id, user_id)
        
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
        
        
        # カテゴリ情報を整形
        categories_data = []
        if post_data["categories"]:
            categories_data = [
                {
                    "id": str(category.id),
                    "name": category.name,
                    "slug": category.slug
                }
                for category in post_data["categories"]
            ]
        
        post_detail = {
            "id": str(post_data["post"].id),
            "title": post_data["post"].description or "無題",
            "description": post_data["post"].description,
            "purchased": post_data["purchased"],
            "video_url": video_url,
            "thumbnail": thumbnail_url,
            "main_video_duration": post_data["main_video_duration"],
            "sample_video_duration": post_data["sample_video_duration"],
            "views": 0,
            "likes": post_data["likes_count"],
            "creator": {
                "name": post_data["creator_profile"].display_name if post_data["creator_profile"] else post_data["creator"].email,
                "slug": post_data["creator"].slug if post_data["creator_profile"] else post_data["creator"].email,
                "avatar": creator_avatar,
                "verified": True
            },
            "single": post_data["single"],
            "subscription": post_data["subscription"],
            "categories": categories_data,
            "created_at": post_data["post"].created_at.isoformat(),
            "updated_at": post_data["post"].updated_at.isoformat()
        }
        
        return post_detail
        
    except HTTPException:
        raise
    except Exception as e:
        print("投稿詳細取得エラーが発生しました", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/new-arrivals" , response_model=List[NewArrivalsResponse])
async def get_new_arrivals(
    db: Session = Depends(get_db)
):
    try:
        recent_posts = get_recent_posts(db, limit=50)
        return [NewArrivalsResponse(
            id=str(post.Posts.id),
            description=post.Posts.description,
            thumbnail_url=f"{BASE_URL}/{post.thumbnail_key}" if post.thumbnail_key else None,
            creator_name=post.slug,
            display_name=post.display_name,
            creator_avatar_url=f"{BASE_URL}/{post.avatar_url}" if post.avatar_url else None,
            duration=get_video_duration(post.duration_sec) if post.duration_sec else None
        ) for post in recent_posts]
    except Exception as e:
        print("新着投稿取得エラーが発生しました", e)
        raise HTTPException(status_code=500, detail=str(e))

def _determine_visibility(single: bool, plan: bool) -> int:
    """投稿の可視性を判定する"""
    if single and plan:
        return PostVisibility.BOTH
    elif single:
        return PostVisibility.SINGLE
    elif plan:
        return PostVisibility.PLAN
    else:
        return PostVisibility.SINGLE  # デフォルト

def _create_individual_plan(db: Session, user_id: str, price: int):
    """単品販売用のプランと価格を作成する"""
    plan_data = {
        "creator_user_id": user_id,
        "name": "単品販売",
        "description": "単品販売",
        "type": PlanStatus.SINGLE,
    }
    plan = create_plan(db, plan_data)
    
    price_data = {
        "plan_id": plan.id,
        "type": PriceType.SINGLE,
        "currency": "JPY",
        "price": price,
    }
    price_obj = create_price(db, price_data)
    
    return plan, price_obj

def _link_plans_to_post(db: Session, post_id: str, plan_ids: list, individual_plan_id: str = None):
    """投稿にプランを紐づける"""
    if individual_plan_id:
        plan_ids.append(individual_plan_id)
    
    for plan_id in plan_ids:
        plan_post_data = {
            "post_id": post_id,
            "plan_id": plan_id,
        }
        create_post_plan(db, plan_post_data)

def _create_post_categories(db: Session, post_id: str, category_ids: list):
    """投稿にカテゴリを紐づける"""
    category_posts = []
    for category_id in category_ids:
        category_data = {
            "post_id": post_id,
            "category_id": category_id,
        }
        category_post = create_post_category(db, category_data)
        category_posts.append(category_post)
    return category_posts

def _create_post_tag(db: Session, post_id: str, tag_name: str):
    """投稿にタグを紐づける"""
    # タグが存在するか確認
    existing_tag = exit_tag(db, tag_name)
    
    if not existing_tag:
        tag_data = {
            "slug": tag_name,
            "name": tag_name,
        }
        tag = create_tag(db, tag_data)
    else:
        tag = db.query(Tags).filter(Tags.name == tag_name).first()
    
    # タグと投稿の中間テーブルに登録
    post_tag_data = {
        "post_id": post_id,
        "tag_id": tag.id,
    }
    return create_post_tag(db, post_tag_data)
