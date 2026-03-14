import json
import importlib.util
from pathlib import Path

from assistant.ollama_client import ask_llm, parse_llm_json
from assistant.prompt_templates import build_prompt
from validators.checklist_validator import validate_documents


class _VoiceCaptureDone(Exception):
    pass


def _load_listen_loop():
    speech_engine_path = Path(__file__).resolve().parent / "Speech-text" / "speech_engine.py"
    if not speech_engine_path.is_file():
        raise RuntimeError(f"Speech engine not found at {speech_engine_path}")

    spec = importlib.util.spec_from_file_location("assistant_speech_engine", speech_engine_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load speech engine module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.listen_loop


def get_voice_input() -> str:
    listen_loop = _load_listen_loop()
    captured_text = {"value": ""}

    def _capture_once(text: str):
        if text:
            captured_text["value"] = text
            raise _VoiceCaptureDone

    try:
        listen_loop(_capture_once)
    except _VoiceCaptureDone:
        return captured_text["value"]

    return captured_text["value"]


def process_voice_text(text: str):
    if not text or not text.strip():
        return {
            "speech_text": text,
            "prompt": None,
            "llm_response": "",
            "parsed_output": None,
            "validation": {"error": "No speech detected"},
        }

    prompt = build_prompt(text)
    llm_response = ask_llm(prompt)
    try:
        parsed_output = parse_llm_json(llm_response)
        validation = validate_documents(json.dumps(parsed_output))
    except ValueError as exc:
        return {
            "speech_text": text,
            "prompt": prompt,
            "llm_response": llm_response,
            "parsed_output": None,
            "validation": {"error": str(exc)},
        }

    return {
        "speech_text": text,
        "prompt": prompt,
        "llm_response": llm_response,
        "parsed_output": parsed_output,
        "validation": validation,
    }
def process_voice_input():
    text = get_voice_input()
    return process_voice_text(text)


def handle_text(text: str):
    result = process_voice_text(text)

    print(f"\nUser said: {result['speech_text']}")
    print("\nLLM Raw Response:")
    print(result["llm_response"])
    print("\nValidation Result:")
    print(result["validation"])
    if result["parsed_output"] is not None:
        print("\nParsed Output:")
        print(result["parsed_output"])


if __name__ == "__main__":
    _load_listen_loop()(handle_text)
