from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from sqlalchemy.orm import Session

from src.document.dtos import DocumentResponse
from src.document.models import DocumentsModel
from src.notes_ai.controller import (
    generate_document_notes,
    process_document_generation,
    upload_and_start_generation,
)
from src.user.models import UserModel
from src.user.controller import is_authenticated
from src.utils.db import get_db


ai_routes = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@ai_routes.post("/generate", response_model=list[DocumentResponse])
async def start_multiple_generation(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(is_authenticated),
):
    return await upload_and_start_generation(
        files=files,
        user_id=current_user.id,
        db=db,
        background_tasks=background_tasks,
    )


@ai_routes.post("/generate/{document_id}", response_model=DocumentResponse)
async def start_generation(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(is_authenticated),
):
    document = (
        db.query(DocumentsModel)
        .filter(
            DocumentsModel.id == document_id,
            DocumentsModel.user_id == current_user.id,
        )
        .first()
    )
    if not document:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = "processing"
    db.commit()
    db.refresh(document)
    background_tasks.add_task(process_document_generation, document.id, current_user.id)
    return document


@ai_routes.post("/notes/{document_id}")
async def create_notes(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(is_authenticated)
):

    return await generate_document_notes(
        document_id=document_id,
        user_id=current_user.id,
        db=db
    )