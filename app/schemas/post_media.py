from pydantic import BaseModel, Field
from typing import Literal, List
from app.schemas.commons import PresignResponseItem

ImageKind = Literal["ogp", "thumbnail"]
VideoKind = Literal["main", "sample"]

class PostMediaImageFileSpec(BaseModel):
    post_id: str
    kind: ImageKind
    content_type: Literal["video/mp4", "image/jpeg", "image/png", "image/webp"]
    ext: Literal["mp4", "jpg", "jpeg", "png", "webp"]

class PostMediaVideoFileSpec(BaseModel):
    kind: VideoKind
    content_type: Literal["video/mp4", "video/webm"]
    ext: Literal["mp4", "webm"]

class PostMediaImagePresignRequest(BaseModel):
    files: List[PostMediaImageFileSpec] = Field(..., description='例: [{"kind":"ogp","ext":"jpg"}, ...]')

class PostMediaVideoPresignRequest(BaseModel):
    videos: List[PostMediaVideoFileSpec] = Field(..., description='例: [{"kind":"main","ext":"mp4"}, ...]')

class PostMediaImagePresignResponse(BaseModel):
    uploads: dict[str, PresignResponseItem]

class PostMediaVideoPresignResponse(BaseModel):
    uploads: dict[str, PresignResponseItem]

class PostRequest(BaseModel):
    title: str
    category_ids: List[str]
    
