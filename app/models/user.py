from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class Gender(str, Enum):
    FEMALE = "FEMALE"
    MALE = "MALE"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    gender: Optional[Gender] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_verified: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
