from pydantic import BaseModel

class UploadFile(BaseModel):
    filename: str
    content_type: str

class UploadRequest(BaseModel):
    filename: str
    content_type: str

class PlayRequest(BaseModel):
    video_id: str
    user_id: str


class CreateUploadReq(BaseModel):
    filename: str
    content_type: str