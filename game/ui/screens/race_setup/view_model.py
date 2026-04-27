"""PROJ-309 Sub-phase 3.1 — RaceSetupViewModel.

Pure derived view state for the race setup wizard. No pygame imports;
no widgets. Holds:

- Tab index constants and names (lifted from the original screen class).
- The currently-active tab (`current_step`).
- The PROJ-299 LLM "still working" dialog threshold counters
  (`bio_dialog_fired_at`, `socio_dialog_fired_at`) and the error-popup
  seen flags (`bio_error_seen`, `socio_error_seen`).
- The `is_editing` flag (toggles the Save button text and the FEAT-05
  overwrite-vs-save-as-new flow).

Per the decomposition design (§3 view_model.py), this module owns all
"small" view state that doesn't fit on the controller (mutation-only)
or the renderer (widget-only).
"""
from __future__ import annotations

from typing import Final, List


# Tab indices — PROJ-66 Phase 6 numbering. Public so the input_handler,
# screen, and existing tests can address tabs by name. Note: the legacy
# `RaceSetupScreen` class re-exports these as class attributes for
# backwards compatibility with the existing test suite.
TAB_SUMMARY: Final[int] = 0
TAB_IDENTITY: Final[int] = 1
TAB_VISUALS: Final[int] = 2
TAB_SHIPS: Final[int] = 3
TAB_ENVIRONMENT: Final[int] = 4
TAB_APTITUDES: Final[int] = 5
TAB_DESCRIPTIONS: Final[int] = 6

TAB_NAMES: Final[List[str]] = [
    "Summary",
    "Identity",
    "Visuals",
    "Ships",
    "Environment",
    "Aptitudes",
    "Descriptions",
]


class RaceSetupViewModel:
    """Selection + derived view state for the race setup wizard."""

    def __init__(self, *, is_editing: bool = False) -> None:
        self.current_step: int = TAB_SUMMARY
        self.is_editing: bool = is_editing

        # PROJ-299 30s/90s "still working" dialog state. Per-field
        # threshold tracking — 0 when dialog hasn't fired for the
        # current call, otherwise records the last threshold (30 or 90)
        # at which it fired.
        self.bio_dialog_fired_at: int = 0
        self.socio_dialog_fired_at: int = 0

        # PROJ-299 error-popup state — one popup per ERROR transition;
        # track the last-seen error per field so we don't spam.
        self.bio_error_seen: bool = False
        self.socio_error_seen: bool = False

    @property
    def tab_count(self) -> int:
        return len(TAB_NAMES)

    def clamp_step(self, step_num: int) -> int:
        """Return `step_num` clamped to a valid tab index."""
        return max(0, min(step_num, len(TAB_NAMES) - 1))

    def show_save_button_on(self, step: int) -> bool:
        """The Save button is only visible on the Summary tab."""
        return step == TAB_SUMMARY

    def show_randomize_button_on(self, step: int) -> bool:
        """The bottom-bar Generate Random button shows on every
        randomizable tab except Summary (where the master "Randomize
        All" button on the panel supersedes it) and Descriptions
        (LLM-generated)."""
        return step in (
            TAB_IDENTITY,
            TAB_VISUALS,
            TAB_SHIPS,
            TAB_ENVIRONMENT,
            TAB_APTITUDES,
        )
