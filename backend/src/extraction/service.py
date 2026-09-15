import os
import shutil
import logging
import pymupdf
import pytesseract

from PIL import Image, ImageOps, ImageFilter
from fastapi import HTTPException, status


logger = logging.getLogger(__name__)


# Find Tesseract executable
tesseract_cmd = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")

if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


async def extract_text(file_path: str, file_type: str) -> str:

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Prefer the file extension when the upload client supplied a generic MIME type.
    extension_types = {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".txt": "text/plain",
    }
    normalized_type = extension_types.get(
        os.path.splitext(file_path)[1].lower(),
        file_type.split(";", 1)[0].strip().lower(),
    )

    logger.info("Starting text extraction: path=%s type=%s", file_path, normalized_type)

    # PDF
    if normalized_type == "application/pdf":
        return extract_pdf_text(file_path)

    # JPG / JPEG / PNG / other images
    if normalized_type.startswith("image/"):
        return extract_image_text(file_path)

    # TXT
    if normalized_type == "text/plain":
        return extract_txt(file_path)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Text extraction is not supported for {normalized_type}"
    )


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Improve image quality before OCR.
    """

    # Convert to grayscale
    image = image.convert("L")

    # Upscale small images
    min_width = 1800

    if image.width < min_width:
        scale = min_width / image.width

        image = image.resize(
            (
                int(image.width * scale),
                int(image.height * scale)
            ),
            Image.Resampling.LANCZOS
        )

    # Improve contrast
    image = ImageOps.autocontrast(image)

    # Slight sharpening
    image = image.filter(ImageFilter.SHARPEN)

    # Convert to black/white
    image = image.point(
        lambda pixel: 0 if pixel < 180 else 255
    )

    return image


def run_ocr(image: Image.Image) -> str:
    """
    Run Tesseract OCR with settings suitable for documents.
    """

    config = "--oem 3 --psm 6"

    try:
        text = pytesseract.image_to_string(
            image,
            config=config,
            lang="eng"
        )
    except pytesseract.TesseractNotFoundError as error:
        logger.exception("Tesseract is not available for OCR")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OCR is unavailable on the server. Please contact the administrator.",
        ) from error

    return clean_ocr_text(text)


def clean_ocr_text(text: str) -> str:
    """
    Clean common OCR noise without destroying useful text.
    """

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Ignore extremely short garbage lines
        if len(line) <= 1:
            continue

        lines.append(line)

    return "\n".join(lines).strip()


def extract_pdf_text(file_path: str) -> str:

    text_parts = []

    with pymupdf.open(file_path) as pdf:

        for page_number, page in enumerate(pdf):

            # First try normal PDF text extraction
            page_text = page.get_text().strip()

            if page_text:
                text_parts.append(page_text)
                continue

            # No text layer -> scanned PDF -> OCR
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(3, 3),
                alpha=False
            )

            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples
            )

            processed_image = preprocess_image(image)

            page_text = run_ocr(processed_image)

            if page_text:
                text_parts.append(page_text)

    return "\n\n".join(text_parts).strip()


def extract_image_text(file_path: str) -> str:

    try:

        with Image.open(file_path) as source_image:

            image = source_image.convert("RGB")

            processed_image = preprocess_image(image)

            return run_ocr(processed_image)

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image OCR failed: {str(e)}"
        )


def extract_txt(file_path: str) -> str:

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read().strip()










# import os
# import shutil
# import pymupdf
# import pytesseract

# from PIL import Image
# from fastapi import HTTPException, status


# tesseract_cmd = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")
# if tesseract_cmd:
#     pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


# async def extract_text(file_path: str, file_type: str) -> str:

#     if not os.path.exists(file_path):
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="File not found"
#         )

#     # PDF
#     if file_type == "application/pdf":
#         return extract_pdf_text(file_path)

#     # Image
#     if file_type.startswith("image/"):
#         return extract_image_text(file_path)

#     # TXT
#     if file_type == "text/plain":
#         return extract_txt(file_path)

#     raise HTTPException(
#         status_code=status.HTTP_400_BAD_REQUEST,
#         detail=f"Text extraction is not supported for {file_type}"
#     )


# def extract_pdf_text(file_path: str) -> str:
#     text_parts = []

#     with pymupdf.open(file_path) as pdf:
#         for page in pdf:
#             page_text = page.get_text().strip()
#             if page_text:
#                 text_parts.append(page_text)
#                 continue

#             # Scanned PDFs have no text layer, so OCR their image pages.
#             pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
#             image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
#             page_text = pytesseract.image_to_string(image).strip()
#             if page_text:
#                 text_parts.append(page_text)

#     return "\n\n".join(text_parts).strip()


# def extract_image_text(file_path: str) -> str:
#     with Image.open(file_path) as source_image:
#         image = source_image.convert("RGB")
#         max_dimension = 3000
#         if max(image.size) > max_dimension:
#             scale = max_dimension / max(image.size)
#             image = image.resize(
#                 (round(image.width * scale), round(image.height * scale)),
#                 Image.Resampling.LANCZOS,
#             )

#         return pytesseract.image_to_string(image).strip()


# def extract_txt(file_path: str) -> str:

#     with open(file_path, "r", encoding="utf-8") as file:
#         return file.read().strip()