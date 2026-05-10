"""PROJ-354B Phase 2 — Sidecar JSON for replay verification results.

A sidecar lives next to its replay record at
``output/saves/<save>/replays/replay_<id>.verification.json``. Mutating
the immutable replay record JSON to add status would break the atomic-
write semantics; the sidecar pattern keeps the verification lifecycle
independent.

Schema is versioned independently of ``REPLAY_SCHEMA_VERSION`` because
the verification format may evolve (e.g., new status values, enriched
diff format) without invalidating captured replays.

Lifecycle:
    * Written by the verification coordinator after a verification
      attempt completes (PASSED/FAILED/ERROR/SKIPPED_*).
    * Deleted by ``ReplayStore.delete`` and ``_evict_excess`` so the
      sidecar can never outlive its replay record.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from game.core.json_utils import load_json, save_json

logger = logging.getLogger(__name__)


REPLAY_VERIFICATION_SCHEMA_VERSION = "1.0.0"

SIDECAR_FILE_PREFIX = "replay_"
SIDECAR_FILE_SUFFIX = ".verification.json"


class VerificationStatus(str, Enum):
    """Lifecycle status of one verification attempt."""

    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    SKIPPED_QUEUE_FULL = "SKIPPED_QUEUE_FULL"
    SKIPPED_DISABLED = "SKIPPED_DISABLED"


class VerificationSource(str, Enum):
    """Where the verification was launched from.

    ``VISUAL_REPLAY`` is reserved for a future opt-in mode where the
    user clicking Replay in the Event Log also re-verifies; not in
    scope for PROJ-354B.
    """

    BACKGROUND = "BACKGROUND"
    VISUAL_REPLAY = "VISUAL_REPLAY"


@dataclass(frozen=True)
class VerificationSidecar:
    """The persisted-on-disk form of a verification result.

    ``diff`` is a list of dicts (each ``{"path": [...], "expected":
    ..., "actual": ...}``) so the JSON shape stays free of dataclass
    types. ``error`` is ``{"type": str, "message": str}`` for
    infrastructure-level failures (e.g., ship_builder raised).
    """

    replay_id: str
    schema_version: str
    status: str
    source: str
    verified_at: str
    duration_ms: Optional[int]
    diff: Optional[List[Dict[str, Any]]]
    error: Optional[Dict[str, str]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "schema_version": self.schema_version,
            "status": self.status,
            "source": self.source,
            "verified_at": self.verified_at,
            "duration_ms": self.duration_ms,
            "diff": self.diff,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VerificationSidecar":
        return cls(
            replay_id=str(data["replay_id"]),
            schema_version=str(data["schema_version"]),
            status=str(data["status"]),
            source=str(data["source"]),
            verified_at=str(data["verified_at"]),
            duration_ms=(
                int(data["duration_ms"]) if data.get("duration_ms") is not None else None
            ),
            diff=data.get("diff"),
            error=data.get("error"),
        )


def sidecar_path_for_replay(replay_dir: Path, replay_id: str) -> Path:
    """Pure path helper — does not touch the filesystem."""
    return Path(replay_dir) / f"{SIDECAR_FILE_PREFIX}{replay_id}{SIDECAR_FILE_SUFFIX}"


def write_verification_sidecar(
    replay_dir: Path,
    sidecar: VerificationSidecar,
) -> Optional[Path]:
    """Atomically write the sidecar JSON. Returns the path on success.

    Failure is logged via ``logger.exception`` and ``None`` is returned;
    we never propagate write errors back to the verification coordinator
    because a sidecar-write failure must not crash the worker.
    """
    path = sidecar_path_for_replay(replay_dir, sidecar.replay_id)
    try:
        ok = save_json(str(path), sidecar.to_dict())
    except Exception:  # Intentional broad catch: sidecar write must not crash worker
        logger.exception("PROJ-354B sidecar write failed: %s", path)
        return None
    if not ok:
        return None
    return path


def read_verification_sidecar(
    replay_dir: Path,
    replay_id: str,
) -> Optional[VerificationSidecar]:
    """Read a sidecar; return ``None`` for missing, corrupt, or
    schema-mismatched files.

    Absence is normal pre-verification state — the caller should treat
    ``None`` as "verification has not yet completed", not as an error.
    """
    path = sidecar_path_for_replay(replay_dir, replay_id)
    if not path.exists():
        return None
    try:
        data = load_json(str(path), default=None)
    except Exception:  # Intentional broad catch: corrupt sidecars must be skipped, not raised
        logger.debug("PROJ-354B sidecar load failed (corrupt JSON): %s", path)
        return None
    if not isinstance(data, dict):
        return None
    try:
        return VerificationSidecar.from_dict(data)
    except (KeyError, TypeError, ValueError):
        # Schema mismatch — newer or older sidecar version. Skip
        # silently; the coordinator can rewrite on next verification.
        logger.debug("PROJ-354B sidecar schema mismatch: %s", path)
        return None


__all__ = [
    "REPLAY_VERIFICATION_SCHEMA_VERSION",
    "SIDECAR_FILE_PREFIX",
    "SIDECAR_FILE_SUFFIX",
    "VerificationSidecar",
    "VerificationSource",
    "VerificationStatus",
    "read_verification_sidecar",
    "sidecar_path_for_replay",
    "write_verification_sidecar",
]
