import redis.asyncio as redis
from src.utils.settings import settings

redis_client =redis.from_url(
    settings.REDIS_URL,
    decode_responses = True
)



async def revoke_token(token: str, expires_in: int):
    key = f"blacklist:{token}"

    await redis_client.set(
        key,
        "revoked",
        ex=expires_in
    )


async def is_token_revoked(token: str):
    key = f"blacklist:{token}"

    result = await redis_client.get(key)

    return result is not None




async def save_refresh_token(jti: str, user_id: int, expires_in: int):

    key = f"refresh_token:{jti}"

    await redis_client.set(
        key,
        str(user_id),
        ex=expires_in
    )


async def get_refresh_token(jti: str):

    key = f"refresh_token:{jti}"

    return await redis_client.get(key)


async def delete_refresh_token(jti: str):

    key = f"refresh_token:{jti}"

    await redis_client.delete(key)