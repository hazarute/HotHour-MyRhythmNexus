from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, NameEmail, SecretStr
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
    MAIL_PASSWORD=(
        settings.SMTP_PASSWORD
        if isinstance(settings.SMTP_PASSWORD, SecretStr)
        else SecretStr(settings.SMTP_PASSWORD if settings.SMTP_PASSWORD else "")
    ),
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

    recipient_email = str(email_to)
    recipient = NameEmail(name=recipient_email, email=recipient_email)

    message = MessageSchema(
        subject=subject_template,
        recipients=[recipient],
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
    display_project_name = project_name.replace(" Core", "").replace("Core ", "").replace("Core", "").strip()
    subject = f"🔥 {display_project_name} - Arenaya Giriş İçin Son Bir Adım"
    
    # Email link - Frontend verify sayfasına yönlendir (URL .env'den okunur)
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    logo_url = f"{settings.FRONTEND_URL}/logo_marka_adi_var.png"
    logo_html = f'<img src="{logo_url}" alt="{display_project_name} Logo" class="logo-img" style="max-height: 60px; width: auto;" />'
    
    html_content = f"""
    <!DOCTYPE html>
    <html dir="ltr" lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            /* E-posta istemcileri için güvenli CSS sıfırlaması */
            body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
            table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
            img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
            
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #050505; /* Deep Black */
                color: #e2e8f0;
                width: 100% !important;
            }}
            .wrapper {{
                width: 100%;
                background-color: #050505;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #0a0f1a; /* Dark Blue/Black Card */
                border: 1px solid #1e293b;
                border-radius: 16px;
                overflow: hidden;
            }}
            .header {{
                padding: 40px 30px 20px;
                text-align: center;
                border-bottom: 1px solid #1e293b;
            }}
            .header h1 {{
                color: #ffffff;
                font-size: 24px;
                font-weight: 900;
                margin: 20px 0 5px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            .header p {{
                color: #00BFFF; /* Neon Blue */
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 3px;
                margin: 0;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .greeting {{
                color: #ffffff;
                font-size: 18px;
                font-weight: 700;
                margin-bottom: 20px;
            }}
            .message {{
                color: #94a3b8;
                font-size: 15px;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .button-container {{
                text-align: center;
                margin: 35px 0;
            }}
            .cta-button {{
                display: inline-block;
                background-color: #00BFFF; /* Neon Blue */
                color: #000000 !important;
                padding: 16px 40px;
                border-radius: 12px;
                text-decoration: none;
                font-weight: 900;
                font-size: 16px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            .info-box {{
                background-color: #050505;
                border-left: 4px solid #f20d80; /* Neon Magenta */
                padding: 16px 20px;
                border-radius: 0 8px 8px 0;
                margin-bottom: 20px;
            }}
            .info-box p {{
                margin: 0;
                font-size: 13px;
                color: #cbd5e1;
                line-height: 1.5;
            }}
            .link-box {{
                background-color: #000000;
                border: 1px solid #1e293b;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin-top: 30px;
            }}
            .link-box p {{
                margin: 0;
                font-family: 'Courier New', Courier, monospace;
                color: #00BFFF;
                font-size: 12px;
                word-break: break-all;
            }}
            .footer {{
                background-color: #050505;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #1e293b;
            }}
            .footer p {{
                color: #64748b;
                font-size: 12px;
                margin: 0 0 10px;
                line-height: 1.5;
            }}
            .footer-links a {{
                color: #f20d80; /* Neon Magenta */
                text-decoration: none;
                font-weight: 600;
                margin: 0 10px;
            }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="container">
                <div class="header">
                    {logo_html}
                    <h1>Arenaya Hoş Geldin</h1>
                    <p>Son Bir Adım Kaldı</p>
                </div>

                <div class="content">
                    <div class="greeting">Merhaba, 👋</div>
                    
                    <div class="message">
                        <strong>{display_project_name}</strong> dünyasına adım attığın için teşekkürler. Canlı Pilates oturumlarında fiyatlar düşerken fırsatları yakalamaya başlamak ve yerini ayırtmak için e-posta adresini doğrulaman gerekiyor.
                    </div>

                    <div class="button-container">
                        <a href="{verification_link}" class="cta-button">HESABI DOĞRULA</a>
                    </div>

                    <div class="info-box" style="border-left-color: #ff7b00;">
                        <p><strong style="color: #ff7b00;">🔥 ZAMAN DARALIYOR:</strong> Güvenliğin için bu doğrulama bağlantısı <strong>48 saat</strong> içinde geçerliliğini yitirecektir.</p>
                    </div>

                    <div class="info-box" style="border-left-color: #00BFFF;">
                        <p>🔒 Butona tıklamakta sorun yaşıyorsan, aşağıdaki şifreli bağlantıyı kopyalayıp tarayıcına yapıştırabilirsin:</p>
                    </div>

                    <div class="link-box">
                        <p>{verification_link}</p>
                    </div>

                    <div class="message" style="margin-top: 40px; font-size: 12px; color: #64748b; text-align: center;">
                        Eğer bu hesabı sen oluşturmadıysan, bu e-postayı güvenle silebilirsin. Başka biri e-posta adresini yanlış yazmış olabilir.
                    </div>
                </div>

                <div class="footer">
                    <p>© 2026 {project_name}. Tüm hakları saklıdır.</p>
                    <p>Pilates Stüdyoları için Dinamik Fiyatlandırma Platformu</p>
                    <div class="footer-links" style="margin-top: 15px;">
                        <a href="{settings.FRONTEND_URL}">Canlı Arenaya Dön</a>
                    </div>
                </div>
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
