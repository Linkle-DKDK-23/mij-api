from pydantic import BaseModel, Field
from typing import Literal, List, Union
from app.schemas.commons import PresignResponseItem
from uuid import UUID

ImageKind = Literal["ogp", "thumbnail", "images"]
VideoKind = Literal["main", "sample"]

class PostMediaImageFileSpec(BaseModel):
    post_id: UUID = Field(..., description='投稿ID')
    kind: ImageKind
    content_type: Literal["image/jpeg", "image/png", "image/webp"]
    ext: Literal["mp4", "jpg", "jpeg", "png", "webp"]

class PostMediaVideoFileSpec(BaseModel):
    post_id: UUID = Field(..., description='投稿ID')
    kind: VideoKind
    content_type: Literal["video/mp4", "video/webm", "video/quicktime"]
    ext: Literal["mp4", "webm", "mov"]

class PostMediaImagePresignRequest(BaseModel):
    files: List[PostMediaImageFileSpec] = Field(..., description='例: [{"kind":"ogp","ext":"jpg"}, ...]')

class PostMediaVideoPresignRequest(BaseModel):
    files: List[PostMediaVideoFileSpec] = Field(..., description='例: [{"kind":"main","ext":"mp4"}, ...]')

class PostMediaImagePresignResponse(BaseModel):
    uploads: dict[str, Union[PresignResponseItem, List[PresignResponseItem]]]

class PostMediaVideoPresignResponse(BaseModel):
    uploads: dict[str, PresignResponseItem]

class PostRequest(BaseModel):
    title: str
    category_ids: List[str]
    
class PoseMediaCovertRequest(BaseModel):
    post_id: UUID