from ocr.document_classifier import detect_document_type
from ocr.parser import parse_document
from ocr.tesseract_reader import read_document


def process_document(file_path):
    ocr_result = read_document(file_path)

    # read_document currently returns dict for OCR; keep a fallback in case this changes.
    if isinstance(ocr_result, dict):
        text = ocr_result.get("raw_text", "")
        base_extracted = ocr_result.get("extracted_data", {}) or {}
    else:
        text = str(ocr_result)
        base_extracted = {}

    doc_type = detect_document_type(text)
    parsed_data = parse_document(doc_type, text)

    extracted_data = {**base_extracted, **parsed_data}

    return {
        "document_type": doc_type,
        "extracted_data": extracted_data,
        "raw_text": text,
    }
