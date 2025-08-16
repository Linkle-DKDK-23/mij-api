from pydantic import BaseModel
from typing import List

class GenderOut(BaseModel):
    slug: str
    name: str

class GenderCreate(BaseModel):
    name: str

class GenderIDList(BaseModel):
    id: List[str]

class GenderSlugList(BaseModel):
    slug: List[str]