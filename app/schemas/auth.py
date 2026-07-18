from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str] = None

    class Config:
        from_attributes = True
