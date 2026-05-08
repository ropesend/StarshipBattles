"""Layer-importance multipliers for prioritizing audit findings.

Audit skills produce findings with severity (CRITICAL/MAJOR/MINOR/ADVISORY/INFO).
Severity alone doesn't capture *where* the finding lives — a CRITICAL in
game/core/ is more impactful than a CRITICAL in game/ui/screens/. This module
returns a per-layer multiplier so the prioritized remediation plan can sort by
``severity_weight * layer_weight * loc_affected``.

Minor findings in low-weight layers still appear in the per-shard detail
tables and category scorecards — the weighting only affects the *ordering*
of the top-N action plan, not what gets reported.
"""

from __future__ import annotations

from typing import Final


SEVERITY_WEIGHT: Final[dict[str, float]] = {
    "CRITICAL": 10.0,
    "MAJOR": 5.0,
    "MINOR": 1.0,
    "ADVISORY": 0.5,
    "INFO": 0.25,
}


# Multipliers applied on top of severity. Higher = higher priority.
# Values reflect blast radius: code in core/ touches everything; ui/screens
# is a leaf layer where issues affect one screen.
_LAYER_WEIGHT: Final[dict[str, float]] = {
    "core": 3.0,
    "engine": 2.5,
    "simulation": 2.0,
    "strategy": 2.0,
    "services": 1.8,
    "ai": 1.5,
    "research": 1.5,
    "assets": 1.2,
    "ui/orchestration": 1.5,
    "ui/services": 1.5,
    "ui/interfaces": 1.4,
    "ui/renderer": 1.2,
    "ui/panels": 1.0,
    "ui/screens": 1.0,
    "ui/components": 1.0,
    "ui/widgets": 1.0,
    "ui/effects": 0.9,
    "ui/filters": 0.9,
    "ui/utils": 1.0,
    "ui": 1.0,  # fallback for files directly under game/ui/
    "root": 1.5,  # game/app.py, game/context.py, etc.
}

DEFAULT_WEIGHT: Final[float] = 1.0


def layer_for_path(path: str) -> str:
    """Resolve the layer name for a game/ file path.

    >>> layer_for_path("game/core/registry.py")
    'core'
    >>> layer_for_path("game/ui/screens/main_menu.py")
    'ui/screens'
    >>> layer_for_path("game/app.py")
    'root'
    """
    norm = path.replace("\\", "/").lstrip("./")
    if not norm.startswith("game/"):
        return "root"
    rest = norm[len("game/"):]
    parts = rest.split("/")

    if len(parts) == 1:
        # game/foo.py — top-level file under game/
        return "root"

    top = parts[0]
    if top == "ui" and len(parts) >= 3:
        # game/ui/<sub>/... — return "ui/<sub>"
        return f"ui/{parts[1]}"
    if top == "ui":
        # game/ui/<file>.py — fallback
        return "ui"
    return top


def weight_for_layer(layer: str) -> float:
    """Return the multiplier for a layer name. Unknown layers get DEFAULT_WEIGHT."""
    return _LAYER_WEIGHT.get(layer, DEFAULT_WEIGHT)


def weight_for_path(path: str) -> float:
    """Convenience: resolve layer from path then return its weight."""
    return weight_for_layer(layer_for_path(path))


def severity_weight(severity: str) -> float:
    """Return the numeric weight for a severity string (case-insensitive)."""
    return SEVERITY_WEIGHT.get(severity.upper(), 0.0)


def priority_score(severity: str, path: str, loc_affected: int = 1) -> float:
    """Compute the combined priority score for a finding.

    Used by audit skills to sort the prioritized remediation plan.
    """
    return severity_weight(severity) * weight_for_path(path) * max(loc_affected, 1)
