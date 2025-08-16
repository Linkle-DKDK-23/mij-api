# FastAPI
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

from app.services.s3.keygen import video_key
from app.services.s3.presign import presign_put, presign_get

from app.schemas.video import UploadRequest, PlayRequest, CreateUploadReq


# Services/Repositories
# from app.services.s3.s3_service import (
#     generate_presigned_url,
#     generate_play_url
# )

router = APIRouter()

# @router.post("/presign-upload")
# def video_presign_upload(body: CreateUploadReq, user=Depends(require_creator_auth)):
#     key = video_key(user.id, body.filename)
#     return presign_put("video", key, body.content_type)

# @router.get("/play-url")
# def video_play_url(file_key: str, user=Depends(require_authorized_to_view)):
#     return presign_get("video", file_key, expires_in=900, response_inline=True, filename=None)


# # 仮でtrueを返す
# def has_user_purchased(user_id: str, video_id: str) -> bool:
#     return True

# def make_video_upload(creator_id: str, filename: str, content_type: str):
#     key = video_key(creator_id, filename)
#     return presign_put("video", key, content_type, expires_in=300)

# def make_video_play_url(file_key: str, filename: str | None = None):
#     return presign_get(
#         "video",
#         file_key,
#         expires_in=900,
#         response_inline=True,
#         filename=filename,
#         response_content_type="application/vnd.apple.mpegurl" 
#     )