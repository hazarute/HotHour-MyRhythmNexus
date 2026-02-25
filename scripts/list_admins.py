#!/usr/bin/env python3
"""
Admin Hesaplarını Listeleyen Script
Kullanım: python scripts/list_admins.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Proje root'u ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from prisma import Prisma
from tabulate import tabulate

# .env dosyasını yükle
load_dotenv()


async def list_admins(verbose: bool = False, prisma_client = None) -> None:
    """Tüm admin hesaplarını listele"""
    
    # Use provided prisma client or create new one
    if prisma_client is None:
        prisma = Prisma()
        await prisma.connect()
        should_disconnect = True
    else:
        prisma = prisma_client
        should_disconnect = False
    
    try:
        # Tüm admin kullanıcılarını getir
        admins = await prisma.user.find_many(
            where={"role": "ADMIN"}
        )
        # Sort by createdAt descending
        admins = sorted(admins, key=lambda x: x.createdAt, reverse=True)
        
        if not admins:
            print("ℹ️  Hiçbir admin hesabı bulunamadı.")
            return
        
        # Tablo verisi hazırla
        table_data = []
        for admin in admins:
            created_at = admin.createdAt.strftime("%d.%m.%Y %H:%M")
            verified_badge = "✅" if admin.isVerified else "❌"
            
            if verbose:
                row = [
                    admin.id,
                    admin.email,
                    admin.fullName,
                    admin.phone,
                    admin.gender or "-",
                    verified_badge,
                    created_at,
                ]
            else:
                row = [
                    admin.id,
                    admin.email,
                    admin.fullName,
                    verified_badge,
                    created_at,
                ]
            
            table_data.append(row)
        
        # Başlık
        if verbose:
            headers = ["ID", "Email", "Ad Soyad", "Telefon", "Cinsiyet", "Doğrulandı", "Oluşturulma"]
        else:
            headers = ["ID", "Email", "Ad Soyad", "Doğrulandı", "Oluşturulma"]
        
        print(f"\n📋 Toplam Admin Sayısı: {len(admins)}\n")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()
        
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
        raise
    finally:
        if should_disconnect:
            await prisma.disconnect()


def main():
    """CLI entry point"""
    
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("📋 Admin Hesaplarını Listeleyen Script")
        print()
        print("Kullanım:")
        print("   python scripts/list_admins.py [--verbose|-v] [--help|-h]")
        print()
        print("Parametreler:")
        print("   --verbose, -v    : Tüm detayları göster (telefon, cinsiyet)")
        print("   --help, -h       : Bu yardım mesajını göster")
        print()
        print("Örnekler:")
        print("   python scripts/list_admins.py")
        print("   python scripts/list_admins.py --verbose")
        print("   python scripts/list_admins.py -v")
        sys.exit(0)
    
    # Async işlemi çalıştır
    import asyncio
    asyncio.run(list_admins(verbose=verbose))


if __name__ == "__main__":
    main()
