import jwt
from datetime import datetime as d, timezone, timedelta
from fastapi import APIRouter, Request, Depends, HTTPException, Security
from pydantic import BaseModel
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from django.contrib.auth import authenticate, login, logout
from starlette.responses import JSONResponse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from django.conf import settings

router = APIRouter()
User = get_user_model()  # This ensures Django uses the correct user model

security = HTTPBearer()


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

# Pydantic models for request validation
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

def create_jwt_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": d.now(tz=timezone.utc) + timedelta(minutes=30),
        "iat": d.now(tz=timezone.utc),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# ✅ User Registration
@router.post("/users/register", status_code=201)
def register_user(request_data: RegisterRequest):
    """
    Register a new user.
    """
    if User.objects.filter(username=request_data.username).exists():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    user = User.objects.create_user(
        username=request_data.username,
        email=request_data.email,
        password=request_data.password
    )
    return JSONResponse(content={"message": "User registered successfully"}, status_code=201)


# ✅ User Login (Session Creation)
@router.post("/users/login")
def login_user(request: Request, request_data: LoginRequest):
    """
    Authenticate user and create a session.
    """
    user = authenticate(username=request_data.username, password=request_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_jwt_token(user.id)
    return JSONResponse(content={"access_token": token, "token_tyoe": "bearer"}, status_code=200)

# user authentication middleware
def get_current_user(token: HTTPAuthorizationCredentials = Security(security),
):
    if not token:
        raise HTTPException(status_code=403, detail="Token missing")
    
    credentials_exception = HTTPException(status_code=403, detail="Invalid token")

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user = User.objects.get(id=payload["user_id"])
        return user
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        raise credentials_exception


# ✅ User Logout (Session Destruction)
@router.post("/users/logout")
def logout_user(request: Request):
    """
    Logout user and destroy session.
    """
    logout(request)  # Destroy session
    return JSONResponse(content={"message": "Logout successful"}, status_code=200)


# ✅ Check Session Status
@router.get("/users/session")
def check_session_status(request: Request):
    """
    Check if a user is authenticated (session exists).
    """
    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    return JSONResponse(content={"message": "Session is active", "user": request.user.username}, status_code=200)

@router.get("/users/me")
def get_user_profile(user: User=Depends(get_current_user)):
    return JSONResponse(content={"username": user.username, "email": user.email})