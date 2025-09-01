# app/schemas/media_covert.py
from pydantic import BaseModel, Field


class MediaCovertRequest(BaseModel):
    post_id: str

# ====== Pydantic ======
class PreviewRequest(BaseModel):
    asset_id: str
    input_key: str                      # 例: post-media/main/<post>/<uuid>.mp4
    output_key: str                     # 例: preview/<post>/<asset>/preview.mp4
    metadata: dict = Field(default_factory=dict)

class FinalHlsRequest(BaseModel):
    asset_id: str
    input_key: str
    output_prefix: str                  # 例: hls/<post>/<asset>/
    metadata: dict = Field(default_factory=dict)