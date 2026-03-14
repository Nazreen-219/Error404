import re


def detect_document_type(text):

    text = text.lower()
    compact = " ".join(text.split())
    upper = text.upper()

    if "uidai" in text or "aadhaar" in text:
        return "aadhaar"

    elif (
        "secondary school examination" in text
        or "matriculation" in text
        or "class x" in text
        or "10th" in text
    ):
        return "10th_marksheet"

    elif (
        "senior school certificate examination" in text
        or "intermediate examination" in text
        or "class xii" in text
        or "12th" in text
    ):
        return "12th_marksheet"

    elif "caste certificate" in text:
        return "caste_certificate"

    elif "residential certificate" in text or "residence certificate" in text:
        return "residential_certificate"

    elif "birth certificate" in text:
        return "birth_certificate"

    elif "death certificate" in text:
        return "death_certificate"

    elif "income certificate" in text:
        return "income_certificate"

    elif (
        "pan card" in text
        or "permanent account number" in text
        or ("income tax department" in compact and "govt. of india" in compact)
        or ("income tax department" in compact and "govt of india" in compact)
        or ("income tax department" in compact and "permanent account" in compact)
        or (re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", upper) is not None)
        or (re.search(r"\b[A-Z]{5}[0-9ILOZS]{4,5}[A-Z]\b", upper) is not None and "india" in text)
        or (
            "india" in text
            and re.search(r"\b[A-Z]{2,}\s+[A-Z]{2,}\b", upper) is not None
            and re.search(r"\b\d{2}/\d{2}/\d{4}\b", text) is not None
            and re.search(r"\b[A-Z0-9]{10,12}\b", upper) is not None
        )
    ):
        return "pan_card"

    elif "ration card" in text or ("nfsa" in text and "card" in text):
        return "ration_card"

    elif (
        ("bank" in text and "ifsc" in text)
        or ("state bank of india" in text and "account" in text)
        or ("state bank of india" in text and "cif" in text)
        or ("cif" in text and "account no" in text)
    ):
        return "bank_passbook"

    else:
        return "unknown"
