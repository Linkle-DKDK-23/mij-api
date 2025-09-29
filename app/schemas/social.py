from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=1000)
    parent_comment_id: Optional[UUID] = None

class CommentUpdate(BaseModel):
    body: str = Field(..., min_length=1, max_length=1000)

class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    user_id: UUID
    parent_comment_id: Optional[UUID]
    body: str
    created_at: datetime
    updated_at: datetime
    user_username: str
    user_avatar: Optional[str] = None

    class Config:
        from_attributes = True

class FollowResponse(BaseModel):
    follower_user_id: UUID
    creator_user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class LikeResponse(BaseModel):
    user_id: UUID
    post_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class BookmarkResponse(BaseModel):
    user_id: UUID
    post_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class UserBasicResponse(BaseModel):
    id: UUID
    username: str
    profile_name: str
    avatar_storage_key: Optional[str] = None

    class Config:
        from_attributes = True

class FollowStatsResponse(BaseModel):
    followers_count: int
    following_count: int

class SocialStatsResponse(BaseModel):
    likes_count: int
    comments_count: int
    bookmarks_count: int
    is_liked: bool = False
    is_bookmarked: bool = False
    is_following: bool = False