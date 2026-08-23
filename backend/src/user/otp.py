import secrets
import json

from src.utils.redis import redis_client


OTP_EXPIRE_SECONDS = 300
REGISTRATION_EXPIRE_SECONDS = 900
RESET_OTP_EXPIRE_SECONDS = 300 
RESET_VERIFIED_EXPIRE_SECONDS = 600
RESEND_OTP_COOLDOWN_SECONDS = 300  # 5 minutes

LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCK_SECONDS = 600  # 10 minutes
LOGIN_ATTEMPT_EXPIRE_SECONDS = 600

# =========================Login attempts=======================

async def get_login_attempts(email: str):
    key = f"login_attempts:{email}"
    attempts = await redis_client.get(key)

    if not attempts:
        return 0

    return int(attempts)


async def increment_login_attempts(email: str):
    key = f"login_attempts:{email}"

    attempts = await redis_client.incr(key)

    # Set TTL only when the key is first created
    if attempts == 1:
        await redis_client.expire(
            key,
            LOGIN_ATTEMPT_EXPIRE_SECONDS
        )

    return attempts



async def reset_login_attempts(email: str):
    key = f"login_attempts:{email}"
    await redis_client.delete(key)


async def lock_login(email: str):
    key = f"login_locked:{email}"

    await redis_client.set(
        key,
        "true",
        ex=LOGIN_LOCK_SECONDS
    )


async def is_login_locked(email: str):
    key = f"login_locked:{email}"

    return await redis_client.exists(key)
# ================================================


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


async def save_registration(email: str, data: dict):
    key = f"email_verification:{email}"

    await redis_client.set(
        key,
        json.dumps(data),
        ex=REGISTRATION_EXPIRE_SECONDS
    )

async def save_registration_otp(email: str, otp: str):
    key = f"registration_otp:{email}"

    await redis_client.set(
        key,
        otp,
        ex=OTP_EXPIRE_SECONDS
    )


async def get_registration(email: str):
    key = f"email_verification:{email}"

    data = await redis_client.get(key)
    if not data:
        return None
    return json.loads(data)


async def get_registration_otp(email: str):
    key = f"registration_otp:{email}"

    return await redis_client.get(key)


async def delete_registration(email: str):
    key = f"email_verification:{email}"
    await redis_client.delete(key)

async def delete_registration_otp(email: str):
    key = f"registration_otp:{email}"

    await redis_client.delete(key)


async def save_reset_otp(email:str, otp:str):
    key = f"reset_password:{email}"
    await redis_client.set(key,otp,ex=RESET_OTP_EXPIRE_SECONDS)

async def get_reset_otp(email:str):
    key = f"reset_password:{email}"
    return await redis_client.get(key)

async def delete_reset_otp(email: str):
    key = f"reset_password:{email}"
    await redis_client.delete(key)

# Reset OTP Verification
# =========================

async def save_reset_verified(email: str):
    key = f"reset_verified:{email}"

    await redis_client.set(
        key,
        "true",
        ex=RESET_VERIFIED_EXPIRE_SECONDS
    )


async def get_reset_verified(email: str):
    key = f"reset_verified:{email}"

    return await redis_client.get(key)


async def delete_reset_verified(email: str):
    key = f"reset_verified:{email}"

    await redis_client.delete(key)


#RESEND COOLDOWN OTP

async def save_registration_resend_cooldown(email: str):
    key = f"registration_resend_cooldown:{email}"

    await redis_client.set(
        key,
        "true",
        ex=RESEND_OTP_COOLDOWN_SECONDS
    )


async def is_registration_resend_cooldown(email: str):
    key = f"registration_resend_cooldown:{email}"

    return await redis_client.exists(key)


async def get_registration_resend_ttl(email: str):
    key = f"registration_resend_cooldown:{email}"

    return await redis_client.ttl(key)

    