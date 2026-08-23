import os
import uuid

from fastapi import UploadFile, HTTPException,status
from sqlalchemy.orm import Session
from src.document.models import DocumentsModel
from src.utils.settings import settings

UPLOAD_DIR = "uploads"
MAX_UPLOAD_SIZE = settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024

def list_documents(user_id: int, db: Session):
    return (
        db.query(DocumentsModel)
        .filter(DocumentsModel.user_id == user_id)
        .order_by(DocumentsModel.updated_at.desc())
        .all()
    )

async def upload_document(file:UploadFile, user_id: int, db:Session):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="File name is required")

    extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = {
         ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".txt",
    }

    if extension  not in allowed_extensions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail=f"File type {extension} is not supported")

    user_upload_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_upload_dir, exist_ok=True)

    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(user_upload_dir , unique_filename)

    file_size = 0

    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File is too large. Maximum size is {settings.UPLOAD_MAX_SIZE_MB} MB."
                    )
                buffer.write(chunk)
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
        # 7. Create database record
    document = DocumentsModel(
        user_id=user_id,
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        status="uploaded"
    )
       # 8. Save to database
    db.add(document)
    db.commit()
    db.refresh(document)

    return document

def delete_document(document_id: int, user_id: int, db: Session):
    document = (
        db.query(DocumentsModel)
        .filter(
            DocumentsModel.id == document_id,
            DocumentsModel.user_id == user_id,
        )
        .first()
    )

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()
