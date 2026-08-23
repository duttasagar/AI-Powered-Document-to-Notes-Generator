from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from src.utils.settings import settings

from typing import List


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="Sagar Dutta",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)


async def send_email(emails: List[str], otp: str):

    html = f"""
    <h2>Email Verification</h2>

    <p>Hi,</p>

    <p>Your OTP for email verification is:</p>

    <h1>{otp}</h1>

    <p>This OTP will expire in 5 minutes.</p>

    <p>If you did not request this, please ignore this email.</p>
    """

    message = MessageSchema(
        subject="Email Verification OTP",
        recipients=emails,
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)

    await fm.send_message(message)

    return {"message": "OTP sent successfully"}


async def send_registration_confirmation(emails: List[str], name: str):

    html = f"""
    <h2>Registration Successful</h2>

    <p>Hi {name},</p>

    <p>Your account has been successfully registered.</p>

    <p>Your email has been verified successfully.</p>

    <p>You can now login to your account.</p>

    <br>

    <p>Thank you for registering.</p>
    """

    message = MessageSchema(
        subject="Registration Successful",
        recipients=emails,
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)

    await fm.send_message(message)

    return {"message": "Confirmation email sent"}





async def send_reset_password_email(
    emails: List[str],
    otp: str
):
    html = f"""
    <h2>Password Reset</h2>

    <p>Hi,</p>

    <p>We received a request to reset your password.</p>

    <p>Your password reset OTP is:</p>

    <h1>{otp}</h1>

    <p>This OTP will expire in 5 minutes.</p>

    <p>If you did not request a password reset, please ignore this email.</p>

    <br>

    <p>Thank you.</p>
    """

    message = MessageSchema(
        subject="Password Reset OTP",
        recipients=emails,
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)

    await fm.send_message(message)

    return {
        "message": "Password reset OTP sent successfully"
    }