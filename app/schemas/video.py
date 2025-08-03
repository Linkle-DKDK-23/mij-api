from pydantic import BaseModel

class UploadFile(BaseModel):
    filename: str
    content_type: str