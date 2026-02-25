#!/usr/bin/env python3
"""
Admin Hesabı Silmeyen Script
Kullanım: python scripts/delete_admin.py <admin_id_veya_email> [--force]
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


async def delete_admin(identifier: str, force: bool = False, prisma_client = None) -> None:
    """Admin hesabını sil"""
    
    # Use provided prisma client or create new one
    if prisma_client is None:
        prisma = Prisma()
        await prisma.connect()
        should_disconnect = True
    else:
        prisma = prisma_client
        should_disconnect = False
    
    try:
        # ID veya email ile admin bul
        admin = None
        
        # Eğer identifier sayı ise ID olarak ara
        if identifier.isdigit():
            admin = await prisma.user.find_unique(
                where={"id": int(identifier)}
            )
        else:
            # Email olarak ara
            admin = await prisma.user.find_unique(
                where={"email": identifier}
            )
        
        # Admin kontrolü
        if not admin:
            print(f"❌ Hata: Admin bulunamadı (ID/Email: {identifier})")
            return
        
        if admin.role != "ADMIN":
            print(f"❌ Hata: Bu kullanıcı admin değildir ! (Role: {admin.role})")
            return
        
        # Silme onayı
        if not force:
            print(f"\n⚠️  Silmek üzere olan admin hesabı:")
            print(f"   ID: {admin.id}")
            print(f"   Email: {admin.email}")
            print(f"   Ad Soyad: {admin.fullName}")
            print(f"   Oluşturulma: {admin.createdAt}")
            print()
            
            # Onay al
            confirm = input("Bu admin hesabını silmek istediğinize emin misiniz? (evet/hayır): ").strip().lower()
            if confirm not in ["evet", "yes", "y", "e"]:
                print("❌ İşlem iptal edildi.")
                return
        
        # Silme işlemi
        deleted_admin = await prisma.user.delete(
            where={"id": admin.id}
        )
        
        print(f"\n✅ Admin hesabı başarıyla silindi !")
        print(f"   ID: {deleted_admin.id}")
        print(f"   Email: {deleted_admin.email}")
        print(f"   Ad Soyad: {deleted_admin.fullName}")
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
        print("🗑️  Admin Hesabı Silme Script")
        print()
        print("Kullanım:")
        print("   python scripts/delete_admin.py <admin_id_veya_email> [--force]")
        print()
        print("Parametreler:")
        print("   admin_id_veya_email : Admin ID'si (sayı) veya Email adresi")
        print("   --force             : Onay dialogs'u atla ve direkt sil")
        print()
        print("Örnekler:")
        print("   python scripts/delete_admin.py 1")
        print("   python scripts/delete_admin.py admin@example.com")
        print("   python scripts/delete_admin.py 1 --force")
        print("   python scripts/delete_admin.py admin@example.com --force")
        sys.exit(1 if len(sys.argv) < 2 else 0)
    
    identifier = sys.argv[1]
    force = "--force" in sys.argv
    
    # Async işlemi çalıştır
    import asyncio
    asyncio.run(delete_admin(identifier, force=force))


if __name__ == "__main__":
    main()
