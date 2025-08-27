from pydantic import BaseModel
from uuid import UUID

class CategoryOut(BaseModel):
    id: UUID
    slug: str
    name: str
    genre_id: UUID

class GenreOut(BaseModel):
    id: UUID
    slug: str
    name: str
