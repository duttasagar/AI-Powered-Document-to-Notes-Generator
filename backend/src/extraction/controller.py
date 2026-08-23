from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.document.models import DocumentsModel
from src.extraction.service import extract_text


async def extract_document(
    document_id: int,
    user_id: int,
    db: Session
):

    # Find document
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

    # Extract text
    text = await extract_text(
        file_path=document.file_path,
        file_type=document.file_type
    )
    if not text.strip():
        document.status = "extraction_failed"
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text could be extracted from this document"
        )

    # if not text:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="No text could be extracted from this document"
    #     )

    # Save extracted text
    document.extracted_text = text
    document.status = "extracted"

    db.commit()
    db.refresh(document)

    return document