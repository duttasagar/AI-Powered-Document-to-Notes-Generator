from fastapi import APIRouter, Depends, status,Request,BackgroundTasks
from sqlalchemy.orm import Session
# from src.user.dtos import (UserSchema,LoginSchema,RegisterResponseSchema,UserResponseSchema,VerifyOTPRequest,ForgotPasswordRequest, VerifyResetOTPRequest,
#     ResetPasswordRequest)

from src.user.dtos import (
    UserSchema,
    LoginSchema,
    RegisterResponseSchema,
    UserResponseSchema,
    VerifyOTPRequest,
    ForgotPasswordRequest,
    VerifyResetOTPRequest,
    ResetPasswordRequest,
    RefreshTokenRequest,
    ResendOTPRequest
)

from src.utils.db import get_db
from src.user import controller
user_routes = APIRouter(prefix="/user")


@user_routes.post("/register" ,response_model=RegisterResponseSchema, status_code=status.HTTP_201_CREATED) 
async def register(body:UserSchema, background_tasks: BackgroundTasks, db:Session = Depends(get_db)):
    return await controller.register(body,db,background_tasks)

@user_routes.post("/login" , status_code=status.HTTP_200_OK) 
async def login_user(body:LoginSchema, db:Session = Depends(get_db)):
    return await controller.login_user(body,db)

# @user_routes.get("/is_auth", response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
# async def is_auth(request:Request , db:Session = Depends(get_db)):
#     return controller.is_authenticated(request , db)


@user_routes.get(
    "/is_auth",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK
)
async def is_auth(
    request: Request,
    db: Session = Depends(get_db)
):
    return await controller.is_authenticated(request, db)

@user_routes.post("/verify_otp", status_code=status.HTTP_200_OK)
async def verify_otp(
    body: VerifyOTPRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    return await controller.verify_otp(body, db, background_tasks)

@user_routes.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return await controller.forgot_password(
        body,
        db,
        background_tasks
    )


@user_routes.post("/verify-reset-otp")
async def verify_reset_otp(
    body: VerifyResetOTPRequest,
    db: Session = Depends(get_db)
):
    return await controller.verify_reset_otp(
        body,
        db
    )



@user_routes.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    return await controller.reset_password(
        body,
        db
    )


@user_routes.post("/logout")
async def logout(request: Request):

    return await controller.logout(request)


@user_routes.post("/refresh")
async def refresh_token(
    body: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    return await controller.refresh_access_token(
        body,
        db
    )


@user_routes.post("/resend-otp")
async def resend_otp(
    body: ResendOTPRequest,
    background_tasks: BackgroundTasks
):

    return await controller.resend_registration_otp(
        body,
        background_tasks
    )