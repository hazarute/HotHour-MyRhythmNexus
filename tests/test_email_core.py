import pytest
from unittest.mock import AsyncMock, patch
from pydantic import SecretStr, NameEmail

from app.core import email as email_module


def test_connection_config_uses_secretstr_password():
    assert isinstance(email_module.conf.MAIL_PASSWORD, SecretStr)


@pytest.mark.asyncio
async def test_send_email_builds_nameemail_recipient():
    with patch.object(email_module.settings, "EMAILS_ENABLED", True):
        with patch("app.core.email.FastMail.send_message", new_callable=AsyncMock) as mock_send:
            await email_module.send_email(
                email_to="test@example.com",
                subject_template="Test Subject",
                html_template="<p>Test</p>",
            )

            assert mock_send.await_count == 1
            args, _ = mock_send.await_args_list[0]
            message = args[0]
            assert len(message.recipients) == 1
            assert isinstance(message.recipients[0], NameEmail)
            assert message.recipients[0].email == "test@example.com"


@pytest.mark.asyncio
async def test_send_email_skips_when_disabled():
    with patch.object(email_module.settings, "EMAILS_ENABLED", False):
        with patch("app.core.email.FastMail.send_message", new_callable=AsyncMock) as mock_send:
            await email_module.send_email(
                email_to="skip@example.com",
                subject_template="Skip",
                html_template="<p>Skip</p>",
            )
            assert mock_send.await_count == 0


@pytest.mark.asyncio
async def test_send_verification_email_calls_send_email_with_expected_payload():
    token = "tok_123"
    email_to = "verify@example.com"

    with patch.object(email_module.settings, "EMAILS_ENABLED", True):
        with patch.object(email_module.settings, "PROJECT_NAME", "HotHour Core"):
            with patch.object(email_module.settings, "FRONTEND_URL", "http://127.0.0.1:3000"):
                with patch("app.core.email.send_email", new_callable=AsyncMock) as mock_send_email:
                    await email_module.send_verification_email(email_to=email_to, token=token)

                    assert mock_send_email.await_count == 1
                    _, kwargs = mock_send_email.await_args_list[0]
                    assert kwargs["email_to"] == email_to
                    assert kwargs["subject_template"] == "🔥 HotHour - Arenaya Giriş İçin Son Bir Adım"
                    assert "verify-email?token=tok_123" in kwargs["html_template"]
                    assert "logo_marka_adi_var.png" in kwargs["html_template"]
                    assert "HESABI DOĞRULA" in kwargs["html_template"]


@pytest.mark.asyncio
async def test_send_verification_email_skips_when_disabled():
    with patch.object(email_module.settings, "EMAILS_ENABLED", False):
        with patch("app.core.email.send_email", new_callable=AsyncMock) as mock_send_email:
            await email_module.send_verification_email(email_to="dev@example.com", token="dev_token")
            assert mock_send_email.await_count == 0
