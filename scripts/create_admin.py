#!/usr/bin/env python3
"""
Admin Hesabı Oluşturma Script
Kullanım: python scripts/create_admin.py <email> <password> <full_name> [phone] [gender] [studio_id]
"""

import sys
import os
from pathlib import Path

# Proje root'u ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from prisma import Prisma
from app.core.security import get_password_hash

# .env dosyasını yükle
load_dotenv()


async def create_admin(
    email: str,
    password: str,
    full_name: str,
    phone: str = None,
    gender: str = None,
    studio_id: int = None,
    prisma_client = None  # Optional: for testing
) -> None:
    """Admin hesabı oluştur"""
    
    # Use provided prisma client or create new one
    if prisma_client is None:
        prisma = Prisma()
        await prisma.connect()
        should_disconnect = True
    else:
        prisma = prisma_client
        should_disconnect = False
    
    try:
        # Email kontrolü
        existing_user = await prisma.user.find_unique(where={"email": email})
        if existing_user:
            print(f"❌ Hata: Email '{email}' zaten kayıtlı !")
            return
        
        # Phone kontrolü
        if phone:
            existing_phone = await prisma.user.find_unique(where={"phone": phone})
            if existing_phone:
                print(f"❌ Hata: Telefon '{phone}' zaten kayıtlı !")
                return
        
        # Şifre hash et
        hashed_password = get_password_hash(password)
        
        # Admin kullanıcı oluştur
        new_admin = await prisma.user.create(
            data={
                "email": email,
                "fullName": full_name,
                "phone": phone or f"admin-{email.split('@')[0]}",  # Fallback phone
                "hashedPassword": hashed_password,
                "role": "ADMIN",
                "isVerified": True,
                "gender": gender if gender in ["MALE", "FEMALE"] else None,
                "studioId": studio_id,
            }
        )
        
        print(f"✅ Admin hesabı başarıyla oluşturuldu !")
        print(f"   ID: {new_admin.id}")
        print(f"   Email: {new_admin.email}")
        print(f"   Ad Soyad: {new_admin.fullName}")
        print(f"   Telefon: {new_admin.phone}")
        print(f"   Role: {new_admin.role}")
        print(f"   Doğrulandı: {new_admin.isVerified}")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
        raise
    finally:
        if should_disconnect:
            await prisma.disconnect()


def main():
    """CLI entry point"""
    
    if len(sys.argv) < 4:
        print("📋 Kullanım:")
        print("   python scripts/create_admin.py <email> <password> <full_name> [phone] [gender] [studio_id]")
        print()
        print("📝 Örnek:")
        print("   python scripts/create_admin.py admin@example.com mypassword123 'Admin Kullanıcı' '+905551234567' MALE 1")
        print()
        print("⚙️  Parametreler:")
        print("   - email: Yöneticinin email adresi (zorunlu)")
        print("   - password: Yöneticinin şifresi (zorunlu)")
        print("   - full_name: Yöneticinin adı soyadı (zorunlu)")
        print("   - phone: Telefon numarası (opsiyonel, varsayılan: admin-[email-prefix])")
        print("   - gender: Cinsiyet - 'MALE' veya 'FEMALE' (opsiyonel)")
        print("   - studio_id: Bağlı olduğu stüdyo ID'si (opsiyonel)")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    full_name = sys.argv[3]
    phone = sys.argv[4] if len(sys.argv) > 4 else None
    gender = sys.argv[5].upper() if len(sys.argv) > 5 else None
    
    studio_id = None
    if len(sys.argv) > 6:
        try:
            studio_id = int(sys.argv[6])
        except ValueError:
            print("❌ Hata: Studio ID sayısal bir değer olmalıdır.")
            sys.exit(1)
    
    # Temel validasyonlar
    if "@" not in email or "." not in email:
        print(f"❌ Hata: Geçerli bir email adresi yazın ! ({email})")
        sys.exit(1)
    
    if len(password) < 6:
        print(f"❌ Hata: Şifre en az 6 karakter olmalıdır !")
        sys.exit(1)
    
    if not full_name.strip():
        print(f"❌ Hata: Ad soyad boş olamaz !")
        sys.exit(1)
    
    if gender and gender not in ["MALE", "FEMALE"]:
        print(f"❌ Hata: Cinsiyet 'MALE' veya 'FEMALE' olmalıdır !")
        sys.exit(1)
    
    # Async işlemi çalıştır
    import asyncio
    asyncio.run(create_admin(email, password, full_name, phone, gender, studio_id))


if __name__ == "__main__":
    main()
