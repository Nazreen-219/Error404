import json
from pathlib import Path
from typing import Callable

import pyaudio
from vosk import KaldiRecognizer, Model


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


def listen_loop(on_text: Callable[[str], None]) -> None:
    base_dir = Path(__file__).resolve().parent
    model_path = _pick_model(base_dir)
    model = Model(str(model_path))

    mic = pyaudio.PyAudio()
    device_index = 4
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
                    print(f"… {partial}")
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()
