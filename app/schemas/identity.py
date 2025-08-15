from pydantic import BaseModel, Field
from typing import Dict, List, Literal
from uuid import UUID

Kind = Literal["front", "back", "selfie"]

class FileSpec(BaseModel):
    kind: Kind
    content_type: Literal["image/jpeg","image/png","application/pdf"]
    ext: Literal["jpg","jpeg","png","pdf"]

class PresignRequest(BaseModel):
    files: List[FileSpec] = Field(..., description='例: [{"kind":"front","content_type":"image/jpeg","ext":"jpg"}, ...]')
    content_type: str = Field("image/jpeg")

class PresignResponseItem(BaseModel):
    key: str
    upload_url: str
    expires_in: int

class PresignResponse(BaseModel):
    verification_id: UUID
    uploads: dict[str, PresignResponseItem]

class UploadItem(BaseModel):
    key: str
    upload_url: str
    required_headers: Dict[str, str]
    expires_in: int

class CompleteRequest(BaseModel):
    submission_id: str
    files: List[dict]

class VerifyFileSpec(BaseModel):
    kind: Literal["front","back","selfie"]
    ext: Literal["jpg","jpeg","png","webp"]

class VerifyRequest(BaseModel):
    verification_id: str
    files: List[VerifyFileSpec]