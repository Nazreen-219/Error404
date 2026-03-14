import json
import re

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_llm(prompt: str):

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()

    return data.get("response", "").strip()


def parse_llm_json(response_text: str):
    cleaned = response_text.strip()

    if not cleaned:
        raise ValueError("LLM returned an empty response")

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"LLM did not return valid JSON: {exc}. Raw response: {cleaned}") from exc
