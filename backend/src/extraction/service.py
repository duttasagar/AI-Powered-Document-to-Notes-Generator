import os
import pymupdf
import pytesseract

from PIL import Image
from fastapi import HTTPException, status


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


async def extract_text(file_path: str, file_type: str) -> str:

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # PDF
    if file_type == "application/pdf":
        return extract_pdf_text(file_path)

    # Image
    if file_type.startswith("image/"):
        return extract_image_text(file_path)

    # TXT
    if file_type == "text/plain":
        return extract_txt(file_path)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Text extraction is not supported for {file_type}"
    )


def extract_pdf_text(file_path: str) -> str:
    text_parts = []

    with pymupdf.open(file_path) as pdf:
        for page in pdf:
            page_text = page.get_text().strip()
            if page_text:
                text_parts.append(page_text)
                continue

            # Scanned PDFs have no text layer, so OCR their image pages.
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            page_text = pytesseract.image_to_string(image).strip()
            if page_text:
                text_parts.append(page_text)

    return "\n\n".join(text_parts).strip()


def extract_image_text(file_path: str) -> str:
    with Image.open(file_path) as source_image:
        image = source_image.convert("RGB")
        max_dimension = 3000
        if max(image.size) > max_dimension:
            scale = max_dimension / max(image.size)
            image = image.resize(
                (round(image.width * scale), round(image.height * scale)),
                Image.Resampling.LANCZOS,
            )

        return pytesseract.image_to_string(image).strip()


def extract_txt(file_path: str) -> str:

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()