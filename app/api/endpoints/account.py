from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.deps.auth import get_current_user
from app.models.user import Users
from app.schemas.account import AccountInfoResponse, AccountUpdateRequest, AccountUpdateResponse
from app.crud.followes_crud import get_follower_count
from app.crud.post_crud import get_total_likes_by_user_id, get_posts_count_by_user_id
from app.crud.sales_crud import get_total_sales
from app.crud.plan_crud import get_plan_counts
from app.crud.user_crud import check_slug_exists

router = APIRouter()

@router.get("/info", response_model=AccountInfoResponse)
def get_account_info(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    アカウント情報を取得
    """
    try:
        follower_data = get_follower_count(db, current_user.id)
        
        total_likes = get_total_likes_by_user_id(db, current_user.id)
        
        posts_data = get_posts_count_by_user_id(db, current_user.id)
        
        total_sales = get_total_sales(db, current_user.id)
        
        plan_data = get_plan_counts(db, current_user.id)
        
        return AccountInfoResponse(
            followers_count=follower_data["followers_count"],
            following_count=follower_data["following_count"],
            total_likes=total_likes,
            pending_posts_count=posts_data["peding_posts_count"],  # Note: typo in original function
            rejected_posts_count=posts_data["rejected_posts_count"],
            unpublished_posts_count=posts_data["unpublished_posts_count"],
            deleted_posts_count=posts_data["deleted_posts_count"],
            approved_posts_count=posts_data["approved_posts_count"],
            total_sales=total_sales,
            plan_count=plan_data["plan_count"],
            total_plan_price=plan_data["total_price"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update", response_model=AccountUpdateResponse)
def update_account_info(
    update_data: AccountUpdateRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    アカウント情報を更新
    """
    try:
        if update_data.name:
            if check_slug_exists(db, update_data.name) and update_data.name != current_user.slug:
                raise HTTPException(status_code=400, detail="このユーザー名は既に使用されています")
            
            current_user.slug = update_data.name
            db.add(current_user)
        
        if update_data.display_name:
            if current_user.profile:
                current_user.profile.display_name = update_data.display_name
                db.add(current_user.profile)
            else:
                from app.crud.profile_crud import create_profile
                create_profile(db, current_user.id, update_data.display_name)
        
        db.commit()
        
        return AccountUpdateResponse(
            message="アカウント情報が正常に更新されました",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
