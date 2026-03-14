import importlib.util
from functools import lru_cache
import os
from pathlib import Path


def _resolve_speech_engine_path() -> Path:
    custom_path = os.getenv("EDGE_AI_SPEECH_ENGINE_PATH")
    if custom_path:
        candidate = Path(custom_path).expanduser().resolve()
        if candidate.is_file():
            return candidate

    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "Speech-text" / "speech_engine.py",
        base_dir / "speech-text" / "speech_engine.py",
        base_dir / "Speech_text" / "speech_engine.py",
        base_dir / "speech_text" / "speech_engine.py",
        base_dir / "speech_engine.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise RuntimeError("Speech engine not found. Set EDGE_AI_SPEECH_ENGINE_PATH or place speech_engine.py in assistant/Speech-text/")


@lru_cache(maxsize=1)
def _load_speech_engine():
    speech_engine_path = _resolve_speech_engine_path()

    spec = importlib.util.spec_from_file_location("speech_engine_dynamic", speech_engine_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load speech engine module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_voice_input(timeout_seconds: float = 8.0):
    # Helpful for local integration tests when no microphone is available.
    mocked_text = os.getenv("EDGE_AI_VOICE_TEST_TEXT")
    if mocked_text is not None:
        return mocked_text

    module = _load_speech_engine()
    if not hasattr(module, "listen_voice"):
        raise RuntimeError("Speech engine does not expose listen_voice()")

    try:
        return module.listen_voice(timeout_seconds=timeout_seconds)
    except TypeError:
        # Backward compatibility for speech engines that expose listen_voice() without kwargs.
        return module.listen_voice()
