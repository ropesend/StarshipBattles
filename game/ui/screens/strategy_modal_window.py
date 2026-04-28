"""Strategy Modal Window base class (PROJ-313).

Replaces the manual 6-step modal-tracking contract documented at
``docs/02_PATTERNS.md`` Pattern #30 (Registrar Close-Callback) with a
structural one. Subclasses auto-register with a ``StrategyWindowManager``
on construction and auto-deregister in ``kill()``. The previous
``has_modal_open() -> is not None`` and ``_is_blocking_ui_element_at() ->
.alive()`` asymmetry — which produced BUG-121 — is collapsed into a
single live-list walk owned by ``StrategyWindowManager.iter_live_modals``.

New strategy-modal windows should subclass ``StrategyModalWindow`` and
accept ``window_manager`` as a keyword argument in ``__init__``,
forwarding it to ``super().__init__(window_manager=window_manager, ...)``.
No further wiring is required — registration and cleanup happen in the
base class.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pygame_gui.elements import UIWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class StrategyModalWindow(UIWindow):
    """Base class for any window that should block strategy-screen input.

    Subclasses get auto-registration on construction and auto-deregistration
    on ``kill()`` — no manual slot wiring required.

    Forgetting to register is impossible because registration happens in
    the base class constructor before any subclass code runs. Forgetting
    to deregister is impossible because ``kill()`` is overridden in the
    base class and pygame_gui guarantees every kill path (programmatic
    ``kill()``, title-bar ``[X]`` button, parent kill) routes through
    this method.

    The class-level ``_registered_subclasses`` set is populated by
    ``__init_subclass__`` at class definition time. The
    ``test_strategy_modal_window`` test suite asserts that every
    registered subclass auto-registers on construction and auto-deregisters
    on kill, replacing the source-string-matching contract test that was
    removed in Phase 8.
    """

    # Populated by __init_subclass__ at class definition time. Using a
    # class-level set rather than `__subclasses__()` because the latter is
    # order-dependent on test imports and only finds loaded classes.
    _registered_subclasses: set[type] = set()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        StrategyModalWindow._registered_subclasses.add(cls)

    def __init__(
        self,
        *args: Any,
        window_manager: "StrategyWindowManager | None",
        **kwargs: Any,
    ) -> None:
        """Initialize and register with the window manager.

        Args:
            *args: Forwarded to ``UIWindow.__init__``. Typically
                ``relative_rect, manager``.
            window_manager: The :class:`StrategyWindowManager` that owns
                the modal-tracking list. The instance registers itself
                here on construction and deregisters on ``kill()``.
                Pass ``None`` only when the window is being opened
                outside the strategy screen (e.g. from a sub-screen
                like ``BuildQueueScreen``); in that case the window
                doesn't participate in strategy-screen modal tracking.
            **kwargs: Forwarded to ``UIWindow.__init__``. Typically
                ``window_display_title``, ``resizable``, etc.
        """
        super().__init__(*args, **kwargs)
        self._window_manager = window_manager
        if window_manager is not None:
            window_manager.register_modal(self)

    def kill(self) -> None:
        """Deregister from the window manager, then kill the underlying window.

        Deregistration runs BEFORE ``super().kill()`` so the modal is off
        the live list at the moment ``alive()`` flips to False — closing
        the asymmetry that produced BUG-121. The ``try/finally`` ensures
        ``super().kill()`` still runs even if deregistration somehow
        raises (it cannot today; defensive).

        Idempotent: ``unregister_modal`` swallows ``ValueError`` for
        already-removed entries, so calling ``kill()`` twice is safe.
        Windows constructed with ``window_manager=None`` skip the
        deregistration step entirely.
        """
        try:
            if self._window_manager is not None:
                self._window_manager.unregister_modal(self)
        finally:
            super().kill()
