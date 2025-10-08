from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.deps.auth import get_current_user
from app.models.user import Users
from app.schemas.plan import PlanCreateRequest, PlanResponse, PlanListResponse, PlanPostsResponse, PlanPostResponse
from app.crud.plan_crud import create_plan, get_user_plans, get_posts_by_plan_id
from app.constants.enums import PlanStatus, PriceType
from app.crud.price_crud import create_price
from uuid import UUID
import os

router = APIRouter()
BASE_URL = os.getenv("CDN_BASE_URL")

@router.post("/create", response_model=PlanResponse)
def create_user_plan(
    plan_data: PlanCreateRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    プランを作成
    """
    try:

        # プランを登録
        plan_create_data = {
            "creator_user_id": current_user.id,
            "name": plan_data.name,
            "description": plan_data.description,
            "type": PlanStatus.PLAN,
        }   
        plan = create_plan(db, plan_create_data)

        # 価格を登録
        price_create_data = {
            "plan_id": plan.id,
            "type": PriceType.PLAN,
            "currency": "JPY",
            "price": plan_data.price,
        }
        price = create_price(db, price_create_data)

        db.commit()
        db.refresh(plan)
        db.refresh(price)

        # 返却用に整形
        plan_response = PlanResponse(
            id=plan.id,
            name=plan.name,
            description=plan.description,
            price=price.price,
        )

        return plan_response
    except Exception as e:
        print("プラン作成エラーが発生しました", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=PlanListResponse)
def get_plans(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ユーザーのプラン一覧を取得
    """
    try:
        plans = get_user_plans(db, current_user.id)

        return PlanListResponse(plans=plans)
    except Exception as e:
        print("プラン取得エラーが発生しました", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{plan_id}/posts", response_model=PlanPostsResponse)
def get_plan_posts(
    plan_id: UUID,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    プランに紐づく投稿一覧を取得
    """
    try:
        posts_data = get_posts_by_plan_id(db, plan_id, current_user.id)

        posts = []
        for post, profile_name, username, avatar_url, thumbnail_key, duration_sec, likes_count, comments_count, created_at in posts_data:
            # 動画時間をフォーマット
            duration = None
            if duration_sec:
                minutes = int(duration_sec // 60)
                seconds = int(duration_sec % 60)
                duration = f"{minutes}:{seconds:02d}"

            post_response = PlanPostResponse(
                id=post.id,
                thumbnail_url=f"{BASE_URL}/{thumbnail_key}" if thumbnail_key else None,
                title=post.description or "",
                creator_avatar=f"{BASE_URL}/{avatar_url}" if avatar_url else None,
                creator_name=profile_name,
                creator_username=username,
                likes_count=likes_count or 0,
                comments_count=comments_count or 0,
                duration=duration,
                is_video=(post.post_type == 1),  # 1が動画
                created_at=created_at
            )
            posts.append(post_response)

        return PlanPostsResponse(posts=posts)
    except Exception as e:
        print("プラン投稿一覧取得エラーが発生しました", e)
        raise HTTPException(status_code=500, detail=str(e))
