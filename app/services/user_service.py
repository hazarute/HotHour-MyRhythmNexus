from app.core.db import db
from app.models.user import UserCreate
from app.core import security

class UserService:
    async def create_user(self, user_in: UserCreate):
        hashed_password = security.get_password_hash(user_in.password)
        user = await db.user.create(
            data={
                "email": user_in.email,
                "hashedPassword": hashed_password,
                "fullName": user_in.full_name,
                "phone": user_in.phone,
                "gender": user_in.gender,
            }
        )
        return user

    async def get_user_by_email(self, email: str):
        return await db.user.find_unique(where={"email": email})
    
    async def get_user_by_phone(self, phone: str):
        return await db.user.find_unique(where={"phone": phone})

    async def verify_user(self, email: str):
        return await db.user.update(
            where={"email": email},
            data={"isVerified": True}
        )
            
user_service = UserService()
