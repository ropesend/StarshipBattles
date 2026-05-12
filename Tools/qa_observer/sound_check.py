"""QA pre-session sound check.

Verifies the microphone the QA observer will use is actually capturing audio
before the game launches, surfacing the common silent-failure modes (wrong
default input device, mic muted, threshold too high). Flow:

  1. TTS: "Sound check. Please say something after the beep."
  2. Beep.
  3. Record from the configured input device until silence or max duration.
  4. If peak RMS < VOICE_THRESHOLD, the device is bad / muted — offer the
     user a list of input devices and write INPUT_DEVICE_INDEX into the
     observer's .env so observer.py and audio_monitor.py pin to the same
     working device.
  5. Otherwise play the captured audio back and ask the user to confirm.

Invoked by qa_launcher.py before observer/monitor/game spawn. Exits 0 on
pass, 1 on user abort or unrecoverable mic failure.
"""

from __future__ import annotations

import math
import os
import sys
import time
from pathlib import Path

import audioop
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv


CHUNK = 1024
SAMPLE_WIDTH = 2
DTYPE = "int16"
CHANNELS = 1
RATE = 16000
MAX_RECORD_SECONDS = 8.0
BEEP_FREQ_HZ = 880
BEEP_DURATION_S = 0.25


def parse_device_index(raw: str | None) -> int | None:
    """Parse INPUT_DEVICE_INDEX env value into a device id or None.

    Treats unset, blank, and non-integer values as "use the default device"
    rather than raising — the sound check is meant to *recover* from a bad
    env value, not crash on one.
    """
    if raw is None:
        return None
    text = raw.strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def compute_peak_rms(frames: list[bytes], sample_width: int) -> int:
    """Return the loudest per-frame RMS across a recording.

    Per-frame peak (not aggregate RMS) so a brief utterance inside an
    otherwise-silent recording still reads as loud.
    """
    peak = 0
    for frame in frames:
        if not frame:
            continue
        rms = audioop.rms(frame, sample_width)
        if rms > peak:
            peak = rms
    return peak


def write_env_var(env_path: Path, key: str, value: str) -> None:
    """Set ``key=value`` in a dotenv file, updating in place or appending.

    Preserves comments, ordering, and other keys. Creates the file if it
    does not exist. Terminates with a trailing newline.
    """
    new_line = f"{key}={value}"
    if not env_path.exists():
        env_path.write_text(new_line + "\n", encoding="utf-8")
        return

    existing = env_path.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    replaced = False
    for line in existing:
        stripped = line.lstrip()
        if not stripped.startswith("#") and "=" in stripped:
            current_key = stripped.split("=", 1)[0].strip()
            if current_key == key:
                updated.append(new_line)
                replaced = True
                continue
        updated.append(line)
    if not replaced:
        updated.append(new_line)
    env_path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def _speak(text: str) -> None:
    """Speak ``text`` via SAPI5 (Windows) through pyttsx3.

    Failures fall back to printing the line — the sound check should still
    proceed if TTS is unavailable, since the *recording* half is what
    actually verifies the mic.
    """
    print(f"[TTS] {text}")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as exc:  # TTS is a nicety, not a hard requirement
        print(f"[TTS] (engine unavailable: {exc})")


def _play_beep() -> None:
    samples = int(RATE * BEEP_DURATION_S)
    t = np.arange(samples, dtype=np.float32) / RATE
    amplitude = 16000
    wave = (amplitude * np.sin(2 * math.pi * BEEP_FREQ_HZ * t)).astype(np.int16)
    _play_int16(wave)


def _play_raw_pcm(pcm: bytes) -> None:
    """Play raw int16 mono PCM through the default output device."""
    if not pcm:
        return
    samples = np.frombuffer(pcm, dtype=np.int16)
    _play_int16(samples)


def _play_int16(samples: np.ndarray) -> None:
    try:
        sd.play(samples, samplerate=RATE, blocking=True)
    except Exception as exc:
        print(f"[Audio] Playback failed: {exc}")


def _record(device_index: int | None, threshold: int, silence_timeout: float) -> list[bytes]:
    """Record from the configured input until silence or MAX_RECORD_SECONDS.

    Returns the captured frames (may be empty if nothing audible ever
    arrived). Errors opening the stream are caught and surfaced via an
    empty result + console log so the caller can offer the device picker.
    """
    try:
        stream = sd.RawInputStream(
            samplerate=RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=CHUNK,
            device=device_index,
        )
        stream.start()
    except Exception as exc:
        print(f"[Audio] Failed to open input stream: {exc}")
        return []

    frames: list[bytes] = []
    started = time.time()
    voice_started_at: float | None = None
    silence_started_at: float | None = None
    try:
        while True:
            raw, _overflow = stream.read(CHUNK)
            data = bytes(raw)
            frames.append(data)
            rms = audioop.rms(data, SAMPLE_WIDTH)
            now = time.time()
            if rms >= threshold:
                if voice_started_at is None:
                    voice_started_at = now
                silence_started_at = None
            elif voice_started_at is not None:
                if silence_started_at is None:
                    silence_started_at = now
                elif now - silence_started_at >= silence_timeout:
                    break
            if now - started >= MAX_RECORD_SECONDS:
                break
    finally:
        stream.stop()
        stream.close()
    return frames


def _list_input_devices() -> list[tuple[int, str]]:
    devices = sd.query_devices()
    inputs: list[tuple[int, str]] = []
    for idx, info in enumerate(devices):
        if int(info.get("max_input_channels", 0)) > 0:
            inputs.append((idx, str(info.get("name", "<unknown>"))))
    return inputs


def _print_input_devices(current: int | None) -> None:
    default_input_index: int | None
    try:
        default_input_index = int(sd.default.device[0]) if sd.default.device else None
    except Exception:
        default_input_index = None

    print("\nAvailable input devices:")
    for idx, name in _list_input_devices():
        markers = []
        if idx == current:
            markers.append("active")
        if idx == default_input_index:
            markers.append("system default")
        suffix = f"  ({', '.join(markers)})" if markers else ""
        print(f"  [{idx}] {name}{suffix}")


def _prompt_pick_device(env_path: Path, current: int | None) -> int | None:
    """Show device list, take a numeric choice, persist it to .env.

    Returns the new device index, or None if the user aborts.
    """
    _print_input_devices(current)
    raw = input("\nEnter device index to try next (blank to abort): ").strip()
    if not raw:
        return None
    try:
        idx = int(raw)
    except ValueError:
        print(f"'{raw}' is not a number.")
        return None
    valid_ids = {device_id for device_id, _ in _list_input_devices()}
    if idx not in valid_ids:
        print(f"Device {idx} is not an input device.")
        return None
    write_env_var(env_path, "INPUT_DEVICE_INDEX", str(idx))
    print(f"Wrote INPUT_DEVICE_INDEX={idx} to {env_path}")
    return idx


def run_sound_check(env_path: Path) -> int:
    threshold = int(os.getenv("VOICE_THRESHOLD", "300"))
    silence_timeout = float(os.getenv("SILENCE_TIMEOUT", "2.0"))
    device_index = parse_device_index(os.getenv("INPUT_DEVICE_INDEX"))

    print("=== QA Sound Check ===")
    while True:
        device_label = "system default" if device_index is None else f"index {device_index}"
        print(f"\nUsing input device: {device_label}")
        print(f"Voice threshold: {threshold}")

        _speak("Sound check. Please say something after the beep.")
        _play_beep()
        print("[Recording] Speak now...")
        frames = _record(device_index, threshold, silence_timeout)
        peak = compute_peak_rms(frames, SAMPLE_WIDTH)
        print(f"[Recording] Captured {len(frames)} frames. Peak RMS: {peak} (threshold {threshold})")

        if peak < threshold:
            print("No voice detected above the threshold.")
            new_index = _prompt_pick_device(env_path, device_index)
            if new_index is None:
                _speak("Sound check failed. Aborting QA session.")
                return 1
            device_index = new_index
            continue

        _speak("Playing back what I heard.")
        _play_raw_pcm(b"".join(frames))

        answer = input("Did you hear yourself clearly? [y/N]: ").strip().lower()
        if answer == "y":
            _speak("Sound check passed.")
            print("Sound check passed.")
            return 0

        print("Confirmation declined.")
        new_index = _prompt_pick_device(env_path, device_index)
        if new_index is None:
            _speak("Sound check failed. Aborting QA session.")
            return 1
        device_index = new_index


def main() -> int:
    here = Path(__file__).resolve().parent
    env_path = here / ".env"
    load_dotenv(env_path)
    load_dotenv()
    return run_sound_check(env_path)


if __name__ == "__main__":
    sys.exit(main())
