from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from src.auth import controller
from src.auth.controller import oauth
from src.utils.settings import settings
from src.utils.db import get_db


auth_routes = APIRouter(prefix="/auth")


@auth_routes.get("/google/login")
async def google_login(request: Request):

    return await oauth.google.authorize_redirect(
        request,
        settings.GOOGLE_REDIRECT_URI
    )


@auth_routes.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):

    return await controller.google_callback(
        request,
        db
    )