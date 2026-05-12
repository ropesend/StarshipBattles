"""User-tunable knobs for the strategy turn engine.

Loaded from ``output/settings/turn_engine_settings.json``. Missing file
or malformed JSON → defaults silently with a debug log; corrupt settings
must never block turn processing.

PROJ-412 Phase 4: ``progress_callback_interval`` controls how often the
``TurnEngine`` invokes its UI progress callback. The callback always
fires at tick 1 and tick 100; this interval governs the in-between
ticks. Default ``5`` means callbacks fire at ticks 1, 5, 10, …, 95, 100
(21 invocations per turn). Larger values reduce UI redraw cost further
at the price of a chunkier "Tick N / 100" overlay; smaller values
return to a smoother overlay at higher CPU cost.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from game.core.json_utils import load_json
from game.core.paths import Paths

logger = logging.getLogger(__name__)


_DEFAULT_PROGRESS_CALLBACK_INTERVAL = 5


@dataclass(frozen=True)
class TurnEngineSettings:
    """User-tunable strategy turn-engine settings.

    Attributes:
        progress_callback_interval: How often ``TurnEngine`` fires the UI
            progress callback during the 100-tick subturn loop. The
            callback always fires at tick 1 and tick 100; for ticks
            in between, it fires when ``tick % interval == 0``. Minimum
            1 (every tick — pre-Phase-4 behavior); maximum 100 (only
            endpoints). Default ``5``.
    """

    progress_callback_interval: int = _DEFAULT_PROGRESS_CALLBACK_INTERVAL


def load_turn_engine_settings(path: Optional[Path] = None) -> TurnEngineSettings:
    """Load turn-engine settings; fall back to defaults if missing/malformed."""
    settings_path = Path(path) if path is not None else Path(Paths.TURN_ENGINE_SETTINGS_FILE)
    if not settings_path.exists():
        logger.debug(
            "PROJ-412 turn engine settings missing — using defaults: %s",
            settings_path,
        )
        return TurnEngineSettings()
    try:
        data = load_json(str(settings_path), default=None)
    except Exception:  # Intentional broad catch: corrupt settings must not block turn processing
        logger.exception(
            "PROJ-412 turn_engine_settings.json failed to load — using defaults"
        )
        return TurnEngineSettings()
    if not isinstance(data, dict):
        return TurnEngineSettings()

    interval_raw = data.get(
        "progress_callback_interval", _DEFAULT_PROGRESS_CALLBACK_INTERVAL,
    )
    try:
        interval = int(interval_raw)
    except (TypeError, ValueError):
        interval = _DEFAULT_PROGRESS_CALLBACK_INTERVAL
    # Clamp to a sensible range. 1 = every tick (pre-Phase-4 behavior);
    # 100 = endpoints only (tick 1 + tick 100).
    interval = max(1, min(100, interval))

    return TurnEngineSettings(progress_callback_interval=interval)
