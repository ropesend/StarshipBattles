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
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Optional

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


@dataclass
class _FieldState:
    """Per-field state container (PROJ-375 Task 2.5).

    Replaces the mirrored `_bio_*` / `_socio_*` attribute pairs.

    Attributes:
        race_attr: The attribute name on `RaceConfig` to write the
            generated text to (`bio_description` or `socio_description`).
        prompt_builder: Callable that produces the `messages` list for
            the LLM call given (race_config, captions).
        log_label: Short label for log lines (`"bio"` / `"socio"`).
        status: Current `FieldStatus`.
        call: Live `LLMBackgroundCall`, or None.
        error: Last `LLMException` if status is ERROR.
    """
    race_attr: str
    prompt_builder: Callable
    log_label: str
    status: FieldStatus = FieldStatus.IDLE
    call: Optional[LLMBackgroundCall] = None
    error: Optional[LLMException] = field(default=None)


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

        # PROJ-375 Task 2.5: per-field state in a dict, no mirrored
        # attribute pairs. The 6 public `@property` accessors below read
        # from this dict — external readers (race_description_panel.py,
        # llm_dialog_service.py) keep their existing API.
        self._fields: Dict[str, _FieldState] = {
            "bio": _FieldState(
                race_attr="bio_description",
                prompt_builder=build_bio_prompt,
                log_label="bio",
            ),
            "socio": _FieldState(
                race_attr="socio_description",
                prompt_builder=build_socio_prompt,
                log_label="socio",
            ),
        }

    # -- Public state accessors ---------------------------------------------

    @property
    def bio_status(self) -> FieldStatus:
        return self._fields["bio"].status

    @property
    def socio_status(self) -> FieldStatus:
        return self._fields["socio"].status

    @property
    def bio_error(self) -> Optional[LLMException]:
        return self._fields["bio"].error

    @property
    def socio_error(self) -> Optional[LLMException]:
        return self._fields["socio"].error

    @property
    def bio_elapsed_seconds(self) -> float:
        call = self._fields["bio"].call
        return call.elapsed_seconds if call is not None else 0.0

    @property
    def socio_elapsed_seconds(self) -> float:
        call = self._fields["socio"].call
        return call.elapsed_seconds if call is not None else 0.0

    # -- Public actions ------------------------------------------------------

    def generate_bio(self) -> None:
        """Start a bio-description generation. Idempotent if already RUNNING."""
        if self._fields["bio"].status == FieldStatus.RUNNING:
            return
        self._start_field("bio")

    def generate_socio(self) -> None:
        """Start a socio-description generation. Idempotent if already RUNNING."""
        if self._fields["socio"].status == FieldStatus.RUNNING:
            return
        self._start_field("socio")

    def re_roll_bio(self) -> None:
        """Cancel any in-flight bio call and start a fresh one."""
        self.cancel_bio()
        self._start_field("bio")

    def re_roll_socio(self) -> None:
        """Cancel any in-flight socio call and start a fresh one."""
        self.cancel_socio()
        self._start_field("socio")

    def cancel_bio(self) -> None:
        """Logical cancel of the bio call. Idempotent."""
        self._cancel_field("bio")

    def cancel_socio(self) -> None:
        """Logical cancel of the socio call. Idempotent."""
        self._cancel_field("socio")

    def cancel_all(self) -> None:
        """Cancel both fields. Called from `RaceSetupScreen.kill()`."""
        self.cancel_bio()
        self.cancel_socio()

    def set_race_config(self, race_config: RaceConfig) -> None:
        """Re-point the controller at a new RaceConfig instance.

        PROJ-299 fix: the screen reassigns `self.race_config` on Load Race
        and Randomize All. `_populate_ui_from_config()` updates each
        panel's reference; this method does the same for the controller.
        Without this, generated text lands in the orphaned old instance
        while the panel reads from the new one (silent data loss).
        """
        self._race = race_config

    # -- Per-frame polling ---------------------------------------------------

    def update(self) -> None:
        """Poll in-flight calls; transition state on completion; fire on_change.

        Called every frame from `RaceSetupScreen.update()`.
        """
        self._poll_field("bio")
        self._poll_field("socio")

    # -- Private -------------------------------------------------------------

    def _start_field(self, field_name: str) -> None:
        """Start an LLM call for the given field (PROJ-375 Task 2.5)."""
        state = self._fields[field_name]
        captions = self._gather_captions()
        cap_summary = {k: ("present" if v else "missing") for k, v in captions.items()}
        logger.info("Race description %s START: captions=%s", state.log_label, cap_summary)
        messages = state.prompt_builder(self._race, captions)
        state.error = None
        state.call = LLMBackgroundCall(
            self._provider, messages, timeout_seconds=_LLM_TIMEOUT_SECONDS,
        )
        try:
            state.call.start()
        except LLMConfigError as e:
            # Concurrent-call limit reached (or other config issue at start).
            logger.error("Race description %s start failed: %s", state.log_label, e)
            state.status = FieldStatus.ERROR
            state.error = e
            self._fire_on_change()
            return
        state.status = FieldStatus.RUNNING
        self._fire_on_change()

    def _cancel_field(self, field_name: str) -> None:
        """Cancel a field's in-flight call (PROJ-375 Task 2.5)."""
        state = self._fields[field_name]
        if state.call is not None:
            state.call.cancel()
        if state.status in (FieldStatus.RUNNING,):
            state.status = FieldStatus.CANCELLED
            self._fire_on_change()

    def _gather_captions(self) -> dict:
        """Resolve visual captions; tolerate missing sidecars."""
        return {
            "flag": self._loader.load_flag(self._race.flag_id) if self._race.flag_id else None,
            "portrait": self._loader.load_portrait(self._race.portrait_id) if self._race.portrait_id else None,
            "theme": self._loader.load_theme(self._race.theme_id) if self._race.theme_id else None,
        }

    def _poll_field(self, field_name: str) -> None:
        """Poll a field's underlying call; transition state if it changed."""
        state = self._fields[field_name]
        if state.call is None or state.status not in (FieldStatus.RUNNING,):
            return

        new_status = _CALL_STATUS_MAP.get(state.call.status, FieldStatus.RUNNING)
        if new_status == state.status:
            return
        self._apply_field_transition(field_name, state.call, new_status)

    def _apply_field_transition(
        self,
        field_name: str,
        call: LLMBackgroundCall,
        new_status: FieldStatus,
    ) -> None:
        """Apply a status transition for a field (PROJ-375 Task 2.5)."""
        state = self._fields[field_name]
        if new_status == FieldStatus.DONE and call.result is not None:
            text = call.result.text or ""
            logger.info(
                "Race description %s DONE: text_len=%d latency=%.2fs tokens=%d",
                state.log_label, len(text), call.result.latency_seconds,
                call.result.usage.total_tokens,
            )
            setattr(self._race, state.race_attr, text)
        elif new_status == FieldStatus.ERROR:
            logger.error(
                "Race description %s ERROR: %s: %s",
                state.log_label,
                type(call.error).__name__ if call.error else "Unknown",
                call.error,
            )
            state.error = call.error
        # CANCELLED also lands here; the race_attr stays as-is (preserves prior text).
        state.status = new_status
        self._fire_on_change()

    def _fire_on_change(self) -> None:
        try:
            self._on_change()
        except Exception as e:  # Intentional broad catch: UI callbacks must not crash the controller
            logger.error("on_change callback raised: %s: %s", type(e).__name__, e)


__all__ = ["FieldStatus", "RaceDescriptionLLMController"]
