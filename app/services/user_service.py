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
            }
        )
        return user

    async def get_user_by_email(self, email: str):
        return await db.user.find_unique(where={"email": email})
            
user_service = UserService()
