"""PROJ-312 Phase 4 — Replay sidecar persistence.

A single owner of replay file IO, scoped to a save folder. Lives in the
strategy layer because saves are a strategy-layer concern; the simulation
layer must not import from here.

The store implements ``IReplayCaptureSink`` so registering it via
``set_default_capture_sink`` (Phase 4 wiring) hooks Phase 3's capture
points end-to-end.

Sidecar layout::

    output/saves/<save>/
    ├── save_metadata.json
    ├── turns/turn_N.json
    ├── designs/
    └── replays/                          ← created lazily on first capture
        ├── replay_<uuid>.json
        └── ...

Settings: ``output/settings/replay_settings.json`` carries
``max_replays_per_save`` (default 50). Missing file falls back to defaults
without raising.

Ring-buffer eviction is **write-then-evict**: a new replay is fully
serialized to disk via the existing atomic ``save_json`` helper, then —
and only then — the oldest replays beyond the cap are deleted.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from game.core.json_utils import load_json, save_json
from game.core.paths import Paths
from game.simulation.replay import (
    REPLAY_SCHEMA_VERSION,
    ReplayCaptureContext,
    ReplayOutcome,
    ReplayRecord,
    ReplaySpec,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReplaySettings:
    """User-tunable replay knobs.

    Loaded from ``output/settings/replay_settings.json``. Missing file
    or malformed JSON → defaults silently with a debug log.

    PROJ-354B Phase 1: ``verification_enabled`` and
    ``verification_queue_cap`` control the background end-state
    verification coordinator. Both default to safe values that turn the
    feature on with a small bounded queue.
    """

    max_replays_per_save: int = 50
    verification_enabled: bool = True
    verification_queue_cap: int = 16


def load_replay_settings(path: Optional[Path] = None) -> ReplaySettings:
    """Load settings; fall back to defaults if missing/malformed."""
    settings_path = Path(path) if path is not None else Path(Paths.REPLAY_SETTINGS_FILE)
    if not settings_path.exists():
        logger.debug("PROJ-312 replay settings missing — using defaults: %s", settings_path)
        return ReplaySettings()
    try:
        data = load_json(str(settings_path), default=None)
    except Exception:  # Intentional broad catch: corrupt settings must not block capture
        logger.exception("PROJ-312 replay_settings.json failed to load — using defaults")
        return ReplaySettings()
    if not isinstance(data, dict):
        return ReplaySettings()
    cap_raw = data.get("max_replays_per_save", 50)
    try:
        cap = int(cap_raw)
    except (TypeError, ValueError):
        cap = 50
    # PROJ-354B Phase 1.1: verification settings.
    verification_enabled = bool(data.get("verification_enabled", True))
    queue_cap_raw = data.get("verification_queue_cap", 16)
    try:
        queue_cap = int(queue_cap_raw)
    except (TypeError, ValueError):
        queue_cap = 16
    return ReplaySettings(
        max_replays_per_save=max(1, cap),
        verification_enabled=verification_enabled,
        verification_queue_cap=max(1, queue_cap),
    )


# ---------------------------------------------------------------------------
# ReplayStore
# ---------------------------------------------------------------------------


@dataclass
class _PendingCapture:
    """In-memory state between ``on_battle_started`` and ``on_battle_ended``."""

    replay_id: str
    spec: ReplaySpec
    context: ReplayCaptureContext


class ReplayStore:
    """Filesystem-backed replay sink + reader.

    Use ``set_save_root(<save_path>)`` after a save folder is loaded /
    created. Use ``clear_save_root()`` when no save is active. While the
    save root is unset, capture is a no-op (started/ended calls discard).

    Implements ``IReplayCaptureSink``::

        on_battle_started(replay_spec, *, context) -> str
        on_battle_ended(replay_id, replay_outcome) -> None
    """

    REPLAY_SUBDIR = "replays"
    REPLAY_FILE_PREFIX = "replay_"
    REPLAY_FILE_SUFFIX = ".json"

    def __init__(
        self,
        *,
        settings: Optional[ReplaySettings] = None,
        save_root: Optional[Path] = None,
        json_writer: Callable[[str, dict], None] = save_json,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self._settings = settings or load_replay_settings()
        self._save_root: Optional[Path] = Path(save_root) if save_root else None
        self._json_writer = json_writer
        self._clock = clock
        self._pending: Dict[str, _PendingCapture] = {}

    # ---- save lifecycle ----

    def set_save_root(self, save_root: Path) -> None:
        """Point the store at a save folder; lazily creates ``replays/``."""
        self._save_root = Path(save_root)
        self._ensure_replay_dir()

    def clear_save_root(self) -> None:
        """Detach the store from any save (main-menu state)."""
        self._save_root = None
        self._pending.clear()

    @property
    def save_root(self) -> Optional[Path]:
        return self._save_root

    def _replay_dir(self) -> Optional[Path]:
        if self._save_root is None:
            return None
        return self._save_root / self.REPLAY_SUBDIR

    def _ensure_replay_dir(self) -> Optional[Path]:
        rd = self._replay_dir()
        if rd is None:
            return None
        rd.mkdir(parents=True, exist_ok=True)
        return rd

    # ---- IReplayCaptureSink ----

    def on_battle_started(
        self,
        replay_spec: ReplaySpec,
        *,
        context: ReplayCaptureContext,
    ) -> str:
        """Stash the spec in memory; return a stable replay_id.

        When no save root is set, returns ``""`` so the engine treats it as
        "no capture" and skips the matching ``on_battle_ended``.
        """
        if self._save_root is None:
            return ""
        replay_id = uuid.uuid4().hex
        self._pending[replay_id] = _PendingCapture(
            replay_id=replay_id, spec=replay_spec, context=context
        )
        return replay_id

    def on_battle_ended(
        self,
        replay_id: str,
        outcome: ReplayOutcome,
    ) -> None:
        """Persist the matched ``ReplayRecord`` and run ring-buffer eviction."""
        pending = self._pending.pop(replay_id, None)
        if pending is None:
            logger.debug(
                "PROJ-312 on_battle_ended: no pending capture for replay_id=%s",
                replay_id,
            )
            return
        record = self._build_record(pending, outcome)
        self.persist(record)

    # ---- write/read ----

    def persist(self, record: ReplayRecord) -> Optional[Path]:
        """Atomic-write the record then evict excess. Returns the file path
        on success, ``None`` if no save root is set."""
        rd = self._ensure_replay_dir()
        if rd is None:
            return None
        path = rd / f"{self.REPLAY_FILE_PREFIX}{record.replay_id}{self.REPLAY_FILE_SUFFIX}"
        try:
            self._json_writer(str(path), record.to_dict())
        except Exception:  # Intentional broad catch: capture must not crash
            logger.exception("PROJ-312 replay persist failed: %s", path)
            return None
        # Write-then-evict: never delete before the new file is on disk.
        self._evict_excess()
        return path

    def list(self) -> List[ReplayRecord]:
        """Return all records sorted by ``captured_at`` descending.
        Skips corrupt and version-mismatched files with a debug log
        (graceful degradation per `race_caption_loader.py`)."""
        rd = self._replay_dir()
        if rd is None or not rd.exists():
            return []
        records: List[ReplayRecord] = []
        for p in sorted(rd.glob(f"{self.REPLAY_FILE_PREFIX}*{self.REPLAY_FILE_SUFFIX}")):
            rec = self._safe_load(p)
            if rec is None:
                continue
            if rec.schema_version != REPLAY_SCHEMA_VERSION:
                logger.debug(
                    "PROJ-312 skipping replay with version=%s (current=%s): %s",
                    rec.schema_version, REPLAY_SCHEMA_VERSION, p,
                )
                continue
            records.append(rec)
        records.sort(key=lambda r: r.captured_at, reverse=True)
        return records

    def load(self, replay_id: str) -> Optional[ReplayRecord]:
        rd = self._replay_dir()
        if rd is None:
            return None
        path = rd / f"{self.REPLAY_FILE_PREFIX}{replay_id}{self.REPLAY_FILE_SUFFIX}"
        if not path.exists():
            return None
        rec = self._safe_load(path)
        if rec is None or rec.schema_version != REPLAY_SCHEMA_VERSION:
            return None
        return rec

    def delete(self, replay_id: str) -> bool:
        rd = self._replay_dir()
        if rd is None:
            return False
        path = rd / f"{self.REPLAY_FILE_PREFIX}{replay_id}{self.REPLAY_FILE_SUFFIX}"
        if path.exists():
            try:
                path.unlink()
                return True
            except OSError:
                logger.exception("PROJ-312 failed to delete replay: %s", path)
                return False
        return False

    # ---- helpers ----

    def _safe_load(self, path: Path) -> Optional[ReplayRecord]:
        try:
            data = load_json(str(path), default=None)
        except Exception:  # Intentional broad catch: corrupt files must be skipped, not raised
            logger.debug("PROJ-312 replay load failed (corrupt JSON): %s", path)
            return None
        if not isinstance(data, dict):
            return None
        try:
            return ReplayRecord.from_dict(data)
        except Exception:  # Intentional broad catch: schema mismatches must be skipped
            logger.debug("PROJ-312 replay schema mismatch: %s", path)
            return None

    def _evict_excess(self) -> int:
        """Delete the oldest replays beyond ``max_replays_per_save``.
        Returns the count deleted."""
        rd = self._replay_dir()
        if rd is None or not rd.exists():
            return 0
        files = sorted(
            rd.glob(f"{self.REPLAY_FILE_PREFIX}*{self.REPLAY_FILE_SUFFIX}"),
            key=lambda p: p.stat().st_mtime,
        )
        cap = self._settings.max_replays_per_save
        excess = max(0, len(files) - cap)
        deleted = 0
        for p in files[:excess]:
            try:
                p.unlink()
                deleted += 1
            except OSError:
                logger.exception("PROJ-312 ring buffer eviction failed: %s", p)
        return deleted

    def _build_record(
        self,
        pending: _PendingCapture,
        outcome: ReplayOutcome,
    ) -> ReplayRecord:
        ctx = pending.context
        captured_at = ctx.captured_at or self._clock().isoformat()
        return ReplayRecord(
            schema_version=REPLAY_SCHEMA_VERSION,
            replay_id=pending.replay_id,
            captured_at=captured_at,
            sector_name=ctx.sector_name,
            sector_coords=ctx.sector_coords,
            turn_number=ctx.turn_number,
            participating_empires=tuple(ctx.participating_empires),
            components_registry_hash=ctx.components_registry_hash,
            spec=pending.spec,
            outcome=outcome,
        )


__all__ = ["ReplaySettings", "ReplayStore", "load_replay_settings"]
