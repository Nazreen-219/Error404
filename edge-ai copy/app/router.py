from pathlib import Path
import sys

from fastapi import APIRouter, HTTPException

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from assistant.ollama_client import ask_llm
from ocr.document_matcher import process_document
from translation.translator import translate
from validators.form_validator import validate_form

router = APIRouter()


@router.post("/validate-form")
def validate(data: dict):
    return validate_form(data)


@router.post("/ocr")
def ocr(file_path: str):
    try:
        result = process_document(file_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    text = result.get("raw_text", "") if isinstance(result, dict) else str(result)
    document_type = result.get("document_type", "unknown") if isinstance(result, dict) else "unknown"
    extracted_data = result.get("extracted_data", {}) if isinstance(result, dict) else {}

    return {
        "document_type": document_type,
        "extracted_data": extracted_data,
        "raw_text": text,
        "text": text,
    }


@router.post("/assistant")
def assistant(question: str):
    response = ask_llm(question)
    return {"response": response}


@router.post("/translate")
def translate_text(text: str, target: str = "hi"):
    return {"translated": translate(text, target)}

#for voice assistant
from assistant.voice_assistant import get_voice_input

@router.post("/voice-input")
def voice():
    try:
        text = get_voice_input()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "speech_text": text
    }
