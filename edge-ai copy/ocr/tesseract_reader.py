import pytesseract
from PIL import Image
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def read_document(image_path):
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if not Path(pytesseract.pytesseract.tesseract_cmd).exists():
        raise RuntimeError(
            "Tesseract executable not found at "
            f"{pytesseract.pytesseract.tesseract_cmd}"
        )

    image = Image.open(path)
    text = pytesseract.image_to_string(image, timeout=15)
    return text.strip()
