import pytesseract
from PIL import Image

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def read_document(image_path):
    
    image = Image.open(image_path)

    text = pytesseract.image_to_string(image)

    return text