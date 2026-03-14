import json

REQUIRED_DOCS = {
    "sand mining": [
        "processing_fee",
        "emp",
        "land_document",
        "gram_panchayat_noc",
        "forest_noc",
        "kml_file"
    ]
}


def validate_documents(llm_response):

    try:
        data = json.loads(llm_response)
    except:
        return {"error": "Invalid JSON from LLM"}

    app_type = data.get("application_type", "")

    present = data.get("documents_present", [])

    required = REQUIRED_DOCS.get(app_type, [])

    missing = [doc for doc in required if doc not in present]

    return {
        "application_type": app_type,
        "missing_documents": missing,
        "risk": "HIGH" if len(missing) > 2 else "MEDIUM"
    }