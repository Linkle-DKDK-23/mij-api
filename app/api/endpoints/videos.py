# FastAPI
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

# Services/Repositories
from app.services.s3_service import (
    generate_presigned_url,
    generate_play_url
)

router = APIRouter()

class UploadRequest(BaseModel):
    filename: str
    content_type: str

class PlayRequest(BaseModel):
    video_id: str
    user_id: str

# 仮でtrueを返す
def has_user_purchased(user_id: str, video_id: str) -> bool:
    return True

@router.post("/upload")
def get_upload_url(request: UploadRequest):
    return generate_presigned_url(request.filename, request.content_type)


@router.post("/play-url")
def get_play_url(request: PlayRequest):
    if not has_user_purchased(request.user_id, request.video_id):
        raise HTTPException(status_code=403, detail="視聴権限がありません")


    file_key = f"uploads/{request.video_id}.MOV"
    return {"play_url": generate_play_url(file_key)}