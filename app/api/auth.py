from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import UserCreate, UserResponse, UserLogin, Token
from app.services.user_service import user_service
from app.core import security
from app.core.deps import get_current_user
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    """
    User registration endpoint.
    
    Validates input, checks for duplicates, creates user, and returns JWT token.
    
    Args:
        user_in: UserCreate model with email, phone, full_name, gender, password
        
    Returns:
        Token: access_token, token_type, and user data
        
    Raises:
        HTTPException 400: If email/phone already exists or validation fails
    """
    # Check for existing email
    existing_user = await user_service.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi ile zaten bir hesap var"
        )
    
    # Check for existing phone
    existing_phone = await user_service.get_user_by_phone(user_in.phone)
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu telefon numarası ile zaten bir hesap var"
        )
    
    try:
        # Create user in database
        user = await user_service.create_user(user_in)
        
        # Generate JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        
        # Build user response with Prisma->Pydantic field mappings
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.fullName,
            phone=user.phone,
            gender=user.gender,
            role=user.role,
            is_verified=user.isVerified,
            created_at=user.createdAt,
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response,
        }
    except Exception as e:
        # Catch database constraint violations, validation errors, etc.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kayıt sırasında bir hata oluştu. Lütfen bilgilerinizi kontrol edin."
        )

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    """
    User login endpoint.
    
    Authenticates user with email and password, returns JWT token.
    
    Args:
        user_in: UserLogin model with email and password
        
    Returns:
        Token: access_token, token_type, and user data
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Verify user exists and password is correct
    user = await user_service.get_user_by_email(user_in.email)
    if not user or not security.verify_password(user_in.password, user.hashedPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # Build user response with Prisma->Pydantic field mappings
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.fullName,
        phone=user.phone,
        gender=user.gender,
        role=user.role,
        is_verified=user.isVerified,
        created_at=user.createdAt,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response,
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user=Depends(get_current_user)):
    """
    Get current user profile.
    
    Returns the authenticated user's profile information.
    
    Args:
        current_user: Injected current user from JWT token
        
    Returns:
        UserResponse: Full user profile with all public data
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.fullName,
        phone=current_user.phone,
        gender=current_user.gender,
        role=current_user.role,
        is_verified=current_user.isVerified,
        created_at=current_user.createdAt,
    )
