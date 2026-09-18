from __future__ import annotations

import io
import tempfile
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

from jarvis.config import Settings
from jarvis.xai import XAI

RATE = 16_000


def record(seconds: float = 5.0) -> bytes:
    frames = int(RATE * seconds)
    print(f"ouvindo {seconds:.0f}s…", flush=True)
    audio = sd.rec(frames, samplerate=RATE, channels=1, dtype="int16")
    sd.wait()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(np.asarray(audio).tobytes())
    return buf.getvalue()


def play_mp3(data: bytes) -> None:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as tmp:
        tmp.write(data)
        tmp.flush()
        path = Path(tmp.name)
        try:
            samples, rate = sf.read(path)
            sd.play(samples, rate)
            sd.wait()
            return
        except Exception:
            pass
    # fallback: write wav-less, try ffplay/afplay
    import shutil
    import subprocess

    player = shutil.which("ffplay") or shutil.which("afplay") or shutil.which("mpg123")
    if not player:
        raise RuntimeError("não há player de áudio (ffplay/afplay/mpg123) nem soundfile decodificou o mp3")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(data)
        name = tmp.name
    try:
        cmd = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", name] if "ffplay" in player else [player, name]
        subprocess.run(cmd, check=False)
    finally:
        Path(name).unlink(missing_ok=True)


def listen_and_transcribe(xai: XAI, seconds: float = 5.0) -> str:
    wav = record(seconds)
    return xai.transcribe(wav)


def speak(settings: Settings, xai: XAI, text: str) -> None:
    audio = xai.tts(text)
    play_mp3(audio)
