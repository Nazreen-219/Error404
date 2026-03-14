import json
import time
from pathlib import Path
from typing import Callable


def _pick_model(base_dir: Path) -> Path:
    # Prefer a larger Hindi model if available for better accuracy
    preferred = [
        "vosk-model-hi-0.22",
        "vosk-model-hi-0.21",
        "vosk-model-small-hi-0.22",
        "vosk-model-small-hi-0.21",
    ]
    model_dir = base_dir / "model"
    for name in preferred:
        candidate = model_dir / name
        if candidate.is_dir():
            return candidate

    # Fallback to any first directory inside model/
    for entry in model_dir.iterdir():
        if entry.is_dir():
            return entry

    return model_dir


def _init_recognizer():
    try:
        import pyaudio
        from vosk import KaldiRecognizer, Model
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Voice dependencies are missing. Install packages from assistant/Speech-text/requirements.txt"
        ) from exc

    base_dir = Path(__file__).resolve().parent
    model_path = _pick_model(base_dir)
    if not model_path.is_dir():
        raise RuntimeError(f"Vosk model directory not found: {model_path}")

    model = Model(str(model_path))
    mic = pyaudio.PyAudio()

    try:
        device_info = mic.get_default_input_device_info()
        device_index = int(device_info.get("index", 0))
    except Exception:
        device_index = 0
        device_info = mic.get_device_info_by_index(device_index)

    sample_rate = int(device_info.get("defaultSampleRate", 16000))

    recognizer = KaldiRecognizer(model, sample_rate)
    recognizer.SetWords(True)
    recognizer.SetMaxAlternatives(3)

    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=4096,
    )

    return mic, stream, recognizer


def listen_voice(timeout_seconds: float = 8.0) -> str:
    mic, stream, recognizer = _init_recognizer()
    stream.start_stream()

    deadline = time.monotonic() + timeout_seconds
    last_partial = ""

    try:
        while time.monotonic() < deadline:
            data = stream.read(4096, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    return text
            else:
                partial = json.loads(recognizer.PartialResult()).get("partial", "").strip()
                if partial:
                    last_partial = partial

        final_text = json.loads(recognizer.FinalResult()).get("text", "").strip()
        return final_text or last_partial
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()


def listen_loop(on_text: Callable[[str], None]) -> None:
    mic, stream, recognizer = _init_recognizer()

    stream.start_stream()
    print("Hindi Voice Assistant Running...")

    try:
        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                on_text(text)
            else:
                # Use partial results for more responsive feedback
                partial = json.loads(recognizer.PartialResult()).get("partial", "")
                if partial:
                    print(f"... {partial}")
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()
