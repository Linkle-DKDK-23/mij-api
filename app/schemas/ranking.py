from pydantic import BaseModel 
from typing import Optional, List

class RankingPostsAllTimeResponse(BaseModel):
    id: str
    description: str
    thumbnail_url: Optional[str] = None
    likes_count: int
    creator_name: str
    username: str
    creator_avatar_url: Optional[str] = None
    rank: int

class RankingPostsMonthlyResponse(BaseModel):
    id: str
    description: str
    thumbnail_url: Optional[str] = None
    likes_count: int
    creator_name: str
    username: str
    creator_avatar_url: Optional[str] = None
    rank: int

class RankingPostsWeeklyResponse(BaseModel):
    id: str
    description: str
    thumbnail_url: Optional[str] = None
    likes_count: int
    creator_name: str
    username: str
    creator_avatar_url: Optional[str] = None
    rank: int

class RankingPostsDailyResponse(BaseModel):
    id: str
    description: str
    thumbnail_url: Optional[str] = None
    likes_count: int
    creator_name: str
    username: str
    creator_avatar_url: Optional[str] = None
    rank: int

class RankingResponse(BaseModel):
    all_time: List[RankingPostsAllTimeResponse]
    monthly: List[RankingPostsMonthlyResponse]
    weekly: List[RankingPostsWeeklyResponse]
    daily: List[RankingPostsDailyResponse]