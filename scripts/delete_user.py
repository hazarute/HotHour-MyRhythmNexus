#!/usr/bin/env python3
"""
Kullanıcı Hesabı Silme Script
Kullanım: python scripts/delete_user.py <user_id_veya_email> [--force]
"""

import sys
import os
from pathlib import Path

# Proje root'u ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from prisma import Prisma

# .env dosyasını yükle
load_dotenv()


async def delete_user(identifier: str, force: bool = False, prisma_client = None) -> None:
    """Kullanıcı hesabını sil"""
    
    # Use provided prisma client or create new one
    if prisma_client is None:
        prisma = Prisma()
        await prisma.connect()
        should_disconnect = True
    else:
        prisma = prisma_client
        should_disconnect = False
    
    try:
        # ID veya email ile kullanıcı bul
        user = None
        
        # Eğer identifier sayı ise ID olarak ara
        if identifier.isdigit():
            user = await prisma.user.find_unique(
                where={"id": int(identifier)}
            )
        else:
            # Email olarak ara
            user = await prisma.user.find_unique(
                where={"email": identifier}
            )
        
        # Kullanıcı kontrolü
        if not user:
            print(f"❌ Hata: Kullanıcı bulunamadı (ID/Email: {identifier})")
            return
        
        # Silme onayı
        if not force:
            print(f"\n⚠️  Silmek üzere olan kullanıcı hesabı:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Ad Soyad: {user.fullName}")
            print(f"   Role: {user.role}")
            print(f"   Email Doğrulanmış: {'Evet' if user.isVerified else 'Hayır'}")
            print(f"   Oluşturulma: {user.createdAt}")
            print()
            
            # Onay al
            confirm = input("Bu kullanıcı hesabını silmek istediğinize emin misiniz? (evet/hayır): ").strip().lower()
            if confirm not in ["evet", "yes", "y", "e"]:
                print("❌ İşlem iptal edildi.")
                return
        
        # Silme işlemi
        deleted_user = await prisma.user.delete(
            where={"id": user.id}
        )
        
        print(f"\n✅ Kullanıcı hesabı başarıyla silindi !")
        print(f"   ID: {deleted_user.id}")
        print(f"   Email: {deleted_user.email}")
        print(f"   Ad Soyad: {deleted_user.fullName}")
        print(f"   Role: {deleted_user.role}")
        print()
        
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
        raise
    finally:
        if should_disconnect:
            await prisma.disconnect()


def main():
    """CLI entry point"""
    
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print("🗑️  Kullanıcı Hesabı Silme Script")
        print()
        print("Kullanım:")
        print("   python scripts/delete_user.py <user_id_veya_email> [--force]")
        print()
        print("Parametreler:")
        print("   user_id_veya_email : Kullanıcı ID'si (sayı) veya Email adresi")
        print("   --force            : Onay dialogs'u atla ve direkt sil")
        print()
        print("Örnekler:")
        print("   python scripts/delete_user.py 1")
        print("   python scripts/delete_user.py user@example.com")
        print("   python scripts/delete_user.py 1 --force")
        print("   python scripts/delete_user.py user@example.com --force")
        sys.exit(1 if len(sys.argv) < 2 else 0)
    
    identifier = sys.argv[1]
    force = "--force" in sys.argv
    
    # Async işlemi çalıştır
    import asyncio
    asyncio.run(delete_user(identifier, force=force))


if __name__ == "__main__":
    main()
