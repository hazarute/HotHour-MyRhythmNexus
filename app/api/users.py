from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.deps import get_current_admin_user
from app.core.db import db

router = APIRouter()

class UserUpdate(BaseModel):
    full_name: str
    email: str
    phone: str
    role: str
    gender: str

@router.get("/")
async def get_all_users(current_admin = Depends(get_current_admin_user)):
    try:
        users = await db.user.find_many(
            order={"createdAt": "desc"}
        )
        # Omit hashed password
        result = []
        for u in users:
            u_dict = u.model_dump()
            u_dict.pop("hashedPassword", None)
            result.append(u_dict)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kullanıcılar getirilirken hata oluştu: {str(e)}"
        )

@router.put("/{user_id}")
async def update_user(user_id: int, user_in: UserUpdate, current_admin = Depends(get_current_admin_user)):
    try:
        updated_user = await db.user.update(
            where={"id": user_id},
            data={
                "fullName": user_in.full_name,
                "email": user_in.email,
                "phone": user_in.phone,
                "role": user_in.role,
                "gender": user_in.gender
            }
        )
        u_dict = updated_user.model_dump()
        u_dict.pop("hashedPassword", None)
        return u_dict
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Kullanıcı güncellenemedi: {str(e)}"
        )

@router.delete("/{user_id}")
async def delete_user(user_id: int, current_admin = Depends(get_current_admin_user)):
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendinizi silemezsiniz."
        )
    
    try:
        # Check if user exists
        user = await db.user.find_unique(where={"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

        await db.user.delete(where={"id": user_id})
        return {"detail": "Kullanıcı başarıyla silindi"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Kullanıcı silinemedi. (Rezervasyonları olabilir): {str(e)}"
        )
