import requests
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from bson import ObjectId
from pymongo import MongoClient, ReturnDocument
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from routes import get_users
from routes import router as application


# class EmailSettings(BaseModel):
#     MAIL_USERNAME: str
#     MAIL_PASSWORD: str
#     MAIL_FROM: str
#     MAIL_PORT: int
#     MAIL_SERVER: str
#     MAIL_TLS: bool
#     MAIL_SSL: bool
#     USE_CREDENTIALS: bool
#
#
# email_settings = EmailSettings(
#     MAIL_USERNAME="mamdouh.koleap@gmail.com",
#     MAIL_PASSWORD="1234567",
#     MAIL_FROM="mamdouh.koleap@gmail.com",
#     MAIL_PORT=587,
#     MAIL_SERVER="smtp.gmail.com",
#     MAIL_TLS=True,
#     MAIL_SSL=False,
#     USE_CREDENTIALS=True
# )


# class Account(BaseModel):
#     id: int
#     Name: str
#
#
# class User(BaseModel):
#     _id: ObjectId
#     UserName: str
#     Email: EmailStr
#     Password: str
#     Accounts: Optional[List[Account]]
#
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
#
# class UserUpdate(BaseModel):
#     UserName: Optional[str]
#     Email: Optional[EmailStr]
#     Password: Optional[str]
#     Accounts: Optional[List[Account]]


app = FastAPI()
app.include_router(application)


# @app.get("//")
# def read_root():
#     return {"Hello": "World"}
# client = MongoClient('mongodb://localhost:27017/')
#
# SECRET_KEY = "your_super_secret_key"  # Typically a long random string
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
#
#
# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# # conf = ConnectionConfig(
# #     MAIL_USERNAME=email_settings.MAIL_USERNAME,
# #     MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
# #     MAIL_FROM=email_settings.MAIL_FROM,
# #     MAIL_PORT=email_settings.MAIL_PORT,
# #     MAIL_SERVER=email_settings.MAIL_SERVER,
# #     MAIL_TLS=email_settings.MAIL_TLS,
# #     MAIL_SSL=email_settings.MAIL_SSL,
# #     USE_CREDENTIALS=email_settings.USE_CREDENTIALS
# # )
#
#
# @app.post("/register/", response_model=Token)
# async def register(user: User):
#     # Check if the user already exists
#     if client['XDec']['User'].find_one({"Email": user.Email}):
#         raise HTTPException(status_code=400, detail="Email already registered")
#
#     hashed_password = pwd_context.hash(user.Password)
#     user.Password = hashed_password
#     user_dict = user.dict()
#     client['XDec']['User'].insert_one(user_dict)
#
#     token_data = {"sub": user.Email}
#     access_token = create_access_token(data=token_data)
#     # verification_link = f"http://yourdomain.com/verify/?token={access_token}"
#     #
#     # message = MessageSchema(
#     #     subject="Please verify your email",
#     #     recipients=[user.Email],  # List of recipients, as many as you can pass
#     #     body=f"Click the link to verify your registration: {verification_link}",
#     #     subtype="html"
#     # )
#     # fm = FastMail(conf)
#     # await fm.send_message(message)
#     return {"access_token": access_token, "token_type": "bearer"}
#
# # uncoment this code to verify
# # @app.get("/verify/")
# # async def verify(token: str):
# #     try:
# #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# #         email = payload.get("sub")
# #         if not email:
# #             raise HTTPException(status_code=400, detail="Invalid token")
# #
# #         # Here you can set a field in the user's document like `is_verified` to True.
# #         user = client['XDec']['User'].find_one({"Email": email})
# #         if not user:
# #             raise HTTPException(status_code=400, detail="User not found")
# #         # Set user as verified etc.
# #     except PyJWTError:
# #         raise HTTPException(status_code=400, detail="Invalid token")
# #
# #     return {"status": "successfully verified"}
#
#
# # get all users
#
# @app.get("/", response_model=list[User])
# def get_users():
#     try:
#         users = client['XDec']['User'].find()
#         return list(users)
#     except Exception as e:
#         print(f"Error fetching users: {e}")
#         return []
#
#
# # create user
# # The code will return the newly created user with its new ObjectI
# @app.post("/user", response_model=User)
# def create_user(user: User):
#     try:
#         # Convert the Pydantic model instance to a dictionary and insert into MongoDB
#         user_id = client['XDec']['User'].insert_one(user.dict()).inserted_id
#
#         # Attach the new ObjectId to the user model instance before returning
#         user._id = user_id
#
#         return user
#
#     except Exception as e:
#         print(f"Error creating user: {e}")
#         raise HTTPException(status_code=400, detail="Error creating user")
#
#
# @app.put("/user/{user_id}", response_model=User)
# def update_user(user_id: str, user_update: UserUpdate = Body(...)):
#     # Convert the update model to a dictionary
#     update_data = user_update.dict(exclude_unset=True)
#
#     # Convert the user_id string to ObjectId
#     try:
#         oid = ObjectId(user_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid user_id format")
#
#     try:
#         # Find and update the user
#         result = client['XDec']['User'].find_one_and_update(
#             {"_id": oid},  # Using ObjectId for _id
#             {"$set": update_data},
#             return_document=ReturnDocument.AFTER  # Return the updated document
#         )
#
#         if not result:
#             raise HTTPException(status_code=404, detail="User not found")
#
#         return result
#
#     except Exception as e:
#         error_message = f"Error updating user: {e}"
#         print(error_message)
#         raise HTTPException(status_code=500, detail=error_message)
#
#
# @app.delete("/user/{user_id}")
# def delete_user(user_id: str):
#     # Convert the user_id string to ObjectId
#     try:
#         oid = ObjectId(user_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid user_id format")
#
#     try:
#         # Delete the user
#         result = client['XDec']['User'].delete_one({"_id": oid})
#
#         # Check if a user was actually deleted
#         if result.deleted_count == 0:
#             raise HTTPException(status_code=404, detail="User not found")
#
#         return {"status": "success", "message": "User deleted successfully"}
#
#     except Exception as e:
#         error_message = f"Error deleting user: {e}"
#         print(error_message)
#         raise HTTPException(status_code=500, detail=error_message)


# Example usage:
users = get_users()
print(users)


# @app.get("/details")
# def Account_Details():
#      url = "https://chat.xdec.io/platform/api/v1/accounts/2"
#
#      headers = {
#          'api_access_token': '8K8MBsNXQZ6QJSTwt9pGr4Fk',
#          'Content-Type': 'application/json; charset=utf-8'
#      }
#      response = requests.request("get", url, headers=headers)
#
#      details = response.json()
#      return details
