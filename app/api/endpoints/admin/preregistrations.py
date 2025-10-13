from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.deps.auth import get_current_admin_user
from app.schemas.admin import (
    AdminPreregistrationResponse,
    PaginatedResponse
)
from app.models.user import Users
from app.crud.preregistrations_curd import get_preregistrations_paginated

router = APIRouter()

@router.get("/preregistrations", response_model=PaginatedResponse[AdminPreregistrationResponse])
def get_preregistrations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort: Optional[str] = "created_at_desc",
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """事前登録一覧を取得"""

    preregistrations, total = get_preregistrations_paginated(
        db=db,
        page=page,
        limit=limit,
        search=search,
        sort=sort
    )

    return PaginatedResponse(
        data=[AdminPreregistrationResponse.from_orm(prereg) for prereg in preregistrations],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit if total > 0 else 1
    )
