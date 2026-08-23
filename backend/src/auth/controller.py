from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode

from src.user.models import UserModel
from src.user.controller import create_access_token, create_refresh_token
from src.utils.redis import save_refresh_token
from src.utils.settings import settings


oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)


async def google_callback(request: Request, db: Session):

    try:
        # 1. Get access token from Google

        token = await oauth.google.authorize_access_token(request)

        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not get user information from Google"
            )

        email = user_info.get("email")
        name = user_info.get("name")
        google_id = user_info.get("sub")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google account email not found"
            )

        # =========================================================
        # 3. Check if user already exists
        # =========================================================

        user = db.query(UserModel).filter(
            UserModel.email == email
        ).first()

        # =========================================================
        # 4. If user DOES NOT exist, create a new user
        # =========================================================

        if not user:

            # Create username
            username = email.split("@")[0]

            # Make username unique if necessary
            existing_username = db.query(UserModel).filter(
                UserModel.username == username
            ).first()

            if existing_username:
                username = f"{username}_{google_id[-6:]}"

            # Create new user
            user = UserModel(
                name=name,
                username=username,
                email=email,
                password=None,
                google_id=google_id,
                is_verified=True
            )

            db.add(user)
            db.commit()
            db.refresh(user)

        # =========================================================
        # 5. Generate YOUR application's JWT
        # =========================================================

        jwt_token = create_access_token(user)
        refresh_token, jti = create_refresh_token(user)
        await save_refresh_token(
            jti,
            user.id,
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        # =========================================================
        # 6. Return YOUR JWT + user information
        # =========================================================

        callback_data = urlencode({
            "token": jwt_token,
            "refresh_token": refresh_token,
            "email": user.email,
        })
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/#google-callback?{callback_data}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # =============================================================
    # Don't convert our HTTPException into 500
    # =============================================================

    except HTTPException:
        raise

    # =============================================================
    # Handle unexpected errors
    # =============================================================

    except Exception as e:
        print("Google OAuth Error:", e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed"
        )