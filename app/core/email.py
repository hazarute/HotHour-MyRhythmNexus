import base64
from email.message import EmailMessage
import json

import aiohttp
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, NameEmail, SecretStr
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

if settings.EMAILS_ENABLED:
    logger.info(f"📧 Email servisi etkinleştirildi - SMTP: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    if settings.GMAIL_API_ENABLED:
        logger.info("📧 Gmail API email provider aktif")
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


def _smtp_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_PORT and settings.EMAILS_FROM_EMAIL)


def _gmail_api_configured() -> bool:
    return bool(
        settings.GMAIL_API_ENABLED
        and settings.GMAIL_CLIENT_ID
        and settings.GMAIL_CLIENT_SECRET
        and settings.GMAIL_REFRESH_TOKEN
        and (settings.GMAIL_SENDER_EMAIL or settings.EMAILS_FROM_EMAIL)
    )


async def _get_gmail_access_token() -> str:
    token_endpoint = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": settings.GMAIL_CLIENT_ID,
        "client_secret": settings.GMAIL_CLIENT_SECRET,
        "refresh_token": settings.GMAIL_REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }

    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(token_endpoint, data=payload) as response:
            text = await response.text()
            if response.status != 200:
                raise RuntimeError(f"Gmail token alınamadı ({response.status}): {text[:300]}")
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                raise RuntimeError("Gmail token yanıtı JSON değil") from exc

    access_token = data.get("access_token")
    if not access_token:
        raise RuntimeError("Gmail token yanıtında access_token yok")

    return access_token


async def _send_email_via_gmail_api(email_to: EmailStr, subject_template: str, html_template: str) -> None:
    access_token = await _get_gmail_access_token()
    sender_email = settings.GMAIL_SENDER_EMAIL or settings.EMAILS_FROM_EMAIL

    if not sender_email:
        raise RuntimeError("Gmail sender email tanımlı değil")

    message = EmailMessage()
    message["To"] = str(email_to)
    message["From"] = sender_email
    message["Subject"] = subject_template
    message.set_content("Bu e-posta HTML içerik barındırır.")
    message.add_alternative(html_template, subtype="html")

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    payload = {"raw": raw_message}

    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=payload,
        ) as response:
            text = await response.text()
            if response.status not in (200, 202):
                raise RuntimeError(f"Gmail API mail gönderimi başarısız ({response.status}): {text[:300]}")


async def _send_email_via_smtp(email_to: EmailStr, subject_template: str, html_template: str) -> None:
    recipient_email = str(email_to)
    recipient = NameEmail(name=recipient_email, email=recipient_email)

    message = MessageSchema(
        subject=subject_template,
        recipients=[recipient],
        body=html_template,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_email(email_to: EmailStr, subject_template: str, html_template: str):
    """
    Base function to send emails
    """
    if not settings.EMAILS_ENABLED:
        logger.info(f"Emails disabled. Skipping email to {email_to}")
        return

    if _gmail_api_configured():
        try:
            logger.debug(f"Attempting Gmail API email to {email_to}")
            await _send_email_via_gmail_api(email_to, subject_template, html_template)
            logger.info(f"✅ Email successfully sent via Gmail API to {email_to}")
            return
        except Exception as e:
            logger.error(f"❌ Gmail API send error for {email_to}: {type(e).__name__}: {str(e)}")
            if not _smtp_configured():
                raise

    if _smtp_configured():
        try:
            logger.debug(f"Attempting SMTP email to {email_to} via {settings.SMTP_HOST}:{settings.SMTP_PORT}")
            await _send_email_via_smtp(email_to, subject_template, html_template)
            logger.info(f"✅ Email successfully sent via SMTP to {email_to}")
            return
        except Exception as e:
            logger.error(f"❌ SMTP send error for {email_to}: {type(e).__name__}: {str(e)}")
            raise

    logger.error("❌ Email provider yapılandırılmamış. Gmail API veya SMTP ayarlarını kontrol edin.")
    raise RuntimeError("Email provider not configured")

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
    
    try:
        await send_email(
            email_to=email_to,
            subject_template=subject,
            html_template=html_content
        )
    except Exception as e:
        logger.error(f"Verification email could not be sent to {email_to}: {type(e).__name__}: {str(e)}")
