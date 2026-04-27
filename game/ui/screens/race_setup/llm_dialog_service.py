"""PROJ-309 Sub-phase 3.1 — LLM "still working" dialog service.

Encapsulates the PROJ-299 threshold-management logic for the description
LLM controller's 30s/90s "still working" modal and the per-error-type
popup. State (threshold counters + seen flags) lives on the
`RaceSetupViewModel`; modal widget construction lives on the
`RaceSetupRenderer`. This service is the "policy" layer that decides
*when* a modal should appear and *what* error message to show.

Design refs:
- `Projects/active_projects/PROJ-309/findings/race_setup_screen_decomposition.md` §6
- `game/strategy/services/race_description_llm_controller.py` (PROJ-299)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.ui.screens.race_setup.renderer import RaceSetupRenderer
    from game.ui.screens.race_setup.view_model import RaceSetupViewModel
    from game.strategy.services.race_description_llm_controller import (
        RaceDescriptionLLMController,
    )


class LLMDialogService:
    """Orchestrates the 30s/90s still-working dialog and the per-error-type
    popup.

    Threshold state lives on the supplied `view_model`; modal widget
    construction is delegated to the supplied `renderer`. Holding
    references to both keeps the policy logic (this class) free of any
    pygame_gui imports.
    """

    def __init__(
        self,
        *,
        view_model: "RaceSetupViewModel",
        renderer: "RaceSetupRenderer",
    ) -> None:
        self._vm = view_model
        self._renderer = renderer

    # ------------------------------------------------------------------
    # 30s / 90s "still working" dialog
    # ------------------------------------------------------------------

    def check_dialog_thresholds(
        self,
        controller: "RaceDescriptionLLMController",
    ) -> None:
        """Per-frame check: should the dialog appear for either field?

        Logic per design.md (PROJ-299):
        - First dialog at elapsed >= 30s; if "Keep Waiting" clicked, re-arm
          for 90s. Tracked per-field via `bio_dialog_fired_at` /
          `socio_dialog_fired_at` (0 / 30 / 90).
        - Only ONE dialog visible at a time. If both fields qualify
          simultaneously, bio wins (arbitrary tie-break).
        - Dialog state resets when the field leaves RUNNING.
        """
        from game.strategy.services.race_description_llm_controller import (
            FieldStatus,
        )

        # Reset thresholds when fields leave RUNNING.
        if controller.bio_status != FieldStatus.RUNNING:
            self._vm.bio_dialog_fired_at = 0
        if controller.socio_status != FieldStatus.RUNNING:
            self._vm.socio_dialog_fired_at = 0

        # Don't fire while a dialog is already up.
        if self._renderer.llm_dialog_window is not None:
            return

        # Bio gets first crack.
        for field, status, elapsed, fired_at_attr in (
            ("bio", controller.bio_status, controller.bio_elapsed_seconds,
             "bio_dialog_fired_at"),
            ("socio", controller.socio_status, controller.socio_elapsed_seconds,
             "socio_dialog_fired_at"),
        ):
            if status != FieldStatus.RUNNING:
                continue
            fired_at = getattr(self._vm, fired_at_attr)
            if fired_at == 0 and elapsed >= 30:
                self._renderer.show_llm_dialog(field, threshold=30)
                setattr(self._vm, fired_at_attr, 30)
                return
            if fired_at == 30 and elapsed >= 90:
                self._renderer.show_llm_dialog(field, threshold=90)
                setattr(self._vm, fired_at_attr, 90)
                return

    # ------------------------------------------------------------------
    # Per-error-type popups
    # ------------------------------------------------------------------

    def check_error_popups(
        self,
        controller: "RaceDescriptionLLMController",
    ) -> None:
        """If a field transitioned to ERROR since last frame, surface a popup."""
        from game.strategy.services.race_description_llm_controller import (
            FieldStatus,
        )

        # Reset seen-flag when state leaves ERROR.
        if controller.bio_status != FieldStatus.ERROR:
            self._vm.bio_error_seen = False
        if controller.socio_status != FieldStatus.ERROR:
            self._vm.socio_error_seen = False

        # Show popups for newly-seen errors. Bio first.
        if (
            controller.bio_status == FieldStatus.ERROR
            and not self._vm.bio_error_seen
            and self._renderer.llm_error_popup is None
        ):
            self._renderer.show_llm_error_popup(
                self.error_message(controller.bio_error)
            )
            self._vm.bio_error_seen = True
            return
        if (
            controller.socio_status == FieldStatus.ERROR
            and not self._vm.socio_error_seen
            and self._renderer.llm_error_popup is None
        ):
            self._renderer.show_llm_error_popup(
                self.error_message(controller.socio_error)
            )
            self._vm.socio_error_seen = True

    @staticmethod
    def error_message(error) -> str:
        """Map an LLMException type → user-facing message."""
        # Late imports to avoid pulling LLM types when no controller exists.
        from game.core.exceptions import (
            LLMConfigError, LLMNetworkError, LLMRateLimited,
            LLMResponseError, LLMTimeoutError,
        )
        if isinstance(error, LLMRateLimited):
            return "Rate limited by the LLM service. Please wait a moment and try again."
        if isinstance(error, LLMTimeoutError):
            return "LLM request timed out after 90 seconds."
        if isinstance(error, LLMNetworkError):
            return "Network error: could not reach the LLM service."
        if isinstance(error, LLMConfigError):
            return "LLM is not configured (DEEPSEEK_API_KEY may be unset)."
        if isinstance(error, LLMResponseError):
            return "The LLM returned an unexpected response."
        return f"LLM error: {type(error).__name__}"
