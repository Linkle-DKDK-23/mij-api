from pydantic import BaseModel


class VerifyIn(BaseModel):
    token: str