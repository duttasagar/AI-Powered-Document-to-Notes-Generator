from fastapi import HTTPException, status
from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.document.models import DocumentsModel
from src.document.controller import upload_document
from src.extraction.service import extract_text
from src.notes_ai.service import generate_notes
from src.utils.db import LocalSession


async def generate_document_notes(
    document_id: int,
    user_id: int,
    db: Session
):

    document = (
        db.query(DocumentsModel)
        .filter(
            DocumentsModel.id == document_id,
            DocumentsModel.user_id == user_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text has not been extracted yet"
        )

    notes = await generate_notes(
        document.extracted_text
    )
    document.generated_notes = notes
    db.commit()

    return {
        "document_id": document.id,
        "notes": notes
    }


async def process_document_generation(document_id: int, user_id: int):
    db = LocalSession()
    stage = "extraction"
    try:
        document = (
            db.query(DocumentsModel)
            .filter(
                DocumentsModel.id == document_id,
                DocumentsModel.user_id == user_id,
            )
            .first()
        )
        if not document:
            return

        document.status = "extracting"
        db.commit()

        text = await extract_text(document.file_path, document.file_type)
        if not text.strip():
            document.status = "extraction_failed"
            document.error_message = "No text could be extracted from this file."
            db.commit()
            return

        document.extracted_text = text
        document.status = "generating"
        db.commit()

        stage = "generation"
        document.generated_notes = await generate_notes(text)
        document.status = "completed"
        db.commit()
    except Exception as error:
        print(f"Document generation failed for {document_id}: {error}")
        db.rollback()
        document = (
            db.query(DocumentsModel)
            .filter(
                DocumentsModel.id == document_id,
                DocumentsModel.user_id == user_id,
            )
            .first()
        )
        if document:
            document.status = f"{stage}_failed"
            if isinstance(error, HTTPException):
                document.error_message = str(error.detail)
            elif stage == "extraction":
                document.error_message = "We could not extract readable text from this file."
            else:
                document.error_message = "We could not generate notes for this file. Please try again."
            db.commit()
    finally:
        db.close()


async def upload_and_start_generation(
    files: list[UploadFile],
    user_id: int,
    db: Session,
    background_tasks,
):
    documents = []
    for file in files:
        document = await upload_document(file, user_id, db)
        document.status = "processing"
        db.commit()
        db.refresh(document)
        background_tasks.add_task(process_document_generation, document.id, user_id)
        documents.append(document)

    return documents