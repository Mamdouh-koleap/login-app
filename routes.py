from bson import ObjectId
from fastapi import FastAPI, HTTPException, Body, APIRouter
from pymongo import ReturnDocument
from config import TOKEN_BLACKLIST
from models import User, UserUpdate, Token
from database import users_collection
from utils import create_access_token, pwd_context
import requests
from fastapi import Request
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/register/", response_model=Token)
async def register(user: User):
    # Check if the user already exists
    if users_collection.find_one({"Email": user.Email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.Password)
    user.Password = hashed_password
    user_dict = user.dict()
    users_collection.insert_one(user_dict)

    token_data = {"sub": user.Email}
    access_token = create_access_token(data=token_data)
    # verification_link = f"http://yourdomain.com/verify/?token={access_token}"
    #
    # message = MessageSchema(
    #     subject="Please verify your email",
    #     recipients=[user.Email],  # List of recipients, as many as you can pass
    #     body=f"Click the link to verify your registration: {verification_link}",
    #     subtype="html"
    # )
    # fm = FastMail(conf)
    # await fm.send_message(message)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Fetch the user from the database
    user = users_collection.find_one({"Email": form_data.username})

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Verify password
    if not pwd_context.verify(form_data.password, user['Password']):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token_data = {"sub": form_data.username}
    access_token = create_access_token(data=token_data)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout/")
async def logout(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        TOKEN_BLACKLIST.add(token)
    return {"detail": "Successfully logged out"}

# uncoment this code to verify
# @app.get("/verify/")
# async def verify(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email = payload.get("sub")
#         if not email:
#             raise HTTPException(status_code=400, detail="Invalid token")
#
#         # Here you can set a field in the user's document like `is_verified` to True.
#         user = client['XDec']['User'].find_one({"Email": email})
#         if not user:
#             raise HTTPException(status_code=400, detail="User not found")
#         # Set user as verified etc.
#     except PyJWTError:
#         raise HTTPException(status_code=400, detail="Invalid token")
#
#     return {"status": "successfully verified"}


# get all users

@router.get("/", response_model=list[User])
def get_users():
    try:
        users = users_collection.find()
        return list(users)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []


# create user
# The code will return the newly created user with its new ObjectI
@router.post("/user", response_model=User)
def create_user(user: User):
    try:
        # Convert the Pydantic model instance to a dictionary and insert into MongoDB
        user_id = users_collection.insert_one(user.dict()).inserted_id

        # Attach the new ObjectId to the user model instance before returning
        user._id = user_id

        return user

    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail="Error creating user")


@router.put("/user/{user_id}", response_model=User)
def update_user(user_id: str, user_update: UserUpdate = Body(...)):
    # Convert the update model to a dictionary
    update_data = user_update.dict(exclude_unset=True)

    # Convert the user_id string to ObjectId
    try:
        oid = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    try:
        # Find and update the user
        result = users_collection.find_one_and_update(
            {"_id": oid},  # Using ObjectId for _id
            {"$set": update_data},
            return_document=ReturnDocument.AFTER  # Return the updated document
        )

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        return result

    except Exception as e:
        error_message = f"Error updating user: {e}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)


@router.delete("/user/{user_id}")
def delete_user(user_id: str):
    # Convert the user_id string to ObjectId
    try:
        oid = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    try:
        # Delete the user
        result = users_collection.delete_one({"_id": oid})

        # Check if a user was actually deleted
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"status": "success", "message": "User deleted successfully"}

    except Exception as e:
        error_message = f"Error deleting user: {e}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)
