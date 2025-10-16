from fastapi import HTTPException
from PIL import Image, ImageOps
import io
from typing import Dict, Tuple, Optional, List
from app.services.s3.client import KMS_ALIAS_MEDIA
import boto3

REGION = "ap-northeast-1"
S3 = boto3.client("s3", region_name=REGION)
REKOG = boto3.client("rekognition", region_name=REGION)

# ---- helpers ----
def _s3_download_bytes(bucket: str, key: str) -> bytes:
    try:
        obj = S3.get_object(Bucket=bucket, Key=key)
        return obj["Body"].read()
    except Exception as e:
        raise HTTPException(500, f"S3 get_object failed: {e}")

def _s3_put_bytes(bucket: str, key: str, data: bytes, content_type: str) -> None:
    try:
        S3.put_object(
            Bucket=bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",
            ServerSideEncryption="aws:kms",
            SSEKMSKeyId=KMS_ALIAS_MEDIA,
        )
    except Exception as e:
        raise HTTPException(500, f"S3 put_object failed: {e}")

def _is_supported_magic(img_bytes: bytes) -> bool:
    sig = img_bytes[:12]
    # JPEG / PNG / WebP（簡易判定）
    if sig.startswith(b"\xff\xd8"):  # JPEG
        return True
    if sig.startswith(b"\x89PNG"):   # PNG
        return True
    if sig.startswith(b"RIFF") and img_bytes[8:12] == b"WEBP":  # WebP
        return True
    # HEICはpillow-heifが開ける場合があるので厳密魔法は省略
    return False

def _sanitize_and_variants(
    img_bytes: bytes,
    *,
    mosaic_boxes: Optional[List[Tuple[int, int, int, int]]] = None,
    mosaic_block: int = 20,
) -> Dict[str, Tuple[bytes, str]]:
    """
    出力:
      {
        "original.jpg":    (bytes, "image/jpeg"),
        "1080w.webp":      (bytes, "image/webp"),
        "mosaic.webp":     (bytes, "image/webp"),
      }
    """
    try:
        im = Image.open(io.BytesIO(img_bytes))
    except Exception:
        raise HTTPException(400, "Unsupported or corrupted image")

    # EXIFに基づく自動回転 + sRGB化（簡易）
    im = ImageOps.exif_transpose(im)
    im = im.convert("RGB")

    # original（再保存JPEG：EXIF除去・圧縮最適化）
    out_original = io.BytesIO()
    im.save(out_original, format="JPEG", quality=85, optimize=True)
    original_bytes = out_original.getvalue()

    # 1080w（横1080px基準のWebP）
    w_target = 1080
    im_1080 = im.copy()
    if im_1080.width > w_target:
        h = int(im_1080.height * (w_target / im_1080.width))
        im_1080 = im_1080.resize((w_target, h), Image.LANCZOS)
    out_1080 = io.BytesIO()
    im_1080.save(out_1080, format="WEBP", quality=78, method=6)
    w1080_bytes = out_1080.getvalue()

    # thumb（256pxサムネWebP）
    im_t = im.copy()
    im_t.thumbnail((256, 256), Image.LANCZOS)
    out_thumb = io.BytesIO()
    im_t.save(out_thumb, format="WEBP", quality=75, method=6)
    thumb_bytes = out_thumb.getvalue()

    # ★ モザイク（全面 or 指定領域）
    im_mosaic = _apply_mosaic(im, boxes=mosaic_boxes, block=mosaic_block)
    out_mosaic = io.BytesIO()
    im_mosaic.save(out_mosaic, format="WEBP", quality=80, method=6)
    mosaic_bytes = out_mosaic.getvalue()

    # モザイク版サムネ（先にモザイク→その後thumbnailで“粗さ”を維持）
    im_mosaic_t = im_mosaic.copy()
    im_mosaic_t.thumbnail((256, 256), Image.NEAREST)  # サムネはNEARESTで荒さを保つ
    out_mosaic_thumb = io.BytesIO()
    im_mosaic_t.save(out_mosaic_thumb, format="WEBP", quality=80, method=6)
    mosaic_thumb_bytes = out_mosaic_thumb.getvalue()

    return {
        "original.jpg":        (original_bytes, "image/jpeg"),
        "1080w.webp":          (w1080_bytes,   "image/webp"),
        "mosaic.webp":         (mosaic_bytes,  "image/webp"),
    }

def _moderation_check(img_bytes: bytes, min_conf: float = 80.0) -> Dict:
    """
    任意: 不適切判定。NGなら {'flagged': True, 'labels': [...]} を返す。
    """
    try:
        resp = REKOG.detect_moderation_labels(Image={"Bytes": img_bytes})
        labels = resp.get("ModerationLabels", [])
        flagged = any(l["Confidence"] >= min_conf for l in labels)
        return {"flagged": flagged, "labels": labels}
    except Exception:
        # Rekognition障害時は通し、ログのみ（必要なら厳格にfailに変更）
        return {"flagged": False, "labels": []}
    
def _make_variant_keys(base_key: str) -> dict:
    # "transcode-mc/{creator}/{post}/ffmpeg/{uuid}.ext" -> stem=".../{uuid}"
    stem, _ext = base_key.rsplit(".", 1)
    return {
        "original.jpg": f"{stem}_original.jpg",
        "1080w.webp":   f"{stem}_1080w.webp",
        "mosaic.webp":   f"{stem}_mosaic.webp",
    }

def _apply_mosaic(
    im: Image.Image,
    boxes: Optional[List[Tuple[int, int, int, int]]] = None,
    block: int = 40,
) -> Image.Image:
    """
    画像にピクセル化モザイクを適用。
    - boxes を指定しない/空: 画像全体に適用
    - boxes を指定: 各矩形領域のみに適用
    block: ピクセル化の粒度（大きいほど粗くなる、デフォルト40でより荒いモザイク）
    """
    im_px = im.copy()

    def _pixelate_region(img: Image.Image) -> Image.Image:
        w, h = img.size
        # より粗いピクセル化のため、より小さく縮小
        # 段階的に縮小してより効果的なモザイクを実現
        down_w = max(1, w // block)
        down_h = max(1, h // block)
        
        # 非常に小さなサイズに縮小してから拡大することで、より粗いモザイクを実現
        if down_w < 4 or down_h < 4:
            # 極端に小さくしてから拡大
            down_w = max(1, w // (block * 2))
            down_h = max(1, h // (block * 2))
        
        small = img.resize((down_w, down_h), Image.NEAREST)
        return small.resize((w, h), Image.NEAREST)

    if not boxes:
        # 全面モザイク
        return _pixelate_region(im_px)

    # 領域モザイク
    for (l, t, r, b) in boxes:
        # 領域は画像範囲にクリップ
        l2 = max(0, min(l, im_px.width))
        t2 = max(0, min(t, im_px.height))
        r2 = max(l2, min(r, im_px.width))
        b2 = max(t2, min(b, im_px.height))
        if r2 - l2 <= 0 or b2 - t2 <= 0:
            continue
        crop = im_px.crop((l2, t2, r2, b2))
        crop_px = _pixelate_region(crop)
        im_px.paste(crop_px, (l2, t2))
    return im_px