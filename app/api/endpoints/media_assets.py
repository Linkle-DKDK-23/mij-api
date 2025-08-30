from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.services.s3.presign import presign_put_public, presign_put
from app.schemas.post_media import (
    PostMediaImagePresignRequest,
    PostMediaVideoPresignRequest,
    ImageKind,
    PostMediaImagePresignResponse,
    PostMediaVideoPresignResponse,
    VideoKind
)
from app.deps.auth import get_current_user
from app.db.base import get_db
from app.services.s3.keygen import post_media_image_key, post_media_video_key
from app.schemas.commons import PresignResponseItem, UploadItem
from typing import Dict
from app.crud.post_crud import update_post_media_assets

router = APIRouter()

@router.post("/")
async def presign_post_media_video(
    request: PostMediaVideoPresignRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        pass
    except Exception as e:
        print("アップロードURL生成エラーが発生しました", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/presign-image-upload")
async def presign_post_media_image(
    request: PostMediaImagePresignRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        allowed_kinds =  {"ogp","thumbnail","images"}

        seen = set()
        for f in request.files:
            if f.kind not in allowed_kinds:
                raise HTTPException(400, f"unsupported kind: {f.kind}")
            if f.kind != "images" and f.kind in seen:
                raise HTTPException(400, f"duplicated kind: {f.kind}")
            seen.add(f.kind)

        uploads: Dict[ImageKind, UploadItem] = {}

        for f in request.files:
            key = post_media_image_key(f.kind, str(user.id), str(f.post_id), f.ext)

            if f.kind == "images":
                response = presign_put("video", key, f.content_type)
            else:
                response = presign_put_public("public", key, f.content_type)

            if f.kind == "images":
                if f.kind not in uploads:
                    uploads[f.kind] = []
                uploads[f.kind].append(PresignResponseItem(
                    key=response["key"],
                    upload_url=response["upload_url"],
                    expires_in=response["expires_in"],
                    required_headers=response["required_headers"]
                ))
            else:
                uploads[f.kind] = PresignResponseItem(
                    key=response["key"],
                    upload_url=response["upload_url"],
                    expires_in=response["expires_in"],
                    required_headers=response["required_headers"]
                )
            post = update_post_media_assets(db, f.post_id, key, f.kind)

        db.commit()
        db.refresh(post)
        

        return PostMediaImagePresignResponse(uploads=uploads)
    except Exception as e:
        print("アップロードURL生成エラーが発生しました", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/presign-video-upload")
async def presign_post_media_video(
    request: PostMediaVideoPresignRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        allowed_kinds = {"main","sample"}

        seen = set()
        for f in request.files:
            if f.kind not in allowed_kinds:
                raise HTTPException(400, f"unsupported kind: {f.kind}")
            if f.kind != "images" and f.kind in seen:
                raise HTTPException(400, f"duplicated kind: {f.kind}")
            seen.add(f.kind)

        uploads: Dict[VideoKind, UploadItem] = {}

        for f in request.files:
            key = post_media_video_key(str(user.id), str(f.post_id), f.ext, f.kind)

            response = presign_put("video", key, f.content_type)

            uploads[f.kind] = PresignResponseItem(
                key=response["key"],
                upload_url=response["upload_url"],
                expires_in=response["expires_in"],
                required_headers=response["required_headers"]
            )
            post = update_post_media_assets(db, f.post_id, key, f.kind)

        db.commit()
        db.refresh(post)

        return PostMediaVideoPresignResponse(uploads=uploads)
    except Exception as e:
        print("アップロードURL生成エラーが発生しました", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
