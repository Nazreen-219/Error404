import re


def validate_form(data: dict):
    data = data or {}
    warnings = []

    required_fields = ("name", "id")
    missing_fields = [field for field in required_fields if not data.get(field)]

    aadhaar = str(data.get("aadhaar", "")).strip()
    if not re.fullmatch(r"\d{12}", aadhaar):
        warnings.append("Invalid Aadhaar number")

    mobile = str(data.get("mobile", "")).strip()
    if not re.fullmatch(r"\d{10}", mobile):
        warnings.append("Invalid mobile number")

    return {
        "valid": not missing_fields and not warnings,
        "missing_fields": missing_fields,
        "warnings": warnings,
        "data": data,
    }
