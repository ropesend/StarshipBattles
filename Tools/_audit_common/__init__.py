"""Shared helpers for audit skills under .opencode/skills/ocode-*-audit/.

Production code under game/ has structured layers; audit reports use these
helpers to weight findings by layer importance and to track trends across
runs. See AgentCoordination/Scratchpad/plans/opencode_review_skills_overhaul.md
for the design rationale.
"""

from . import layer_weight, run_tracker

__all__ = ["layer_weight", "run_tracker"]
