"""
OCR Extraction Service — text extractor.

Provides a single public function that accepts raw file bytes and a file type
string, then uses Tesseract OCR (via pytesseract) to return extracted text.

PDF handling converts each page to a PIL image first (via pdf2image / Poppler)
before passing it to Tesseract.  Non-PDF files are treated as images directly.
"""

import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io


def extract_text_from_file(file_bytes: bytes, file_type: str) -> str:
    """
    Extract text from a file using Tesseract OCR.

    For PDFs, each page is rendered to an image by pdf2image (which internally
    calls Poppler's ``pdftoppm``) and then fed to Tesseract individually.
    For image files (PNG, JPG, TIFF, etc.) the bytes are decoded directly by
    Pillow and passed straight to Tesseract.

    Args:
        file_bytes: Raw binary content of the file.
        file_type: File extension (case-insensitive), e.g. ``"pdf"``, ``"png"``,
                   ``"jpg"``.

    Returns:
        str: The full extracted text, with pages separated by newlines (PDF)
             or as a single string (image).  Trailing whitespace is stripped
             for PDFs.
    """
    if file_type.lower() == "pdf":
        # Convert every PDF page to a PIL image, then OCR each page
        images = convert_from_bytes(file_bytes)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
        return text.strip()
    else:
        # For all image formats, decode with Pillow and run OCR directly
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image)
