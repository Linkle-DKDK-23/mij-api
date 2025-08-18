from pydantic import BaseModel, Field
from typing import Dict, List, Literal


class UploadItem(BaseModel):
    key: str
    upload_url: str
    required_headers: Dict[str, str]
    expires_in: int

class PresignResponseItem(BaseModel):
    key: str
    upload_url: str
    expires_in: int
    required_headers: Dict[str, str]
