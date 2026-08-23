from pydantic import BaseModel

class UserSchema(BaseModel):
    name : str
    username : str
    password : str
    email : str

class UserResponseSchema(BaseModel):
    name : str
    username : str
    email : str
    id : int

class RegisterResponseSchema(BaseModel):
    message: str
    email: str

class LoginSchema(BaseModel):
    password : str
    email : str


class VerifyOTPRequest(BaseModel):
    email: str
    otp: str


# Forgot Password
class ForgotPasswordRequest(BaseModel):
    email: str


class VerifyResetOTPRequest(BaseModel):
    email: str
    otp: str


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ResendOTPRequest(BaseModel):
    email: str