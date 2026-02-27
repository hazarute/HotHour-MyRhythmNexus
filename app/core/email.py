from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from app.core.config import settings
from app.core.security import create_verification_token
import logging
import asyncio

logger = logging.getLogger(__name__)

# Gmail kontrol
if settings.EMAILS_ENABLED:
    logger.info(f"📧 Email servisi etkinleştirildi - SMTP: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    logger.info(f"📧 Gönderen email: {settings.EMAILS_FROM_EMAIL}")

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_user if settings.SMTP_user else "",
    MAIL_PASSWORD=settings.SMTP_PASSWORD if settings.SMTP_PASSWORD else "",
    MAIL_FROM=settings.EMAILS_FROM_EMAIL if settings.EMAILS_FROM_EMAIL else "noreply@hothour.com",
    MAIL_PORT=settings.SMTP_PORT if settings.SMTP_PORT else 587,
    MAIL_SERVER=settings.SMTP_HOST if settings.SMTP_HOST else "smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False  # Gmail için sertifika doğrulama devre dışı
)

async def send_email(email_to: EmailStr, subject_template: str, html_template: str):
    """
    Base function to send emails
    """
    if not settings.EMAILS_ENABLED:
        logger.info(f"Emails disabled. Skipping email to {email_to}")
        return

    message = MessageSchema(
        subject=subject_template,
        recipients=[email_to],
        body=html_template,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    try:
        logger.debug(f"Attempting to send email to {email_to} via {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        await fm.send_message(message)
        logger.info(f"✅ Email successfully sent to {email_to}")
    except Exception as e:
        logger.error(f"❌ Error sending email to {email_to}: {type(e).__name__}: {str(e)}")
        raise

async def send_verification_email(email_to: str, token: str) -> None:
    """
    Sends a verification email to the user with HotHour branding
    """
    if not settings.EMAILS_ENABLED:
        logger.info(f"Verification token for {email_to}: {token}") # Log token for dev without email server
        return

    project_name = settings.PROJECT_NAME
    subject = f"✨ {project_name} - Hesabınızı Doğrulayın"
    
    # Email link - Frontend verify sayfasına yönlendir (URL .env'den okunur)
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                max-width: 600px;
                width: 100%;
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px 30px;
                text-align: center;
                color: white;
            }}
            .logo-section {{
                margin-bottom: 20px;
            }}
            .logo {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .header h1 {{
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 5px;
                letter-spacing: -0.5px;
            }}
            .header p {{
                font-size: 14px;
                opacity: 0.9;
                font-weight: 500;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .greeting {{
                font-size: 18px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 20px;
            }}
            .message {{
                font-size: 15px;
                line-height: 1.6;
                color: #555;
                margin-bottom: 30px;
            }}
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 14px 40px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                font-size: 16px;
                transition: transform 0.2s, box-shadow 0.2s;
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
                border: none;
            }}
            .cta-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6);
            }}
            .link-section {{
                margin-top: 30px;
                padding-top: 30px;
                border-top: 1px solid #f0f0f0;
                text-align: center;
            }}
            .link-label {{
                font-size: 12px;
                color: #999;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 10px;
            }}
            .link-text {{
                font-size: 13px;
                color: #666;
                word-break: break-all;
                font-family: 'Courier New', monospace;
                background: #f8f8f8;
                padding: 12px;
                border-radius: 6px;
            }}
            .timer {{
                background: #fff9e6;
                border-left: 4px solid #ffa500;
                padding: 15px;
                margin: 25px 0;
                border-radius: 4px;
                font-size: 14px;
                color: #666;
            }}
            .footer {{
                background: #f8f8f8;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
                color: #999;
            }}
            .footer p {{
                margin-bottom: 10px;
                line-height: 1.5;
            }}
            .footer-links {{
                font-size: 11px;
                margin-top: 15px;
            }}
            .footer-links a {{
                color: #667eea;
                text-decoration: none;
                margin: 0 10px;
            }}
            .security-note {{
                background: #e3f2fd;
                border-left: 4px solid #2196F3;
                padding: 12px;
                margin: 20px 0;
                border-radius: 4px;
                font-size: 13px;
                color: #1565c0;
            }}
            @media (max-width: 600px) {{
                .container {{
                    border-radius: 8px;
                }}
                .header {{
                    padding: 30px 20px;
                }}
                .content {{
                    padding: 25px 20px;
                }}
                .greeting {{
                    font-size: 16px;
                }}
                .message {{
                    font-size: 14px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <div class="logo-section">
                    <div class="logo">⏳🔥</div>
                </div>
                <h1>{project_name}</h1>
                <p>Pilates Oturumları Platformu</p>
            </div>

            <!-- Content -->
            <div class="content">
                <p class="greeting">Merhaba! 👋</p>
                
                <p class="message">
                    {project_name} hesabınızı oluşturdığunuz için teşekkür ederiz! Hesabınızı aktif hale getirmek için 
                    lütfen aşağıdaki butona tıklayarak email adresinizi doğrulayın.
                </p>

                <center>
                    <a href="{verification_link}" class="cta-button">Hesabımı Doğrula ✨</a>
                </center>

                <div class="timer">
                    ⏱️ <strong>Önemli:</strong> Bu doğrulama linki 48 saat geçerlidir. Lütfen bu süre içinde doğrulama işlemini tamamlayın.
                </div>

                <div class="security-note">
                    🔒 Eğer linke tıklamakta sorun yaşıyorsanız, aşağıdaki linki tarayıcınızın adres çubuğuna yapıştırabilirsiniz.
                </div>

                <!-- Link Section -->
                <div class="link-section">
                    <div class="link-label">Doğrulama Linki:</div>
                    <div class="link-text">{verification_link}</div>
                </div>

                <p class="message" style="margin-top: 30px; font-size: 13px; color: #999;">
                    <strong>Bu email'i siz açmadıysanız:</strong> Lütfen bu email'i görmezden gelin. Başka birisi yanlışlıkla 
                    email adresinizi kullanmış olabilir.
                </p>
            </div>

            <!-- Footer -->
            <div class="footer">
                <p>© 2026 {project_name}. Tüm hakları saklıdır.</p>
                <p>Pilates Stüdyoları için Dinamik Fiyatlandırma Platformu</p>
                <div class="footer-links">
                    <a href="http://localhost:3000">Website</a> | 
                    <a href="http://localhost:3000">Yardım</a> | 
                    <a href="http://localhost:3000">Gizlilik Politikası</a>
                </div>
                <p style="margin-top: 15px; font-size: 11px; color: #bbb;">
                    Eğer problemler yaşıyorsanız: support@hothour.com ile iletişime geçin.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=html_content
    )
