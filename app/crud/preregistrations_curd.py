from sqlalchemy.orm import Session
from app.models.preregistrations import Preregistrations
from uuid import UUID
from typing import List

def create_preregistration(db: Session, preregistration_data: Preregistrations) -> Preregistrations:
    db.add(preregistration_data)
    db.commit()
    db.refresh(preregistration_data)
    return preregistration_data
