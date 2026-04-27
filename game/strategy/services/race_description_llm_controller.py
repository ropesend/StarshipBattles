"""Race description LLM controller (PROJ-299).

Pygame-free state machine that owns the LLM call lifecycle for the
Race Setup Description tab. Two parallel sub-machines (bio and socio).
The UI polls `bio_status` / `socio_status` / `bio_elapsed_seconds` etc.
each frame from the screen's `update()` and re-renders on change via
the injected `on_change` callback.

The controller wraps PROJ-296 `LLMBackgroundCall` for the actual
worker-thread execution. We use `timeout_seconds=90` (overrides
`LLMConfig.DEFAULT_TIMEOUT_SECONDS=60`) so the network timeout fires
shortly after the second "still working" UI dialog at t=90s — giving
the user a definitive end to their wait rather than an indefinite hang.

See `Projects/active_projects/PROJ-299/design.md` § "RaceDescriptionLLMController state machine"
for the full state diagram and contract.
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Callable, Optional

from game.core.exceptions import LLMConfigError, LLMException
from game.services.llm.background import (
    CallStatus,
    LLMBackgroundCall,
)
from game.services.llm.provider import LLMProvider
from game.strategy.data.race_caption_loader import RaceCaptionLoader
from game.strategy.data.race_config import RaceConfig
from game.strategy.services.race_description_prompt_builder import (
    build_bio_prompt,
    build_socio_prompt,
)

logger = logging.getLogger(__name__)


# Override of LLMConfig.DEFAULT_TIMEOUT_SECONDS for this consumer. The
# 30s + 60s = 90s "still working" dialog UX requires the underlying call
# to NOT time out before the second dialog appears.
_LLM_TIMEOUT_SECONDS: float = 90.0


class FieldStatus(str, Enum):
    """Lifecycle status of a single description field (bio or socio)."""
    IDLE = "idle"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


# Map LLMBackgroundCall.CallStatus → FieldStatus.
_CALL_STATUS_MAP = {
    CallStatus.PENDING: FieldStatus.RUNNING,
    CallStatus.RUNNING: FieldStatus.RUNNING,
    CallStatus.DONE: FieldStatus.DONE,
    CallStatus.ERROR: FieldStatus.ERROR,
    CallStatus.CANCELLED: FieldStatus.CANCELLED,
}


class RaceDescriptionLLMController:
    """Owns the LLM-call lifecycle for bio + socio description generation.

    Pygame-free. Tests inject a stub `LLMProvider` and a mock
    `RaceCaptionLoader`. Production wiring lives in `RaceSetupScreen`.

    Args:
        race_config: The race being edited. Generated text is written
            directly to `race_config.bio_description` /
            `race_config.socio_description` on completion.
        provider: An `LLMProvider` (typically from
            `get_default_llm_provider()`).
        caption_loader: A `RaceCaptionLoader` for resolving visual
            asset captions when assembling the prompt.
        on_change: Callback invoked whenever the controller's state
            transitions (IDLE→RUNNING, RUNNING→DONE, etc.) so the UI
            can re-render itself.
    """

    def __init__(
        self,
        race_config: RaceConfig,
        provider: LLMProvider,
        caption_loader: RaceCaptionLoader,
        on_change: Callable[[], None],
    ) -> None:
        self._race = race_config
        self._provider = provider
        self._loader = caption_loader
        self._on_change = on_change

        # Per-field state.
        self._bio_status: FieldStatus = FieldStatus.IDLE
        self._socio_status: FieldStatus = FieldStatus.IDLE
        self._bio_call: Optional[LLMBackgroundCall] = None
        self._socio_call: Optional[LLMBackgroundCall] = None
        self._bio_error: Optional[LLMException] = None
        self._socio_error: Optional[LLMException] = None

    # -- Public state accessors ---------------------------------------------

    @property
    def bio_status(self) -> FieldStatus:
        return self._bio_status

    @property
    def socio_status(self) -> FieldStatus:
        return self._socio_status

    @property
    def bio_error(self) -> Optional[LLMException]:
        return self._bio_error

    @property
    def socio_error(self) -> Optional[LLMException]:
        return self._socio_error

    @property
    def bio_elapsed_seconds(self) -> float:
        return self._bio_call.elapsed_seconds if self._bio_call is not None else 0.0

    @property
    def socio_elapsed_seconds(self) -> float:
        return self._socio_call.elapsed_seconds if self._socio_call is not None else 0.0

    # -- Public actions ------------------------------------------------------

    def generate_bio(self) -> None:
        """Start a bio-description generation. Idempotent if already RUNNING."""
        if self._bio_status == FieldStatus.RUNNING:
            return
        self._start_bio()

    def generate_socio(self) -> None:
        """Start a socio-description generation. Idempotent if already RUNNING."""
        if self._socio_status == FieldStatus.RUNNING:
            return
        self._start_socio()

    def re_roll_bio(self) -> None:
        """Cancel any in-flight bio call and start a fresh one."""
        self.cancel_bio()
        self._start_bio()

    def re_roll_socio(self) -> None:
        """Cancel any in-flight socio call and start a fresh one."""
        self.cancel_socio()
        self._start_socio()

    def cancel_bio(self) -> None:
        """Logical cancel of the bio call. Idempotent."""
        if self._bio_call is not None:
            self._bio_call.cancel()
        if self._bio_status in (FieldStatus.RUNNING,):
            self._bio_status = FieldStatus.CANCELLED
            self._fire_on_change()

    def cancel_socio(self) -> None:
        """Logical cancel of the socio call. Idempotent."""
        if self._socio_call is not None:
            self._socio_call.cancel()
        if self._socio_status in (FieldStatus.RUNNING,):
            self._socio_status = FieldStatus.CANCELLED
            self._fire_on_change()

    def cancel_all(self) -> None:
        """Cancel both fields. Called from `RaceSetupScreen.kill()`."""
        self.cancel_bio()
        self.cancel_socio()

    # -- Per-frame polling ---------------------------------------------------

    def update(self) -> None:
        """Poll in-flight calls; transition state on completion; fire on_change.

        Called every frame from `RaceSetupScreen.update()`.
        """
        self._poll_field("bio")
        self._poll_field("socio")

    # -- Private -------------------------------------------------------------

    def _start_bio(self) -> None:
        captions = self._gather_captions()
        messages = build_bio_prompt(self._race, captions)
        self._bio_error = None
        self._bio_call = LLMBackgroundCall(
            self._provider, messages, timeout_seconds=_LLM_TIMEOUT_SECONDS,
        )
        try:
            self._bio_call.start()
        except LLMConfigError as e:
            # Concurrent-call limit reached (or other config issue at start).
            self._bio_status = FieldStatus.ERROR
            self._bio_error = e
            self._fire_on_change()
            return
        self._bio_status = FieldStatus.RUNNING
        self._fire_on_change()

    def _start_socio(self) -> None:
        captions = self._gather_captions()
        messages = build_socio_prompt(self._race, captions)
        self._socio_error = None
        self._socio_call = LLMBackgroundCall(
            self._provider, messages, timeout_seconds=_LLM_TIMEOUT_SECONDS,
        )
        try:
            self._socio_call.start()
        except LLMConfigError as e:
            self._socio_status = FieldStatus.ERROR
            self._socio_error = e
            self._fire_on_change()
            return
        self._socio_status = FieldStatus.RUNNING
        self._fire_on_change()

    def _gather_captions(self) -> dict:
        """Resolve visual captions; tolerate missing sidecars."""
        return {
            "flag": self._loader.load_flag(self._race.flag_id) if self._race.flag_id else None,
            "portrait": self._loader.load_portrait(self._race.portrait_id) if self._race.portrait_id else None,
            "theme": self._loader.load_theme(self._race.theme_id) if self._race.theme_id else None,
        }

    def _poll_field(self, field: str) -> None:
        """Poll a field's underlying call; transition state if it changed."""
        if field == "bio":
            call = self._bio_call
            current = self._bio_status
            apply = self._apply_bio_transition
        else:
            call = self._socio_call
            current = self._socio_status
            apply = self._apply_socio_transition

        if call is None or current not in (FieldStatus.RUNNING,):
            return

        new_status = _CALL_STATUS_MAP.get(call.status, FieldStatus.RUNNING)
        if new_status == current:
            return
        apply(call, new_status)

    def _apply_bio_transition(
        self, call: LLMBackgroundCall, new_status: FieldStatus
    ) -> None:
        if new_status == FieldStatus.DONE and call.result is not None:
            self._race.bio_description = call.result.text
        elif new_status == FieldStatus.ERROR:
            self._bio_error = call.error
        # CANCELLED also lands here when the call was cancelled by us;
        # bio_description stays as-is (preserves prior text).
        self._bio_status = new_status
        self._fire_on_change()

    def _apply_socio_transition(
        self, call: LLMBackgroundCall, new_status: FieldStatus
    ) -> None:
        if new_status == FieldStatus.DONE and call.result is not None:
            self._race.socio_description = call.result.text
        elif new_status == FieldStatus.ERROR:
            self._socio_error = call.error
        self._socio_status = new_status
        self._fire_on_change()

    def _fire_on_change(self) -> None:
        try:
            self._on_change()
        except Exception as e:  # Intentional broad catch: UI callbacks must not crash the controller
            logger.error("on_change callback raised: %s: %s", type(e).__name__, e)


__all__ = ["FieldStatus", "RaceDescriptionLLMController"]
