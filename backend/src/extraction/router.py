from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.document.models import DocumentsModel
from src.document.dtos import DocumentResponse
from src.extraction.controller import extract_document
from src.user.models import UserModel
from src.user.controller import is_authenticated
from src.utils.db import get_db


extraction_routes = APIRouter(
    prefix="/extraction",
    tags=["Extraction"]
)


@extraction_routes.post(
    "/{document_id}",
    response_model=DocumentResponse
)
async def extract(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(is_authenticated)
):

    document = await extract_document(
        document_id=document_id,
        user_id=current_user.id,
        db=db
    )

    return document