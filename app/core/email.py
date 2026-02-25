from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from app.core.config import settings
from app.core.security import create_verification_token
import logging

logger = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_user if settings.SMTP_user else "",
    MAIL_PASSWORD=settings.SMTP_PASSWORD if settings.SMTP_PASSWORD else "",
    MAIL_FROM=settings.EMAILS_FROM_EMAIL if settings.EMAILS_FROM_EMAIL else "noreply@hothour.com",
    MAIL_PORT=settings.SMTP_PORT if settings.SMTP_PORT else 587,
    MAIL_SERVER=settings.SMTP_HOST if settings.SMTP_HOST else "smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
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
        await fm.send_message(message)
        logger.info(f"Email sent to {email_to}")
    except Exception as e:
        logger.error(f"Error sending email to {email_to}: {e}")

async def send_verification_email(email_to: str, token: str) -> None:
    """
    Sends a verification email to the user
    """
    if not settings.EMAILS_ENABLED:
        logger.info(f"Verification token for {email_to}: {token}") # Log token for dev without email server
        return

    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - E-posta Doğrulama"
    link = f"http://localhost:3000/verify-email?token={token}"
    
    html_content = f"""
    <html>
        <body>
            <h1>Hoşgeldiniz!</h1>
            <p>{project_name} hesabınızı doğrulamak için aşağıdaki linke tıklayınız:</p>
            <p>
                <a href="{link}">Hesabımı Doğrula</a>
            </p>
            <p>Link 48 saat geçerlidir.</p>
        </body>
    </html>
    """
    
    await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=html_content
    )
