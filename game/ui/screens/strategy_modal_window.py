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
    ``test_strategy_modal_window`` test suite asserts the base invariants
    and required strategy-only constructor signatures. The legacy
    source-string slot cleanup contract remains as a regression for the
    retained caller-convenience slot pathway.
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

        Bypass-init shell (PROJ-328 Phase A Task A.1):

        When a subclass sets ``Cls.bypass_init = True`` (typically via
        ``tests.fixtures.ui_widget_factory.bypass_init``), this method
        skips the heavy ``UIWindow.__init__`` chain but still leaves a
        usable minimal shell so subclasses' Stage-1 cheap state survives
        and Stage-3 widget construction can be branched on
        ``self._window_init_bypassed``.

        The shell sets:

        * ``self._window_manager`` — populated even under bypass so
          ``kill()`` cleanup is consistent. We intentionally do NOT call
          ``window_manager.register_modal(self)`` because bypassed
          instances are test fixtures, not real live windows.
        * ``self.ui_manager`` — extracted from ``args``/``kwargs`` (the
          first positional arg after the rect, or the ``manager`` keyword)
          so subclasses' renderer/builder code that reads
          ``self.ui_manager`` survives.
        * ``self._window_init_bypassed = True`` — the flag subclasses
          check after ``super().__init__`` to short-circuit their own
          Stage-3 widget construction.

        Note: ``self.rect`` is NOT assigned here. ``pygame_gui``'s
        ``GUISprite`` base class makes ``rect`` a descriptor that mutates
        ``self.blit_data`` on write, and ``blit_data`` is initialized
        only by the ``pygame.sprite.Sprite.__init__`` chain that
        ``bypass_init`` skips. (PROJ-325 PoC finding 1.)
        """
        # PROJ-324 Phase 1 / PROJ-328 Phase A Task A.1: opt-in test
        # escape hatch. When a test sets ``Cls.bypass_init = True``
        # (preferably via the
        # ``tests.fixtures.ui_widget_factory.bypass_init`` context
        # manager), skip the heavy ``UIWindow.__init__`` chain that
        # requires a real pygame display. Production code never sets
        # the flag; ``getattr`` with default ``False`` keeps behavior
        # unchanged when the flag is absent. ``type(self)`` (not the
        # defining class) is required so flags set on concrete
        # subclasses (e.g., ``FleetReportWindow``) are honored when the
        # subclass calls ``super().__init__()``.
        if getattr(type(self), 'bypass_init', False):
            self._window_manager = window_manager
            # Extract the manager so subclass code that reads
            # ``self.ui_manager`` (renderers, list builders, etc.) keeps
            # working under bypass. Subclasses call us as
            # ``super().__init__(rect, manager, ..., window_manager=...)``
            # in production — args[1] is the manager. They may also pass
            # it by keyword as ``manager=...``.
            resolved_manager = kwargs.get('manager')
            if resolved_manager is None and len(args) >= 2:
                resolved_manager = args[1]
            self.ui_manager = resolved_manager
            self._window_init_bypassed = True
            return
        super().__init__(*args, **kwargs)
        # Issue #12 (hover scope-expansion): enable pygame-gui's native
        # modal hover-block. UIWindow.check_hover returns True
        # unconditionally when is_blocking, propagating
        # hover_handled=True to UIManager._handle_hovering. That
        # suppresses hover dispatch on every lower-layer element
        # (top-bar buttons, detail-panel context buttons, tree items,
        # etc.) without per-button retrofit. Click-block continues to
        # come from StrategyEventRouter (commit 28c681595); both
        # defenses coexist.
        self.is_blocking = True
        self._window_manager = window_manager
        self._window_init_bypassed = False
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
            # getattr-with-default tolerates tests that bypass __init__
            # via __new__ + patched-init technique (existing pattern in
            # this codebase).
            wm = getattr(self, "_window_manager", None)
            if wm is not None:
                wm.unregister_modal(self)
        finally:
            super().kill()
