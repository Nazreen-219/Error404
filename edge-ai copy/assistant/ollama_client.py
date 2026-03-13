import json
from urllib import error, request


def ask_llm(question: str, model: str = "llama3.2"):
    payload = json.dumps(
        {
            "model": model,
            "prompt": question,
            "stream": False,
        }
    ).encode("utf-8")
    req = request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except error.URLError:
        return "Ollama is not reachable on http://127.0.0.1:11434."

    return data.get("response", "").strip()
