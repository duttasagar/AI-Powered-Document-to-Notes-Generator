from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session
from src.user.models import UserModel
from src.document.controller import delete_document, list_documents, upload_document
from src.document.dtos import DocumentResponse
from src.utils.db import get_db
from src.user.controller import is_authenticated


document_routes = APIRouter(
    prefix="/document",
    tags=["Document"]
)


@document_routes.get(
    "",
    response_model=list[DocumentResponse]
)
async def list_user_documents(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(is_authenticated)
):
    return list_documents(user_id=current_user.id, db=db)


@document_routes.post(
    "/upload",
    response_model=DocumentResponse
)
async def upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user : UserModel = Depends(is_authenticated)
):
    document = await upload_document(
        file=file,
        user_id=current_user.id,
        db=db
    )

    return document


@document_routes.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(is_authenticated)
):
    delete_document(document_id=document_id, user_id=current_user.id, db=db)