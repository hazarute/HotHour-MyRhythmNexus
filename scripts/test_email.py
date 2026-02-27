#!/usr/bin/env python3
"""
Email Gönderim Test Script
Kullanım: python scripts/test_email.py <alici_email>
"""

import sys
import os
from pathlib import Path
import asyncio

# Proje root'u ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from app.core.config import settings
from app.core.email import send_email

# .env dosyasını yükle
load_dotenv()


async def test_email(recipient_email: str):
    """Test email gönderimi"""
    
    print("📧 Email Konfigürasyonu Kontrol")
    print("=" * 50)
    print(f"EMAILS_ENABLED: {settings.EMAILS_ENABLED}")
    print(f"FRONTEND_URL: {settings.FRONTEND_URL}")
    print(f"SMTP_HOST: {settings.SMTP_HOST}")
    print(f"SMTP_PORT: {settings.SMTP_PORT}")
    print(f"SMTP_USER: {settings.SMTP_user}")
    print(f"EMAILS_FROM_EMAIL: {settings.EMAILS_FROM_EMAIL}")
    print()
    
    if not settings.EMAILS_ENABLED:
        print("❌ EMAIL SERVİSİ KAPALI!")
        print("SMTP ayarlarını .env dosyasında kontrol edin.")
        return
    
    if not settings.SMTP_PASSWORD:
        print("❌ SMTP_PASSWORD ayarlanmamış!")
        print(".env dosyasında SMTP_PASSWORD tanımlayın.")
        return
    
    print("🚀 Email gönderiliyor...")
    print()
    
    try:
        await send_email(
            email_to=recipient_email,
            subject_template="HotHour - Test Email",
            html_template="""
            <html>
                <body style="font-family: Arial; direction: rtl;">
                    <h1>🎉 Merhaba!</h1>
                    <p>Bu bir test email'idir.</p>
                    <p>Eğer bunu alıyorsanız, email servisi düzgün çalışıyor!</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">HotHour - Pilates Oturumları Platformu</p>
                </body>
            </html>
            """
        )
        print(f"✅ Email başarıyla {recipient_email} adresine gönderildi!")
        
    except Exception as e:
        print(f"❌ Email gönderim hatası:")
        print(f"   Hata Türü: {type(e).__name__}")
        print(f"   Hata Mesajı: {str(e)}")
        print()
        print("📝 Olası Çözümler:")
        print("   1. Gmail hesabında 2-Factor Authentication etkin mi?")
        print("   2. App Password oluşturulmuş mu ve .env'de doğru mu?")
        print("   3. İnternet bağlantısı var mı?")
        print("   4. SMTP_PASSWORD şifresi boşluk içeriyor mu? (Tırnak içinde yazılmalı)")


def main():
    """CLI entry point"""
    
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print("📧 Email Test Script")
        print()
        print("Kullanım:")
        print("   python scripts/test_email.py <alici_email>")
        print()
        print("Örnek:")
        print("   python scripts/test_email.py test@example.com")
        sys.exit(1 if len(sys.argv) < 2 else 0)
    
    recipient_email = sys.argv[1]
    
    # Async işlemi çalıştır
    asyncio.run(test_email(recipient_email))


if __name__ == "__main__":
    main()
