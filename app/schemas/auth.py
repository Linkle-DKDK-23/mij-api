# app/schemas/auth.py
from pydantic import BaseModel, EmailStr

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginCookieOut(BaseModel):
    message: str
    csrf_token: str
