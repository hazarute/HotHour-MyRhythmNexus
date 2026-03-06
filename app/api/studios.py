from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from uuid import uuid4
from app.core.deps import get_current_admin_user
from app.models.studio import StudioResponse, StudioUpdate
from app.services.studio_service import studio_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me", response_model=StudioResponse)
async def get_my_studio(request: Request, current_admin = Depends(get_current_admin_user)):
    """
    Get the studio details for the currently logged-in admin.
    """
    if not current_admin.studioId:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Size bağlı bir stüdyo bulunamadı."
        )
    
    try:
        studio = await studio_service.get_studio_by_id(current_admin.studioId)
        if not studio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stüdyo veritabanında bulunamadı."
            )
        
        # Ensure logoUrl is absolute when it is a relative uploads path
        try:
            if getattr(studio, 'logoUrl', None) and str(studio.logoUrl).startswith('/uploads/'):
                base = str(request.base_url).rstrip('/')
                studio.logoUrl = f"{base}{studio.logoUrl}"
        except Exception:
            # If transformation fails, return studio as-is
            pass

        return studio
    except Exception as e:
        logger.error(f"Error fetching studio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stüdyo bilgileri getirilirken hata oluştu."
        )

@router.put("/me", response_model=StudioResponse)
async def update_my_studio(request: Request, studio_in: StudioUpdate, current_admin = Depends(get_current_admin_user)):
    """
    Update the studio details for the currently logged-in admin.
    """
    if not current_admin.studioId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Size bağlı bir stüdyo olmadığı için güncelleme yapamazsınız."
        )
    
    try:
        updated_studio = await studio_service.update_studio(current_admin.studioId, studio_in)

        # Normalize logoUrl to absolute if it's a relative uploads path
        try:
            if getattr(updated_studio, 'logoUrl', None) and str(updated_studio.logoUrl).startswith('/uploads/'):
                base = str(request.base_url).rstrip('/')
                updated_studio.logoUrl = f"{base}{updated_studio.logoUrl}"
        except Exception:
            pass

        return updated_studio
    except Exception as e:
        logger.error(f"Error updating studio: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stüdyo güncellenemedi: {str(e)}"
        )

@router.post("/me/logo", response_model=StudioResponse)
async def upload_studio_logo(
    request: Request,
    file: UploadFile = File(...),
    current_admin=Depends(get_current_admin_user)
):
    """
    Upload a new logo for the studio and update the URL.
    """
    if not current_admin.studioId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Size bağlı bir stüdyo olmadığı için yükleme yapamazsınız."
        )

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lütfen geçerli bir görsel dosyası yükleyin (png, jpeg, vb)."
        )

    try:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.getcwd(), 'uploads', 'studios')
        os.makedirs(upload_dir, exist_ok=True)

        # Generate a unique filename
        ext = file.filename.split('.')[-1]
        unique_filename = f"{current_admin.studioId}_{uuid4().hex[:8]}.{ext}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # The public URL will be /uploads/studios/filename
        # Return an absolute URL so frontends served from other origins can load it directly
        public_path = f"/uploads/studios/{unique_filename}"
        base = str(request.base_url).rstrip('/')
        public_url = f"{base}{public_path}"

        # Update studio with the relative path in DB but return absolute URL in response
        update_data = StudioUpdate(logoUrl=public_path)
        updated_studio = await studio_service.update_studio(current_admin.studioId, update_data)

        try:
            # Attach absolute URL for response
            if getattr(updated_studio, 'logoUrl', None):
                updated_studio.logoUrl = public_url
        except Exception:
            pass

        return updated_studio
    except Exception as e:
        logger.error(f"Error uploading logo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logo yüklenirken hata oluştu: {str(e)}"
        )