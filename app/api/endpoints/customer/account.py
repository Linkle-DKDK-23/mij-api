from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from app.db.base import get_db
from app.deps.auth import get_current_user
from app.models.user import Users
from app.schemas.account import (
    Kind,
    AccountInfoResponse, 
    AccountUpdateRequest, 
    AccountUpdateResponse, 
    AvatarPresignRequest, 
    AccountPresignResponse,
    AccountPostStatusResponse,
    AccountPostResponse,
)
from app.schemas.commons import UploadItem, PresignResponseItem
from app.crud.followes_crud import get_follower_count
from app.crud.post_crud import get_total_likes_by_user_id, get_posts_count_by_user_id,get_post_status_by_user_id
from app.crud.sales_crud import get_total_sales
from app.crud.plan_crud import get_plan_counts
from app.crud.user_crud import check_profile_name_exists, update_user
from app.crud.profile_crud import get_profile_by_user_id
from app.services.s3.keygen import account_asset_key
from app.services.s3.presign import presign_put_public
from app.crud.profile_crud import update_profile
import os

router = APIRouter()
BASE_URL = os.getenv("CDN_BASE_URL")

@router.get("/info", response_model=AccountInfoResponse)
def get_account_info(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    アカウント情報を取得
    """
    try:
        profile = get_profile_by_user_id(db, current_user.id)

        follower_data = get_follower_count(db, current_user.id)
        
        total_likes = get_total_likes_by_user_id(db, current_user.id)
        
        posts_data = get_posts_count_by_user_id(db, current_user.id)
        
        total_sales = get_total_sales(db, current_user.id)
        
        plan_data = get_plan_counts(db, current_user.id)
        
        return AccountInfoResponse(
            profile_name=current_user.profile_name or "",
            username=profile.username if profile else "",
            avatar_url=f"{BASE_URL}/{profile.avatar_url}" if profile and profile.avatar_url else None,
            cover_url=f"{BASE_URL}/{profile.cover_url}" if profile and profile.cover_url else None,
            followers_count=follower_data["followers_count"] if follower_data else 0,
            following_count=follower_data["following_count"] if follower_data else 0,
            total_likes=total_likes or 0,
            pending_posts_count=posts_data["peding_posts_count"] if posts_data else 0,
            rejected_posts_count=posts_data["rejected_posts_count"] if posts_data else 0,
            unpublished_posts_count=posts_data["unpublished_posts_count"] if posts_data else 0,
            deleted_posts_count=posts_data["deleted_posts_count"] if posts_data else 0,
            approved_posts_count=posts_data["approved_posts_count"] if posts_data else 0,
            total_sales=total_sales or 0,
            plan_count=plan_data["plan_count"] if plan_data else 0,
            total_plan_price=plan_data["total_price"] if plan_data else 0
        )
    except Exception as e:
        print("アカウント情報取得エラーが発生しました", e)
        # エラー時はデフォルト値で返す
        return AccountInfoResponse(
            profile_name=current_user.profile_name or "",
            username="",
            avatar_url=None,
            cover_url=None,
            followers_count=0,
            following_count=0,
            total_likes=0,
            pending_posts_count=0,
            rejected_posts_count=0,
            unpublished_posts_count=0,
            deleted_posts_count=0,
            approved_posts_count=0,
            total_sales=0,
            plan_count=0,
            total_plan_price=0
        )

@router.put("/update", response_model=AccountUpdateResponse)
def update_account_info(
    update_data: AccountUpdateRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    アカウント情報を更新

    Args:
        update_data (AccountUpdateRequest): 更新するアカウント情報
        current_user (Users): 現在のユーザー
        db (Session): データベースセッション

    Returns:
        AccountUpdateResponse: アカウント情報更新のレスポンス

    Raises:
        HTTPException: エラーが発生した場合
    """
    try:
        if update_data.name:
            if check_profile_name_exists(db, update_data.name) and update_data.name != current_user.profile_name:
                raise HTTPException(status_code=400, detail="このユーザー名は既に使用されています")

            user = update_user(db, current_user.id, update_data.name)

        if update_data.username:
            profile = update_profile(db, current_user.id, update_data)

        db.commit()
        db.refresh(user)
        db.refresh(profile)

        return AccountUpdateResponse(
            message="アカウント情報が正常に更新されました",
            success=True
        )
    except Exception as e:
        print("アカウント情報更新エラーが発生しました", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/presign-upload")
def presign_upload(
    request: AvatarPresignRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    アバターのアップロードURLを生成
    """
    try:

        allowed_kinds =  {"avatar","cover"}

        seen = set()
        for f in request.files:
            if f.kind not in allowed_kinds:
                raise HTTPException(400, f"unsupported kind: {f.kind}")
            if f.kind in seen:
                raise HTTPException(400, f"duplicated kind: {f.kind}")
            seen.add(f.kind)

        uploads: Dict[Kind, UploadItem] = {}

        for f in request.files:
            key = account_asset_key(str(user.id), f.kind, f.ext)

            response = presign_put_public("public", key, f.content_type)
            
            uploads[f.kind] = PresignResponseItem(
                key=response["key"],
                upload_url=response["upload_url"],
                expires_in=response["expires_in"],
                required_headers=response["required_headers"]
            )

        return AccountPresignResponse(uploads=uploads)
    except Exception as e:
        print("アップロードURL生成エラーが発生しました", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts")
def get_post_status(
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    投稿ステータスを取得
    """
    try:
        posts_data = get_post_status_by_user_id(db, user.id)
        
        # データ変換用のヘルパー関数
        def convert_posts(posts_list):
            return [
                AccountPostResponse(
                    id=str(post.Posts.id),
                    description=post.Posts.description,
                    thumbnail_url=f"{BASE_URL}/{post.thumbnail_key}" if post.thumbnail_key else None,
                    likes_count=post.likes_count,
                    creator_name=post.profile_name,
                    username=post.username,
                    creator_avatar_url=f"{BASE_URL}/{post.avatar_url}" if post.avatar_url else None,
                    price=post.post_price,
                    currency=post.post_currency
                )
                for post in posts_list
            ]
        
        return AccountPostStatusResponse(
            pending_posts=convert_posts(posts_data["pending_posts"]),
            rejected_posts=convert_posts(posts_data["rejected_posts"]),
            unpublished_posts=convert_posts(posts_data["unpublished_posts"]),
            deleted_posts=convert_posts(posts_data["deleted_posts"]),
            approved_posts=convert_posts(posts_data["approved_posts"])
        )
    except Exception as e:
        print("投稿ステータス取得エラーが発生しました", e)
        raise HTTPException(status_code=500, detail=str(e))