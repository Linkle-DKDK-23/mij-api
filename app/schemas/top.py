from pydantic import BaseModel
from typing import List, Optional

class GenreResponse(BaseModel):
    id: str
    name: str
    post_count: int

class RankingPostResponse(BaseModel):
    id: str
    description: str
    thumbnail_url: Optional[str] = None
    likes_count: int
    creator_name: str
    creator_avatar_url: Optional[str] = None
    rank: int

class CreatorResponse(BaseModel):
    id: str
    name: str
    avatar_url: Optional[str] = None
    followers_count: int
    rank: Optional[int] = None

class RecentPostResponse(BaseModel):
    id: str
    description: str
    thumbnail_url: Optional[str] = None
    creator_name: str
    creator_avatar_url: Optional[str] = None

class TopPageResponse(BaseModel):
    genres: List[GenreResponse]
    ranking_posts: List[RankingPostResponse]
    top_creators: List[CreatorResponse]
    new_creators: List[CreatorResponse]
    recent_posts: List[RecentPostResponse]
