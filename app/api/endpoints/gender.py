from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.gender import GenderOut
from typing import List
from app.crud.gender_crud import get_genders

router = APIRouter()

@router.get("/", response_model=List[GenderOut])
def get_genders_api(db: Session = Depends(get_db)):
    """
    性別一覧を取得
    
    Args:
        db (Session): データベースセッション

    Returns:
        List[GenderOut]: 性別一覧
    """
    try:
        genders = get_genders(db)
        return [GenderOut(slug=gender.slug, name=gender.name) for gender in genders]
    except Exception as e:
        print("性別一覧取得エラー: ", e)
        raise HTTPException(status_code=500, detail=str(e))