from src.user.dtos import (UserSchema,LoginSchema,VerifyOTPRequest,VerifyResetOTPRequest,ResetPasswordRequest,RefreshTokenRequest,ResendOTPRequest)
from sqlalchemy.orm import Session
from fastapi import HTTPException,Request,status,BackgroundTasks,Depends
from src.user.models import UserModel
from pwdlib import PasswordHash
import jwt 
from src.utils.settings import settings
from datetime import datetime, timedelta
from jwt.exceptions import InvalidTokenError
from src.utils.mail import (send_email,send_registration_confirmation , send_reset_password_email)
from src.utils.redis import (is_token_revoked,revoke_token,save_refresh_token,delete_refresh_token,get_refresh_token)
import secrets
from src.utils.db import get_db

LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCK_SECONDS = 600  # 10 minutes
LOGIN_ATTEMPT_EXPIRE_SECONDS = 600


from src.user.otp import (
    save_registration,
    generate_otp,
    get_registration,
    delete_registration,
    save_reset_otp,
    get_reset_otp,
    delete_reset_otp,
    save_reset_verified,
    get_reset_verified,
    delete_reset_verified,
    is_login_locked,
    increment_login_attempts,
    lock_login,
    reset_login_attempts,
    save_registration_otp,
    get_registration_otp,
    delete_registration_otp,
    save_registration_resend_cooldown,
    is_registration_resend_cooldown,
    get_registration_resend_ttl,
    
    
)

password_hash = PasswordHash.recommended()


def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


async def register(body:UserSchema, db:Session, background_tasks: BackgroundTasks):
    is_user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if is_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist..")

    is_username = db.query(UserModel).filter(UserModel.username == body.username).first()
    if is_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )   

    hash_password = get_password_hash(body.password)


    registration_data = {
    "name": body.name,
    "username": body.username,
    "email": body.email,
    "password": hash_password
    }

    # Save registration information
    await save_registration(
    body.email,
    registration_data
    )
    otp = generate_otp()

    await save_registration_otp(
    body.email,
    otp
)

    background_tasks.add_task(
    send_email,
    [body.email],
    otp
)
    
    # otp = generate_otp()

    # registration_data = {
    #     "name": body.name,
    #     "username": body.username,
    #     "email": body.email,
    #     "password": hash_password,
    #     "otp": otp
    # }

    # await save_registration(
    #     body.email,
    #     registration_data
    # )

    # await send_email(
    #     [body.email],
    #     otp
    # )

    # background_tasks.add_task(
    #     send_email,
    #     [body.email],
    #     otp
    # )

    return {
        "message": "OTP sent to your email",
        "email": body.email
    }


async def resend_registration_otp(
    body: ResendOTPRequest,
    background_tasks: BackgroundTasks
):

    if await is_registration_resend_cooldown(body.email):
        remaining = await get_registration_resend_ttl(body.email)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Please wait {remaining} seconds before requesting another OTP"
        )

    # Check registration session
    registration_data = await get_registration(
        body.email
    )

    if not registration_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration session expired. Please register again."
        )

    # Generate new OTP
    new_otp = generate_otp()

    # Save new OTP
    await save_registration_otp(
        body.email,
        new_otp
    )
    await save_registration_resend_cooldown(
    body.email
)

    # Send new OTP
    background_tasks.add_task(
        send_email,
        [body.email],
        new_otp
    )

    return {
        "message": "New OTP sent successfully",
        "email": body.email
    }

async def verify_otp(body:VerifyOTPRequest, db:Session,  background_tasks: BackgroundTasks):
    registration_data = await get_registration(body.email)
    if not registration_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail= "OTP expired or registration data not found")
    
    # if registration_data["otp"] != body.otp:
    #     raise HTTPException( status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    stored_otp = await get_registration_otp(body.email)
    
    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please resend OTP."
        )

    if stored_otp != body.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
    )



    existing_email = db.query(UserModel).filter(UserModel.email == body.email).first()

    if existing_email:
        await delete_registration(body.email)
        raise HTTPException( status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    existing_username = db.query(UserModel).filter( UserModel.username == registration_data["username"]).first()

    if existing_username:
            await  delete_registration(body.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
     # Create user ONLY AFTER OTP verification
    new_user = UserModel(
        name=registration_data["name"],
        username=registration_data["username"],
        email=registration_data["email"],
        password=registration_data["password"],
        is_verified=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Delete OTP + temporary registration data
    await delete_registration(body.email)
    await delete_registration_otp(body.email)
    background_tasks.add_task(
        send_registration_confirmation,
        [new_user.email],
        new_user.name
    )


    return {
        "message": "Registration completed successfully",
        "email": new_user.email,
        "id": new_user.id
    }




async def login_user(body:LoginSchema,db:Session):

        if await is_login_locked(body.email):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts. Try again later."
            )
        user = db.query(UserModel).filter(UserModel.email == body.email).first()
        if not user:
            await increment_login_attempts(body.email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You entered wrong email or password")

        if not user.is_verified: 
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Please verify your email before login")

        if not user.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )

        if not verify_password(body.password , user.password):
            attempts = await increment_login_attempts(body.email)
            if attempts >= LOGIN_MAX_ATTEMPTS:
                await lock_login(body.email)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many failed login attempts. Try again after 10 minutes."
                )

            remaining = LOGIN_MAX_ATTEMPTS - attempts
            raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Wrong email or password. {remaining} attempts remaining."
                    )
        await reset_login_attempts(body.email)

        access_token = create_access_token(user)

        refresh_token, jti = create_refresh_token(user)

        await save_refresh_token(
            jti,
            user.id,
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }



async def is_authenticated(request: Request,   db: Session = Depends(get_db)):

    try:
        authorization = request.headers.get("authorization")

        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are unauthorized"
            )

        token = authorization.split(" ")[-1]

        # Check if token was logged out
        if await is_token_revoked(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        data = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = data.get("_id")

        user = db.query(UserModel).filter(
            UserModel.id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are unauthorized"
            )

        return user

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are unauthorized"
        )


async def forgot_password( body, db: Session, background_tasks: BackgroundTasks):
    is_user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not is_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST ,detail="E-mail does not exist")
    otp = generate_otp()
    if not otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP generation failed")    

    await save_reset_otp(
        body.email,
        otp
    )
    background_tasks.add_task(
        send_reset_password_email,
        [body.email],
        otp
    )

    return {
        "message": "Password reset OTP sent to your email",
        "email": body.email
    }

async def verify_reset_otp(
    body: VerifyResetOTPRequest,
    db: Session
):
    # Check whether user exists
    user = db.query(UserModel).filter(
        UserModel.email == body.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get OTP from Redis
    stored_otp = await get_reset_otp(body.email)

    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired or not found"
        )

    # Compare OTP
    if stored_otp != body.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    # IMPORTANT:
    # Mark OTP as verified in Redis
    await save_reset_verified(body.email)

    # Delete the OTP so it cannot be reused
    await delete_reset_otp(body.email)

    return {
        "message": "OTP verified successfully",
        "email": body.email
    }
          
async def reset_password(
    body: ResetPasswordRequest,
    db: Session
):
    # Check whether OTP was verified
    verified = await get_reset_verified(body.email)

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please verify OTP first"
        )

    # Find user
    user = db.query(UserModel).filter(
        UserModel.email == body.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Hash new password
    user.password = get_password_hash(body.new_password)

    # Save password
    db.commit()
    db.refresh(user)

    # Delete verification permission
    await delete_reset_verified(body.email)

    return {
        "message": "Password reset successfully"
    }

async def logout(request: Request):

    authorization = request.headers.get("authorization")

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token required"
        )

    token = authorization.split(" ")[-1]

    try:
        data = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        exp = data.get("exp")

        if not exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )

        # Calculate remaining JWT lifetime
        remaining_seconds = int(
            exp - datetime.now().timestamp()
        )

        if remaining_seconds <= 0:
            return {
                "message": "Token already expired"
            }

        # Add token to Redis blacklist
        await revoke_token(
            token,
            remaining_seconds
        )

        return {
            "message": "Logout successful"
        }

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def create_access_token(user):
    exp_time = datetime.now() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "_id": user.id,
        "email": user.email,
        "type": "access",
        "exp": exp_time.timestamp()
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(user):

    jti = secrets.token_urlsafe(32)

    exp_time = datetime.now() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "_id": user.id,
        "jti": jti,
        "type": "refresh",
        "exp": exp_time.timestamp()
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token, jti


async def refresh_access_token(
    body: RefreshTokenRequest,
    db: Session
):

    refresh_token = body.refresh_token

    try:

        data = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Make sure this is a refresh token
        if data.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = data.get("_id")
        jti = data.get("jti")

        if not user_id or not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Check Redis
        stored_user_id = await get_refresh_token(jti)

        if not stored_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or revoked"
            )

        # Make sure token belongs to same user
        if str(user_id) != stored_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = db.query(UserModel).filter(
            UserModel.id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # --------------------------------
        # ROTATE REFRESH TOKEN
        # --------------------------------

        # Delete old refresh token
        await delete_refresh_token(jti)

        # Create new access token
        new_access_token = create_access_token(user)

        # Create new refresh token
        new_refresh_token, new_jti = create_refresh_token(user)

        # Store new refresh token
        await save_refresh_token(
            new_jti,
            user.id,
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except InvalidTokenError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

