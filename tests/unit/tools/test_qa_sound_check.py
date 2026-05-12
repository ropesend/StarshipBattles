"""Tests for ``Tools/qa_observer/sound_check.py`` pure-logic helpers.

The sound-check script itself is interactive (TTS, mic capture, playback,
console y/n). These tests exercise only the parts that don't touch the
hardware or the user: env parsing, RMS aggregation over recorded frames,
and ``.env`` writeback.
"""

from __future__ import annotations

import importlib.util
import struct
import sys
from pathlib import Path


def _load_sound_check():
    repo_root = Path(__file__).resolve().parents[3]
    script = repo_root / "Tools" / "qa_observer" / "sound_check.py"
    spec = importlib.util.spec_from_file_location("qa_sound_check_under_test", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["qa_sound_check_under_test"] = module
    spec.loader.exec_module(module)
    return module


def test_parse_device_index_returns_none_for_unset() -> None:
    sc = _load_sound_check()
    assert sc.parse_device_index(None) is None


def test_parse_device_index_returns_none_for_blank() -> None:
    sc = _load_sound_check()
    assert sc.parse_device_index("") is None
    assert sc.parse_device_index("   ") is None


def test_parse_device_index_parses_integer() -> None:
    sc = _load_sound_check()
    assert sc.parse_device_index("0") == 0
    assert sc.parse_device_index("7") == 7
    assert sc.parse_device_index("  3  ") == 3


def test_parse_device_index_returns_none_for_non_integer() -> None:
    sc = _load_sound_check()
    assert sc.parse_device_index("default") is None
    assert sc.parse_device_index("1.5") is None


def test_compute_peak_rms_returns_zero_for_no_frames() -> None:
    sc = _load_sound_check()
    assert sc.compute_peak_rms([], sample_width=2) == 0


def test_compute_peak_rms_picks_loudest_frame() -> None:
    sc = _load_sound_check()
    quiet = struct.pack("<4h", 10, -10, 10, -10)
    loud = struct.pack("<4h", 5000, -5000, 5000, -5000)
    silence = struct.pack("<4h", 0, 0, 0, 0)
    peak = sc.compute_peak_rms([quiet, loud, silence], sample_width=2)
    # Loud frame's RMS is 5000; quiet is 10; silence is 0. Peak = 5000.
    assert peak == 5000


def test_write_env_var_creates_file_when_missing(tmp_path: Path) -> None:
    sc = _load_sound_check()
    env_path = tmp_path / ".env"
    sc.write_env_var(env_path, "INPUT_DEVICE_INDEX", "4")
    assert env_path.read_text(encoding="utf-8") == "INPUT_DEVICE_INDEX=4\n"


def test_write_env_var_appends_when_key_missing(tmp_path: Path) -> None:
    sc = _load_sound_check()
    env_path = tmp_path / ".env"
    env_path.write_text("VOICE_THRESHOLD=300\nSILENCE_TIMEOUT=2.0\n", encoding="utf-8")
    sc.write_env_var(env_path, "INPUT_DEVICE_INDEX", "2")
    text = env_path.read_text(encoding="utf-8")
    assert text == "VOICE_THRESHOLD=300\nSILENCE_TIMEOUT=2.0\nINPUT_DEVICE_INDEX=2\n"


def test_write_env_var_updates_existing_key(tmp_path: Path) -> None:
    sc = _load_sound_check()
    env_path = tmp_path / ".env"
    env_path.write_text(
        "VOICE_THRESHOLD=300\nINPUT_DEVICE_INDEX=1\nSILENCE_TIMEOUT=2.0\n",
        encoding="utf-8",
    )
    sc.write_env_var(env_path, "INPUT_DEVICE_INDEX", "5")
    text = env_path.read_text(encoding="utf-8")
    assert text == "VOICE_THRESHOLD=300\nINPUT_DEVICE_INDEX=5\nSILENCE_TIMEOUT=2.0\n"


def test_write_env_var_preserves_unrelated_commented_lines(tmp_path: Path) -> None:
    sc = _load_sound_check()
    env_path = tmp_path / ".env"
    env_path.write_text(
        "# Audio Recording Settings\nVOICE_THRESHOLD=300\n",
        encoding="utf-8",
    )
    sc.write_env_var(env_path, "INPUT_DEVICE_INDEX", "0")
    text = env_path.read_text(encoding="utf-8")
    assert "# Audio Recording Settings" in text
    assert "VOICE_THRESHOLD=300" in text
    assert "INPUT_DEVICE_INDEX=0" in text
