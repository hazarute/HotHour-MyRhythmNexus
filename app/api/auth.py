from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from app.models.user import UserCreate, UserResponse, UserLogin, Token
from app.services.user_service import user_service
from app.core import security
from app.core.deps import get_current_user
from app.core.email import send_verification_email
from datetime import timedelta
from app.core.config import settings
from app.core.timezone import now_tr

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, background_tasks: BackgroundTasks):
    """
    User registration endpoint.
    
    Validates input, checks for duplicates, creates user, and returns JWT token.
    Sends verification email in background.
    
    Args:
        user_in: UserCreate model with email, phone, full_name, gender, password
        background_tasks: FastAPI BackgroundTasks
        
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
        # Create user in database (isVerified defaults to False)
        # Note: Prisma schema sets isVerified default to false
        user = await user_service.create_user(user_in)
        
        # Determine verification status (if manually set or forced)
        # Assuming database default is False, so user.isVerified is False
        
        # Update user to be unverified if needed, but create_user should handle it
        # Send verification email
        is_verified = getattr(user, 'is_verified', getattr(user, 'isVerified', False))
        if not is_verified:
            verification_token = security.create_verification_token(user.email)
            background_tasks.add_task(send_verification_email, user.email, verification_token)
        
        # Generate Access Token (so user is logged in immediately)
        # They can access the site but might be restricted on some features until verified
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        
        # Build user response with Prisma->Pydantic field mappings
        # Note: Prisma Client Python converts schema fields (camelCase) to snake_case attributes
        user_response = UserResponse(
            id=user.id,
            email=getattr(user, 'email', ''),
            full_name=getattr(user, 'full_name', getattr(user, 'fullName', '')),
            phone=getattr(user, 'phone', ''),
            gender=getattr(user, 'gender', 'FEMALE'),  # Default if missing
            role=getattr(user, 'role', 'USER'),
            is_verified=getattr(user, 'is_verified', getattr(user, 'isVerified', False)),
            created_at=getattr(user, 'created_at', getattr(user, 'createdAt', now_tr())),
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response,
        }
    except Exception as e:
        # Catch database constraint violations, validation errors, etc.
        # Log the error for debugging
        print(f"Registration error attributes: {dir(user)}")
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kayıt sırasında bir hata oluştu. Lütfen bilgilerinizi kontrol edin."
        )

@router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(token: str):
    """
    Verify email address using the token sent via email.
    """
    payload = security.decode_token(token)
    if not payload or payload.get("type") != "verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz veya süresi dolmuş doğrulama linki"
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz token içeriği"
        )
        
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
        
    is_verified = getattr(user, 'is_verified', getattr(user, 'isVerified', False))
    if is_verified:
        return {"message": "Email adresi zaten doğrulanmış"}
        
    await user_service.verify_user(email)
    
    return {"message": "Email adresi başarıyla doğrulandı"}

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
    hashed_password = getattr(user, 'hashed_password', getattr(user, 'hashedPassword', ''))
    if not user or not security.verify_password(user_in.password, hashed_password):
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
        email=getattr(user, 'email', ''),
        full_name=getattr(user, 'full_name', getattr(user, 'fullName', '')),
        phone=getattr(user, 'phone', ''),
        gender=getattr(user, 'gender', 'FEMALE'),
        role=getattr(user, 'role', 'USER'),
        is_verified=getattr(user, 'is_verified', getattr(user, 'isVerified', False)),
        created_at=getattr(user, 'created_at', getattr(user, 'createdAt', now_tr())),
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
        email=getattr(current_user, 'email', ''),
        full_name=getattr(current_user, 'full_name', getattr(current_user, 'fullName', '')),
        phone=getattr(current_user, 'phone', ''),
        gender=getattr(current_user, 'gender', 'FEMALE'),
        role=getattr(current_user, 'role', 'USER'),
        is_verified=getattr(current_user, 'is_verified', getattr(current_user, 'isVerified', False)),
        created_at=getattr(current_user, 'created_at', getattr(current_user, 'createdAt', now_tr())),
    )
