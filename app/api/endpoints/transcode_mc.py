from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.services.s3.media_covert import build_media_rendition_job_settings, build_hls_abr4_settings
from app.crud.media_assets_crud import get_media_asset_by_post_id
from app.schemas.post_media import PoseMediaCovertRequest
from app.services.s3.keygen import (
    transcode_mc_key, 
    transcode_mc_hls_prefix, 
    transcode_mc_ffmpeg_key
)
from app.services.s3.image_screening import (
    _s3_download_bytes, 
    _s3_put_bytes,
    _is_supported_magic,
    _sanitize_and_variants,
    _moderation_check,
    _make_variant_keys,
)
from app.services.s3.client import s3_client_for_mc, ENV, s3_client, MEDIA_BUCKET_NAME, INGEST_BUCKET, KMS_ALIAS_MEDIA
from app.constants.enums import (
    MediaRenditionJobKind, 
    MediaRenditionJobBackend, 
    MediaRenditionJobStatus,
    MediaRenditionKind,
    PostStatus,
    PostType,
)
from app.crud.media_rendition_jobs_crud import create_media_rendition_job, update_media_rendition_job
from app.crud.media_rendition_crud import create_media_rendition
from app.crud.post_crud import update_post_status
import boto3
from typing import Dict, Any, Optional



S3 = boto3.client("s3", region_name="ap-northeast-1")

router = APIRouter()

def _create_media_convert_job(
    db: Session,
    asset_row: Any,
    post_id: str,
    job_kind: MediaRenditionJobKind,
    output_prefix: str,
    usermeta_type: str,
    build_settings_func
) -> Any:
    """
    メディアコンバートジョブを作成する共通処理
    
    Args:
        db: データベースセッション
        asset_row: メディアアセット行
        post_id: 投稿ID
        job_kind: ジョブの種類
        output_prefix: 出力プレフィックス
        usermeta_type: ユーザーメタタイプ
        build_settings_func: 設定ビルド関数
    
    Returns:
        作成されたメディアレンディションジョブ
    """
    # ジョブ作成
    media_rendition_job_data = {
        "asset_id": asset_row.id,
        "rendition_id": None,
        "kind": job_kind,
        "input_key": asset_row.storage_key,
        "output_prefix": output_prefix,
        "backend": MediaRenditionJobBackend.MEDIACONVERT,
        "status": MediaRenditionJobStatus.PENDING,
    }
    media_rendition_job = create_media_rendition_job(db, media_rendition_job_data)

    # ジョブ設定作成
    usermeta = {
        "postId": str(post_id), 
        "assetId": str(asset_row.id), 
        "renditionJobId": str(media_rendition_job.id),
        "type": usermeta_type,
        "env": ENV,
    } 
    settings = build_settings_func(
        input_key=asset_row.storage_key,
        output_prefix=output_prefix,
        usermeta=usermeta,
    )

    # MediaConvertにジョブを送信
    try:
        mediaconvert_client = s3_client_for_mc()
        response = mediaconvert_client.create_job(**settings)
        
        # ジョブIDを保存
        update_data = {
            "id": media_rendition_job.id,
            "status": MediaRenditionJobStatus.PROGRESSING,
            "job_id": response['Job']['Id']
        }
    except Exception as e:
        print(f"Error creating MediaConvert job: {e}")
        # エラーが発生した場合はステータスを更新
        update_data = {
            "id": media_rendition_job.id,
            "status": MediaRenditionJobStatus.FAILED,
        }

    # ジョブ設定更新
    update_media_rendition_job(db, media_rendition_job.id, update_data)
    return media_rendition_job


def _process_image_asset(
    db: Session,
    asset_row: Any,
    post_id: str
) -> Optional[Any]:
    """
    画像アセットを処理する共通処理
    
    Args:
        db: データベースセッション
        asset_row: メディアアセット行
        post_id: 投稿ID
    
    Returns:
        作成されたメディアレンディション（最後のもの）
    """
    # 1) 取り込み元の取得
    src_key = asset_row.storage_key
    img_bytes = _s3_download_bytes(INGEST_BUCKET, src_key)

    # 2) マジックナンバー/整合性チェック
    if not _is_supported_magic(img_bytes):
        raise HTTPException(400, "Unsupported image format")

    # 3) 任意: モデレーション
    mod = _moderation_check(img_bytes, min_conf=80.0)
    if mod["flagged"]:
        # ここでDBをREJECTにする等の処理を行っても良い
        raise HTTPException(status_code=400, detail=f"Image rejected by moderation: {mod['labels']}")

    # 4) 正規化＋派生生成
    variants = _sanitize_and_variants(img_bytes)

    # 出力先key
    base_output_key = transcode_mc_ffmpeg_key(
        creator_id=asset_row.creator_user_id,
        post_id=asset_row.post_id,
        ext="jpg", 
    )

    # ベースキーから派生ファイルの最終保存キーを決定
    variant_keys = _make_variant_keys(base_output_key)

    last_rendition = None
    # 5) アップロード（SSE-KMS, CacheControl 付き）
    for filename, (bytes_data, ctype) in variants.items():
        dst_key = variant_keys[filename]
        _s3_put_bytes(MEDIA_BUCKET_NAME, dst_key, bytes_data, ctype)

        # 6) DB: media_rendition 登録（bytesは保存サイズ）
        media_rendition_data = {
            "asset_id": asset_row.id,
            "kind": MediaRenditionKind.FFMPEG,  # 既存Enum流用。新設するなら IMAGE_PIPELINE に変更
            "storage_key": dst_key,
            "mime_type": ctype,
            "bytes": len(bytes_data),
        }
        last_rendition = create_media_rendition(db, media_rendition_data)
    
    return last_rendition


@router.post("/transcode_mc/{post_id}/{post_type}")
def transcode_mc_unified(
    post_id: str = Path(..., description="Post ID"),
    post_type: int = Path(..., description="Post Type"),
    db: Session = Depends(get_db)
):
    """
    投稿メディアコンバート統合処理（HLS ABR4 + FFmpeg）
    
    Args:
        post_id: str
        post_type: str
        db: Session
    
    Returns:
        dict: メディアコンバート結果
    """
    try:
        # post_typeから処理タイプを決定
        type_mapping = {
            PostType.VIDEO: "video",  # 動画投稿
            PostType.IMAGE: "image",  # 画像投稿
        }
        type = type_mapping.get(post_type, "video")  # デフォルトはvideo

        # メディアアセットの取得
        assets = get_media_asset_by_post_id(db, post_id, post_type)
        if not assets:
            raise HTTPException(status_code=404, detail="Media asset not found")

        last_rendition = None

        for row in assets:
            # HLS ABR4処理（ビデオの場合のみ）
            if type == "video":
                output_prefix = transcode_mc_hls_prefix(
                    creator_id=row.creator_user_id,
                    post_id=row.post_id,
                    asset_id=row.id,
                )

                _create_media_convert_job(
                    db=db,
                    asset_row=row,
                    post_id=post_id,
                    job_kind=MediaRenditionJobKind.HLS_ABR4,
                    output_prefix=output_prefix,
                    usermeta_type="final-hls",
                    build_settings_func=build_hls_abr4_settings
                )

            # FFmpeg処理（画像の場合のみ）
            if type == "image":
                last_rendition = _process_image_asset(db, row, post_id)

        # 投稿ステータスの更新
        post = update_post_status(db, post_id, PostStatus.APPROVED)
        db.commit()
        
        if last_rendition:
            db.refresh(last_rendition)
            db.refresh(post)

        return {"status": True, "message": f"Media conversion completed for {type}"}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")