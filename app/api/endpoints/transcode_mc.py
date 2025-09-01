from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.services.s3.media_covert import build_media_rendition_job_settings
from app.crud.media_assets import get_media_asset_by_post_id
from app.schemas.media_covert import MediaCovertRequest
from app.services.s3.keygen import transcode_mc_key
from app.services.s3.client import s3_client_for_mc
from app.deps.auth import get_current_user
from app.constants.enums import (
    MediaRenditionJobKind, 
    MediaRenditionJobBackend, 
    MediaRenditionJobStatus
)
from app.crud.media_rendition_jobs_crud import create_media_rendition_job, update_media_rendition_job

router = APIRouter()


@router.get("/transcode_mc/{post_id}")
def transcode_mc(
    post_id: str = Path(..., description="Post ID"),
    db: Session = Depends(get_db)
):
    """
    投稿メディアコンバート

    Args:
        post_id: str
        db: Session

    Returns:
        dict: メディアコンバート
    """
    result = get_media_asset_by_post_id(db, post_id)
    if not result:
        raise HTTPException(status_code=404, detail="Media asset not found")

    # 結果からメディアアセットとユーザーIDを取得
    for row in result:
        output_key = transcode_mc_key(
            creator_id=row.creator_user_id,
            post_id=row.post_id,
            asset_id=row.id,
        )

        # ジョブ作成
        media_rendition_job_data = {
            "asset_id": row.id,
            "rendition_id": None,
            "kind": MediaRenditionJobKind.PREVIEW_MP4,
            "input_key": row.storage_key,
            "output_key": output_key,
            "backend": MediaRenditionJobBackend.MEDIACONVERT,
            "status": MediaRenditionJobStatus.PENDING,
        }
        media_rendition_job = create_media_rendition_job(db, media_rendition_job_data)

        # ジョブ設定作成
        usermeta = {"postId": str(post_id), "assetId": str(row.id), "renditionJobId": str(media_rendition_job.id)} 
        settings = build_media_rendition_job_settings(
            input_key=row.storage_key,
            output_key=output_key,
            usermeta=usermeta,
        )

        # MediaConvertにジョブを送信
        try:
            mediaconvert_client = s3_client_for_mc()
            response = mediaconvert_client.create_job(**settings)
            
            # ジョブIDを保存
            media_rendition_job_data = {
                "id": media_rendition_job.id,
                "status": MediaRenditionJobStatus.SUBMITTED,
                "job_id": response['Job']['Id']
            }
        except Exception as e:
            print(f"Error creating MediaConvert job: {e}")
            # エラーが発生した場合はステータスを更新
            media_rendition_job_data = {
                "id": media_rendition_job.id,
                "status": MediaRenditionJobStatus.FAILED,
            }

        # ジョブ設定更新
        update_media_rendition_job(db, media_rendition_job.id, media_rendition_job_data)

    db.commit()
    db.refresh(media_rendition_job)
    #　ジョブ作成
    # row.creator_user_idを使用してジョブを作成

    return "success"