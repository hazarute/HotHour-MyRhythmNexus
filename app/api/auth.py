from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import UserCreate, UserResponse, UserLogin, Token
from app.services.user_service import user_service
from app.core import security
from app.core.deps import get_current_user
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    existing_user = await user_service.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    user = await user_service.create_user(user_in)
    # Map Prisma model attributes to Pydantic response fields
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.fullName,
        "phone": user.phone,
        "role": user.role,
        "is_verified": user.isVerified,
    }

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    user = await user_service.get_user_by_email(user_in.email)
    if not user or not security.verify_password(user_in.password, user.hashedPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.fullName,
        "phone": current_user.phone,
        "role": current_user.role,
        "is_verified": current_user.isVerified,
    }
