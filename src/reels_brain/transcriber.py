from pathlib import Path

from faster_whisper import WhisperModel

from .config import WHISPER_COMPUTE, WHISPER_DEVICE, WHISPER_MODEL

_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        print(f"   (nahrávam whisper model {WHISPER_MODEL} — prvýkrát sa sťahuje, ~1.6 GB)")
        _model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE)
    return _model


def transcribe(audio: Path) -> str:
    segments, _info = _get_model().transcribe(str(audio), vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments)
    return " ".join(text.split())
