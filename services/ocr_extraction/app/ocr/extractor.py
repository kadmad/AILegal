import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io

def extract_text_from_file(file_bytes: bytes, file_type: str) -> str:
    if file_type.lower() == "pdf":
        images = convert_from_bytes(file_bytes)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
        return text.strip()
    else:  # assume image   
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image)
