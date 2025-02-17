from urllib import request
from fastapi import APIRouter

from users.views import register_view

router = APIRouter()

@router.get("/users")
def list_users():
    register_view(request)
    return {"message": "List of users"}

@router.post("/users")
def create_user():
    return {"message": "User created"}
