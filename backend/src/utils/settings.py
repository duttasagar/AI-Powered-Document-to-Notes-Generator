from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env" , extra="ignore")

    DB_CONNECTION : str
    GROQ_API_KEY: str
    SECRET_KEY : str
    ALGORITHM :str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    REDIS_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    FRONTEND_URL: str = "http://localhost:5173"
    UPLOAD_MAX_SIZE_MB: int = 10

    MAIL_USERNAME : str
    MAIL_PASSWORD : str
    MAIL_FROM : str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int



settings = Settings()