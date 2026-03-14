import re
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image

try:
    import pillow_avif  # noqa: F401  # Enables AVIF support for Pillow when installed.
except Exception:
    pillow_avif = None

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log"}
IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".tif",
    ".webp",
    ".gif",
    ".avif",
}


def extract_aadhaar_data(text: str):
    data = {
        "name": None,
        "dob": None,
        "aadhaar": None,
    }

    aadhaar_match = re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text)
    if aadhaar_match:
        data["aadhaar"] = aadhaar_match.group().replace(" ", "")

    dob_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    if dob_match:
        data["dob"] = dob_match.group()

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if len(line) <= 3:
            continue

        lower_line = line.lower()
        if any(x in lower_line for x in ["government", "india", "uidai", "dob"]):
            continue

        if re.fullmatch(r"[A-Za-z ]+", line):
            data["name"] = line
            break

    return data


def _load_image_bgr(path: Path):
    # First attempt via OpenCV (fast path).
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is not None:
        return img

    # Fallback via Pillow for formats OpenCV may fail to decode (e.g., AVIF on some builds).
    try:
        pil_img = Image.open(path).convert("RGB")
        arr = np.array(pil_img)
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    except Exception as exc:
        raise RuntimeError(f"Unable to read image data from: {path}") from exc


def _resize_for_ocr(gray: np.ndarray):
    h, w = gray.shape[:2]
    longest = max(h, w)
    if longest < 1800:
        scale = 1800.0 / float(longest)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    return gray


def _preprocess_variants(img_bgr: np.ndarray):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = _resize_for_ocr(gray)

    # Denoise then create multiple binarization variants for noisy scans/photos.
    denoised = cv2.fastNlMeansDenoising(gray, None, h=12, templateWindowSize=7, searchWindowSize=21)

    otsu = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    adaptive = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    # Morph cleanup variants.
    kernel = np.ones((2, 2), np.uint8)
    morph_open = cv2.morphologyEx(otsu, cv2.MORPH_OPEN, kernel)
    morph_close = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel)

    return [gray, otsu, adaptive, morph_open, morph_close]


def _score_text(text: str) -> int:
    if not text:
        return 0
    alnum = sum(ch.isalnum() for ch in text)
    lines = sum(1 for line in text.splitlines() if line.strip())
    return alnum + (lines * 5)


def _ocr_with_configs(image_obj, timeout=20):
    configs = [
        "--oem 3 --psm 6",
        "--oem 3 --psm 4",
        "--oem 3 --psm 11",
    ]

    best_text = ""
    best_score = -1

    for cfg in configs:
        try:
            text = pytesseract.image_to_string(image_obj, config=cfg, timeout=timeout).strip()
        except Exception:
            continue

        score = _score_text(text)
        if score > best_score:
            best_score = score
            best_text = text

    return best_text


def ocr_image_file(path: Path) -> str:
    img_bgr = _load_image_bgr(path)
    variants = _preprocess_variants(img_bgr)

    best_text = ""
    best_score = -1

    for variant in variants:
        text = _ocr_with_configs(variant, timeout=20)
        score = _score_text(text)
        if score > best_score:
            best_score = score
            best_text = text

    return best_text.strip()


def ocr_pdf_file(path: Path) -> str:
    try:
        from pdf2image import convert_from_path
    except ImportError as exc:
        raise RuntimeError(
            "PDF OCR requires pdf2image. Install it with: pip install pdf2image"
        ) from exc

    pages = convert_from_path(str(path), dpi=300)
    page_text = []

    for page in pages:
        page_arr = np.array(page)
        page_bgr = cv2.cvtColor(page_arr, cv2.COLOR_RGB2BGR)
        variants = _preprocess_variants(page_bgr)

        best_page_text = ""
        best_score = -1
        for variant in variants:
            text = _ocr_with_configs(variant, timeout=25)
            score = _score_text(text)
            if score > best_score:
                best_score = score
                best_page_text = text

        if best_page_text:
            page_text.append(best_page_text)

    return "\n".join(page_text).strip()


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def read_document(file_path):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not Path(pytesseract.pytesseract.tesseract_cmd).exists():
        raise RuntimeError(
            "Tesseract executable not found at "
            f"{pytesseract.pytesseract.tesseract_cmd}"
        )

    suffix = path.suffix.lower()

    if suffix in TEXT_EXTENSIONS:
        text = read_text_file(path)
    elif suffix == ".pdf":
        text = ocr_pdf_file(path)
    elif suffix in IMAGE_EXTENSIONS:
        text = ocr_image_file(path)
    else:
        # Last-attempt fallback: try loading via PIL and OCR it.
        try:
            image = Image.open(path)
            text = _ocr_with_configs(image, timeout=20).strip()
        except Exception as exc:
            raise RuntimeError(
                f"Unsupported file type: {suffix or 'unknown'}. "
                "Supported: images, PDF, and text files."
            ) from exc

    structured_data = extract_aadhaar_data(text)

    return {
        "raw_text": text,
        "extracted_data": structured_data,
    }
