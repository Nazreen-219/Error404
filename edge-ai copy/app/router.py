from pathlib import Path
import sys

from fastapi import APIRouter, HTTPException

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from assistant.ollama_client import ask_llm
from ocr.tesseract_reader import read_document
from translation.translator import translate
from validators.form_validator import validate_form

router = APIRouter()


@router.post("/validate-form")
def validate(data: dict):
    return validate_form(data)


@router.post("/ocr")
def ocr(file_path: str):
    try:
        text = read_document(file_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"text": text}


@router.post("/assistant")
def assistant(question: str):
    response = ask_llm(question)
    return {"response": response}


@router.post("/translate")
def translate_text(text: str, target: str = "hi"):
    return {"translated": translate(text, target)}
