from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.deps.auth import get_current_user
from app.models.user import Users
from app.schemas.plan import PlanCreateRequest, PlanResponse, PlanListResponse
from app.crud.plan_crud import create_plan, get_user_plans

router = APIRouter()

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
        plan = create_plan(db, current_user.id, plan_data)
        return plan
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
