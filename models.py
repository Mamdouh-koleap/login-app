from pydantic import BaseModel, EmailStr
from typing import List, Optional
from bson import ObjectId

# class EmailSettings(BaseModel):
#     MAIL_USERNAME: str
#     MAIL_PASSWORD: str
#     MAIL_FROM: str
#     MAIL_PORT: int
#     MAIL_SERVER: str
#     MAIL_TLS: bool
#     MAIL_SSL: bool
#     USE_CREDENTIALS: bool


class Account(BaseModel):
    id: int
    Name: str


class User(BaseModel):
    _id: ObjectId
    UserName: str
    Email: EmailStr
    Password: str
    Accounts: List[Account] = []


class Token(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    UserName: Optional[str]
    Email: Optional[EmailStr]
    Password: Optional[str]
    Accounts: Optional[List[Account]]