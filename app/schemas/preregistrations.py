from pydantic import BaseModel

class PreregistrationCreateRequest(BaseModel):
    name: str
    email: str
    x_name: str