import re


DATE_PATTERN = (
    r"\b(?:"
    r"\d{2}[\/\-.]\d{2}[\/\-.]\d{4}"
    r"|"
    r"\d{2}[\/\-.](?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[\/\-.]\d{4}"
    r")\b"
)


def _clean_value(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip(" :.-\n\t")


def _digits_only(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _extract_id_token(value: str):
    if not value:
        return None
    match = re.search(r"[A-Z0-9][A-Z0-9()/_-]{4,}", value.upper())
    if match:
        return match.group(0)
    return _clean_value(value)


def _normalize_date(value: str) -> str:
    return value.replace(".", "/").replace("-", "/").upper()


def _normalize_ocr_date(value: str):
    if not value:
        return None

    token = value.strip().upper().replace(".", "/").replace("-", "/")
    token = token.replace("I", "1").replace("L", "1").replace("|", "1").replace("O", "0")
    parts = token.split("/")
    if len(parts) != 3:
        return None

    day_str, month_str, year_str = parts[0], parts[1], parts[2]
    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit()):
        return None
    if len(year_str) != 4:
        return None

    day = int(day_str)
    month = int(month_str)
    year = int(year_str)

    # OCR fix for common PAN-DOB confusion: 11 read as 19.
    if month > 12 and month_str.startswith("1"):
        month = 11

    if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
        return None

    return f"{day:02d}/{month:02d}/{year:04d}"


def _normalize_pan_ocr_token(token: str):
    if not token:
        return None

    cleaned = re.sub(r"[^A-Z0-9]", "", token.upper())
    if len(cleaned) != 10:
        return None

    first = cleaned[:5]
    mid = cleaned[5:9]
    last = cleaned[9]

    if not first.isalpha() or not last.isalpha():
        return None

    repl = {
        "I": "1",
        "L": "1",
        "O": "0",
        "Q": "0",
        "Z": "2",
        "S": "5",
        "B": "8",
    }
    mid_norm = "".join(repl.get(ch, ch) for ch in mid)
    if not mid_norm.isdigit():
        return None

    return f"{first}{mid_norm}{last}"


def _find_date(text: str):
    match = re.search(DATE_PATTERN, text or "", re.IGNORECASE)
    if not match:
        return None
    return _normalize_date(match.group())


def _extract_label_value(text: str, label_patterns):
    text = text or ""
    for label in label_patterns:
        match = re.search(label + r"\s*[:\-]?\s*([^\n\r]{1,100})", text, re.IGNORECASE)
        if match:
            value = _clean_value(match.group(1))
            value = re.split(r"\s{2,}", value)[0].strip()
            return value
    return None


def _extract_id_from_labels(text: str, label_patterns):
    text = text or ""
    for label in label_patterns:
        for match in re.finditer(label + r"\s*[:\-]?\s*([^\n\r]{1,100})", text, re.IGNORECASE):
            candidate = _extract_id_token(match.group(1))
            if candidate and re.search(r"\d{3,}", candidate):
                return candidate
    return None


def parse_aadhaar(text: str):
    data = {}
    text = text or ""

    aadhaar_candidates = re.findall(r"(?:\d[\s-]?){12,14}", text)
    for candidate in aadhaar_candidates:
        aadhaar_number = _digits_only(candidate)
        if len(aadhaar_number) == 12:
            data["aadhaar"] = aadhaar_number
            break

    dob = _extract_label_value(text, [r"\bDOB\b", r"\bDoB\b", r"\bdate\s*of\s*birth\b"])
    if dob:
        dob_match = re.search(DATE_PATTERN, dob, re.IGNORECASE)
        if dob_match:
            data["dob"] = _normalize_date(dob_match.group())

    if "dob" not in data:
        date_value = _find_date(text)
        if date_value:
            data["dob"] = date_value

    return data


def parse_pan(text: str):
    data = {}
    original_text = text or ""
    text = original_text.upper()

    pan = re.search(r"\b([A-Z]{5}\s?[0-9]{4}\s?[A-Z])\b", text)
    if pan:
        data["pan_number"] = pan.group(1).replace(" ", "")

    if "pan_number" not in data:
        noisy_pan = re.search(r"\b([A-Z]{5}[0-9ILOZS]{4}[A-Z])\b", text)
        if noisy_pan:
            fixed = _normalize_pan_ocr_token(noisy_pan.group(1))
            if fixed:
                data["pan_number"] = fixed

    # Fallback for OCR-distorted PAN samples (kept separate from strict PAN format).
    pan_label_value = _extract_label_value(text, [r"\bPERMANENT\s+ACCOUNT\s+NUMBER\b", r"\bPAN\b"])
    if pan_label_value and "pan_number" not in data:
        token = re.sub(r"[^A-Z0-9]", "", pan_label_value.upper())
        if len(token) >= 8:
            data["pan_number_raw"] = token[:12]

    token_candidates = re.findall(r"\b[A-Z0-9]{8,12}\b", text)
    if "pan_number" not in data and re.search(r"\b(pan|account|income\s+tax)\b", text, re.IGNORECASE):
        for token in token_candidates:
            if token in {"GOVTOFINDIA", "INCOMETAX", "DEPARTMENT", "PERMANENT", "ACCOUNT", "NUMBER"}:
                continue
            if len(token) == 10 and re.search(r"[A-Z]{5,}", token):
                data["pan_number_raw"] = token
                break

    dob_match = re.search(r"\b(\d{2}[\/\-.][0-9ILO]{2}[\/\-.]\d{4})\b", original_text, re.IGNORECASE)
    if dob_match:
        dob = _normalize_ocr_date(dob_match.group(1))
        if dob:
            data["dob"] = dob

    lines = [line.strip() for line in original_text.splitlines() if line.strip()]
    for idx, line in enumerate(lines):
        cleaned = re.sub(r"[^A-Za-z ]", "", line).strip()
        if not cleaned:
            continue
        lower = cleaned.lower()
        if "income tax" in lower or "department" in lower or "govt" in lower or "india" in lower:
            for j in range(idx + 1, min(idx + 6, len(lines))):
                candidate = re.sub(r"[^A-Za-z ]", "", lines[j]).strip()
                candidate_lower = candidate.lower()
                if (
                    4 <= len(candidate) <= 40
                    and len(candidate.split()) >= 2
                    and all(w not in candidate_lower for w in ["govt", "india", "sample", "immihelp", "department"])
                ):
                    data["name"] = " ".join(word.capitalize() for word in candidate.split())
                    break
            if "name" in data:
                break

    # Fallback name pick near date when header context is noisy.
    if "name" not in data and lines:
        date_idx = None
        for i, line in enumerate(lines):
            if re.search(r"\d{2}[\/\-.][0-9ILO]{2}[\/\-.]\d{4}", line, re.IGNORECASE):
                date_idx = i
                break
        if date_idx is not None:
            for j in range(max(0, date_idx - 12), date_idx):
                candidate = re.sub(r"[^A-Za-z ]", "", lines[j]).strip()
                if 4 <= len(candidate) <= 40 and len(candidate.split()) >= 2:
                    cand_low = candidate.lower()
                    if all(w not in cand_low for w in ["govt", "india", "sample", "immihelp", "department"]):
                        data["name"] = " ".join(word.capitalize() for word in candidate.split())
                        break

    return data


def parse_income_certificate(text: str):
    data = {}
    text = text or ""

    income = re.search(
        r"(?:rs|inr)[\s.:_-]*([0-9][0-9,]*(?:\.[0-9]{1,2})?)\s*(?:/-|only)?",
        text,
        re.IGNORECASE,
    )
    if income:
        data["income"] = income.group(1).replace(",", "")

    certificate_no = _extract_label_value(
        text,
        [r"\bcertificate\s*(?:no|number)\b", r"\bref(?:erence)?\s*(?:no|number)\b"],
    )
    if certificate_no:
        data["certificate_number"] = certificate_no

    return data


def parse_10th_marksheet(text: str):
    data = {}
    text = text or ""

    roll_no = _extract_label_value(text, [r"\broll\s*no\b", r"\broll\s*number\b", r"\banu?kr?mank\b"])
    if roll_no:
        roll_match = re.search(r"[A-Z0-9\/-]{4,}", roll_no, re.IGNORECASE)
        if roll_match:
            candidate = roll_match.group()
            if re.search(r"\d", candidate):
                data["roll_no"] = candidate

    years = re.findall(r"\b(?:19|20)\d{2}\b", text)
    if years:
        data["year"] = years[0]

    percentage = re.search(r"\b(\d{1,2}(?:\.\d{1,2})?)\s?%\b", text)
    if percentage:
        data["percentage"] = f"{percentage.group(1)}%"
    else:
        total_match = re.search(r"\b(\d{2,3})\s*/\s*(\d{2,3})\b", text)
        if total_match:
            obtained = int(total_match.group(1))
            total = int(total_match.group(2))
            if total > 0:
                data["percentage"] = f"{round((obtained / total) * 100, 2)}%"

    return data


def parse_12th_marksheet(text: str):
    return parse_10th_marksheet(text)


def parse_caste_certificate(text: str):
    data = {}
    text = text or ""

    cert_no = _extract_id_from_labels(
        text,
        [
            r"\bcertificate\s*(?:no|number)\b",
            r"\breg(?:istration)?\s*(?:no|number)\b",
            r"\boutward\s*(?:no|number)\b",
            r"\bapplication\s*(?:no|number)\b",
        ],
    )
    if cert_no:
        data["certificate_number"] = cert_no

    caste = re.search(r"\b(sc|st|obc|sebc|general|ews|maratha)\b", text, re.IGNORECASE)
    if caste:
        data["category"] = caste.group().upper()

    issue_date = _extract_label_value(text, [r"\bdate\b", r"\bdate\s*of\s*issue\b"])
    if issue_date:
        issue_date_match = re.search(DATE_PATTERN, issue_date, re.IGNORECASE)
        if issue_date_match:
            data["issue_date"] = _normalize_date(issue_date_match.group())

    return data


def parse_residential_certificate(text: str):
    data = {}
    text = text or ""

    cert_no = _extract_id_from_labels(
        text,
        [r"\bcertificate\s*(?:no|number)\b", r"\breg(?:istration)?\s*(?:no|number)\b"],
    )
    if cert_no:
        data["certificate_number"] = cert_no

    issue_date = re.search(DATE_PATTERN, text, re.IGNORECASE)
    if issue_date:
        data["issue_date"] = _normalize_date(issue_date.group())

    address = _extract_label_value(text, [r"\baddress\b", r"\bresident\s+of\b"])
    if address:
        data["address"] = address

    return data


def parse_birth_certificate(text: str):
    data = {}
    text = text or ""

    dob = _extract_label_value(text, [r"\bdate\s*of\s*birth\b", r"\bdob\b"])
    if dob:
        dob_match = re.search(DATE_PATTERN, dob, re.IGNORECASE)
        if dob_match:
            data["date_of_birth"] = _normalize_date(dob_match.group())

    if "date_of_birth" not in data:
        any_date = re.search(DATE_PATTERN, text, re.IGNORECASE)
        if any_date:
            data["date_of_birth"] = _normalize_date(any_date.group())

    name = _extract_label_value(text, [r"\bname\b", r"\bchild\s*name\b"])
    if name:
        data["name"] = name

    reg_no = _extract_id_from_labels(
        text,
        [
            r"\bregistration\s*(?:no|number)\b",
            r"\breg(?:istration)?\s*(?:no|number)\b",
            r"\bapplication\s*(?:no|number)\b",
        ],
    )
    if reg_no:
        data["registration_number"] = reg_no

    return data


def parse_death_certificate(text: str):
    data = {}
    text = text or ""

    dod = _extract_label_value(text, [r"\bdate\s*of\s*death\b", r"\bdod\b"])
    if dod:
        dod_match = re.search(DATE_PATTERN, dod, re.IGNORECASE)
        if dod_match:
            data["date_of_death"] = _normalize_date(dod_match.group())

    if "date_of_death" not in data:
        any_date = re.search(DATE_PATTERN, text, re.IGNORECASE)
        if any_date:
            data["date_of_death"] = _normalize_date(any_date.group())

    name = _extract_label_value(text, [r"\bname\b", r"\bname\s*of\s*deceased\b"])
    if name:
        data["name"] = name

    reg_no = _extract_id_from_labels(
        text,
        [
            r"\bapplication\s*(?:no|number)\b",
            r"\bapplication\s*n[ou]\b",
            r"\back\s*no\b",
            r"\bregistration\s*(?:no|number)\b",
            r"\breg(?:istration)?\s*(?:no|number)\b",
        ],
    )
    if reg_no:
        data["registration_number"] = reg_no

    return data


def parse_bank_passbook(text: str):
    data = {}
    text = text or ""

    account_no = _extract_label_value(text, [r"\baccount\s*no\b", r"\ba\/c\s*no\b"])
    if account_no:
        account_digits = _digits_only(account_no)
        data["account_number"] = account_digits if len(account_digits) >= 6 else account_no

    cif_no = _extract_label_value(text, [r"\bcif\s*no\b", r"\bcustomer\s*id\b"])
    if cif_no:
        cif_digits = _digits_only(cif_no)
        data["cif_number"] = cif_digits if len(cif_digits) >= 6 else cif_no

    ifsc = _extract_label_value(text, [r"\bifsc\s*code\b", r"\bifsc\b"])
    if ifsc:
        ifsc_match = re.search(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", ifsc.upper())
        data["ifsc"] = ifsc_match.group() if ifsc_match else ifsc.upper()
    else:
        # Fallback when OCR misses IFSC label but captures raw token.
        global_ifsc = re.search(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", text.upper())
        if global_ifsc:
            data["ifsc"] = global_ifsc.group()

    customer_name = _extract_label_value(text, [r"\bcustomer\s*name\b", r"\bname\b"])
    if customer_name:
        data["customer_name"] = customer_name
    else:
        # Some OCR outputs spell "name" as "nane".
        customer_name_alt = _extract_label_value(text, [r"\bcustomer\s*nane\b"])
        if customer_name_alt:
            data["customer_name"] = customer_name_alt

    return data


def parse_ration_card(text: str):
    data = {}
    text = text or ""

    card_id = _extract_label_value(
        text,
        [
            r"\bration\s*card\s*i[do0]\b",
            r"\bcard\s*i[do0]\b",
            r"\bcard\s*number\b",
        ],
    )
    if card_id:
        data["ration_card_id"] = card_id

    head_name = _extract_label_value(
        text,
        [
            r"\bname\s+of\s+head\b",
            r"\bhead\s+of\s+family\b",
            r"\bname\s+of\s+card\s+holder\b",
            r"\bname\s+of\s+father\/husband\b",
        ],
    )
    if head_name:
        data["head_of_family"] = head_name

    phone = _extract_label_value(text, [r"\bphone\s*no\b", r"\bmobile\s*no\b"])
    if phone:
        digits = _digits_only(phone)
        if digits:
            data["phone"] = digits

    return data


def parse_document(document_type: str, text: str):
    parser_map = {
        "aadhaar": parse_aadhaar,
        "pan_card": parse_pan,
        "income_certificate": parse_income_certificate,
        "10th_marksheet": parse_10th_marksheet,
        "12th_marksheet": parse_12th_marksheet,
        "caste_certificate": parse_caste_certificate,
        "residential_certificate": parse_residential_certificate,
        "birth_certificate": parse_birth_certificate,
        "death_certificate": parse_death_certificate,
        "bank_passbook": parse_bank_passbook,
        "ration_card": parse_ration_card,
    }

    parser = parser_map.get(document_type)
    if not parser:
        return {}

    return parser(text or "")
