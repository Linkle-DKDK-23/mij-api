from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.preregistrations import PreregistrationCreateRequest
from app.crud.preregistrations_curd import create_preregistration
from app.models.preregistrations import Preregistrations

router = APIRouter()

@router.post("/")
def create_preregistration_endpoint(preregistration: PreregistrationCreateRequest, db: Session = Depends(get_db)):
    try:
        preregistration_data = Preregistrations(
            name=preregistration.name,
            email=preregistration.email,
            x_name=preregistration.x_name
        )
        preregistration_data = create_preregistration(db, preregistration_data)

        if preregistration_data:
            # 登録が完了したらメールを送信する
            return {"result": preregistration_data}
        else:
            raise HTTPException(status_code=500, detail="Failed to create preregistration")
    except Exception as e:
        print("Error creating preregistration", e)
        raise HTTPException(status_code=500, detail=str(e)) 