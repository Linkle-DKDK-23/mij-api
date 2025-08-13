# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    class Config:
        from_attributes = True
