"""
User models for HotHour authentication and registration.
Aligned with Prisma schema: prisma/schema.prisma

Field mappings:
- fullName (Prisma) ↔ full_name (Pydantic)
- isVerified (Prisma) ↔ is_verified (Pydantic)
- createdAt (Prisma) ↔ created_at (Pydantic)
- hashedPassword (Prisma) ↔ hashed_password (Pydantic)
"""

from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum
from datetime import datetime
import re


# ============================================================================
# ENUMS (aligned with prisma/schema.prisma)
# ============================================================================

class Gender(str, Enum):
    """User gender enum from Prisma schema"""
    FEMALE = "FEMALE"
    MALE = "MALE"


class Role(str, Enum):
    """User role enum from Prisma schema"""
    USER = "USER"
    ADMIN = "ADMIN"


# ============================================================================
# REQUEST MODELS (what client sends)
# ============================================================================

class UserCreate(BaseModel):
    """
    Schema for user registration.
    Validates all fields before creating user in database.
    
    Fields:
    - email: Valid email address (must be unique)
    - full_name: User's full name (3+ chars, letters only)
    - phone: Valid phone number (10+ digits)
    - gender: FEMALE or MALE
    - password: At least 8 characters
    """
    email: EmailStr
    full_name: str
    phone: str
    gender: Gender
    password: str

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """
        Validate full name:
        - Min 3 characters
        - Only letters (Latin + Turkish: ç, ğ, ı, ö, ş, ü)
        - Spaces and hyphens allowed
        
        Args:
            v: Full name string
            
        Returns:
            Trimmed and validated full name
            
        Raises:
            ValueError: If validation fails
        """
        if not v or len(v.strip()) < 3:
            raise ValueError('Ad Soyadı en az 3 karakter olmalıdır')
        
        # Allow: Latin letters, Turkish letters, spaces, hyphens
        if not re.match(r'^[a-zA-ZçğıöşüÇĞİÖŞÜ\s\-]+$', v):
            raise ValueError('Ad Soyadı sadece harfler, boşluk ve tire içerebilir')
        
        return v.strip()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """
        Validate phone number:
        - Min 10 digits (after removing non-digit chars)
        - Accepts: +, -, (, ), spaces, dots
        
        Args:
            v: Phone string
            
        Returns:
            Trimmed phone string
            
        Raises:
            ValueError: If phone is invalid
        """
        if not v:
            raise ValueError('Telefon zorunludur')
        
        # Extract only digits
        digits = re.sub(r'\D', '', v)
        
        if len(digits) < 10:
            raise ValueError('Telefon en az 10 rakam olmalıdır')
        
        return v.strip()

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: Gender) -> Gender:
        """
        Validate gender enum.
        Pydantic auto-validates enums, but explicit validation for clarity.
        
        Args:
            v: Gender enum
            
        Returns:
            Validated gender
            
        Raises:
            ValueError: If gender is not FEMALE or MALE
        """
        if v not in [Gender.FEMALE, Gender.MALE]:
            raise ValueError('Cinsiyet FEMALE veya MALE olmalıdır')
        
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password:
        - Min 8 characters
        
        Args:
            v: Password string
            
        Returns:
            Validated password
            
        Raises:
            ValueError: If password is too short
        """
        if not v or len(v) < 8:
            raise ValueError('Şifre en az 8 karakter olmalıdır')
        
        return v


class UserLogin(BaseModel):
    """User login credentials"""
    email: EmailStr
    password: str


class UserPasswordUpdate(BaseModel):
    """
    Schema for password update requests.
    """
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or len(v) < 8:
            raise ValueError('Yeni şifre en az 8 karakter olmalıdır')
        return v


# ============================================================================
# RESPONSE MODELS (what API returns)
# ============================================================================

class UserResponse(BaseModel):
    """
    User response model.
    Maps Prisma snake_case fields to camelCase.
    Does NOT include password or hashedPassword for security.
    
    Used for user profile endpoints and token responses.
    """
    id: int
    email: str
    full_name: str  # fullName (Prisma) → full_name (Pydantic)
    phone: str
    gender: Gender
    role: Role
    is_verified: bool  # isVerified (Prisma) → is_verified (Pydantic)
    created_at: datetime  # createdAt (Prisma) → created_at (Pydantic)

    class Config:
        from_attributes = True  # Enable mapping from Prisma ORM objects


class UserPublicProfile(BaseModel):
    """
    Public user profile (minimal data).
    Used when displaying user info to other users (e.g., in reservations list).
    Does NOT expose email or phone for privacy.
    """
    id: int
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# INTERNAL MODELS (for backend operations - DO NOT EXPOSE VIA API)
# ============================================================================

class UserInDB(BaseModel):
    """
    Internal model representing user in database.
    Includes sensitive fields (only for backend use, NEVER return via API).
    """
    id: int
    email: str
    full_name: str
    phone: str
    gender: Gender
    hashed_password: str  # hashedPassword (Prisma) → hashed_password
    role: Role
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AUTHENTICATION & TOKEN
# ============================================================================

class Token(BaseModel):
    """JWT Token response after successful login/registration"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse  # Include user data with token


class TokenData(BaseModel):
    """Data extracted and validated from JWT token"""
    user_id: int
    email: str
