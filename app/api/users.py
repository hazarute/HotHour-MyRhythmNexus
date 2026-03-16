from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from app.core import security
from app.core.deps import get_current_admin_user
from app.core.db import db
from app.core.email import send_verification_email
from app.models.enums import Gender, Role
from app.services.user_service import user_service

router = APIRouter()

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str
    phone: str
    gender: Gender


def _serialize_user(user):
    u_dict = user.model_dump() if hasattr(user, "model_dump") else user.dict() if hasattr(user, "dict") else dict(user)
    u_dict.pop("hashedPassword", None)
    return u_dict

@router.get("")
async def get_all_users(current_admin = Depends(get_current_admin_user)):
    try:
        users = await db.user.find_many(
            order={"createdAt": "desc"},
            include={"studio": True}
        )
        return [_serialize_user(user) for user in users]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kullanıcılar getirilirken hata oluştu: {str(e)}"
        )

@router.put("/{user_id}")
async def update_user(user_id: int, user_in: UserUpdate, current_admin = Depends(get_current_admin_user)):
    try:
        existing_user = await db.user.find_unique(where={"id": user_id})
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

        target_role = getattr(existing_user, "role", None)
        target_id = getattr(existing_user, "id", None)
        if target_role == Role.ADMIN.value and target_id != current_admin.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Diğer admin kullanıcıların bilgileri düzenlenemez."
            )

        updated_user = await db.user.update(
            where={"id": user_id},
            data={
                "fullName": user_in.full_name,
                "phone": user_in.phone,
                "gender": user_in.gender
            },
            include={"studio": True}
        )
        return _serialize_user(updated_user)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Kullanıcı güncellenemedi: {str(e)}"
        )

@router.delete("/{user_id}")
async def delete_user(user_id: int, current_admin = Depends(get_current_admin_user)):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Kullanıcı silme işlemi desteklenmiyor."
    )


@router.post("/{user_id}/resend-verification")
async def resend_verification_email_to_user(
    user_id: int,
    background_tasks: BackgroundTasks,
    current_admin = Depends(get_current_admin_user),
):
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

    if getattr(user, "role", None) == Role.ADMIN.value and getattr(user, "id", None) != current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Diğer admin kullanıcılar için doğrulama işlemi yapılamaz."
        )

    is_verified = getattr(user, "is_verified", getattr(user, "isVerified", False))
    if is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcının e-posta adresi zaten doğrulanmış."
        )

    email = getattr(user, "email", None)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kullanıcının e-posta adresi bulunamadı."
        )

    verification_token = security.create_verification_token(email)
    background_tasks.add_task(send_verification_email, email, verification_token)
    return {"detail": "Doğrulama e-postası yeniden gönderildi."}


@router.post("/{user_id}/reset-password")
async def reset_user_password(user_id: int, current_admin = Depends(get_current_admin_user)):
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

    if getattr(user, "role", None) == Role.ADMIN.value and getattr(user, "id", None) != current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Diğer admin kullanıcıların şifresi sıfırlanamaz."
        )

    await user_service.update_password(user_id, "sifredegistir")
    return {"detail": "Kullanıcı şifresi varsayılan değere sıfırlandı."}
