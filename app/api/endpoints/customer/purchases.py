from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.deps.auth import get_current_user
from app.schemas.purchases import PurchaseCreateRequest
from app.crud.purchases_crud import create_purchase

router = APIRouter()

@router.post("/create")
async def create_purchase_endpoint(
    purchase_create: PurchaseCreateRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    購入情報を作成

    Args:
        purchase_create (PurchaseCreateRequest): 購入情報
        user (User): ユーザー
        db (Session): データベースセッション

    Raises:
        HTTPException: エラーが発生した場合

    Returns:
        dict: 購入情報を作成しました
    """
    try:
        purchase_data = {
            "user_id": user.id,
            "post_id": purchase_create.post_id,
            "plan_id": purchase_create.plan_id,
        }
        purchase = create_purchase(db, purchase_data)
        db.commit()
        db.refresh(purchase)

        return {
            "message": "購入情報を作成しました",
            "purchase_id": purchase.id
        }
    except Exception as e:
        db.rollback()
        print("購入情報処理に失敗しました", e)
        raise HTTPException(status_code=500, detail=str(e))