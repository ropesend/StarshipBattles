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

import pygame_gui
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

    def request_close(self) -> None:
        """User-requested close (Esc / Cancel / etc.).

        PROJ-411 Task 2.5: extension point for window-reuse subclasses.
        Default behaviour is ``self.kill()`` — equivalent to the legacy
        contract. Reusable subclasses (PlanetListWindow, StarListWindow,
        EmpirePanelWindow, EventLogWindow) override this to call
        ``self.hide()`` so the instance survives for fast re-open.

        Called by the strategy event router's Esc handler. Distinct from
        ``kill()`` so true teardown (scene exit, parent kill, game
        shutdown) still routes through ``kill()`` and clears the slot.
        """
        self.kill()

    def hide(self, hide_contents: bool = True) -> None:
        """Hide the modal so background UI receives input again.

        PROJ-411 Task 2.8: consolidated reuse-hide logic on the base
        class. Subclasses no longer override hide(); they implement
        their own ``open_for_X`` to rebind context and call ``show()``.

        Three things must happen for hidden-modal-reuse to work:
        1. ``is_blocking = False`` so pygame_gui's
           ``check_clicked_inside_or_blocking`` doesn't claim clicks.
        2. Unregister from ``StrategyWindowManager._modals`` so
           ``has_modal_open()`` returns False.
        3. Remove from pygame_gui's ``window_stack`` so the hidden
           window isn't z-top — otherwise hit-testing / focus state
           routes events to the dead-but-alive window.

        PROJ-411 Task 2.6's visibility-aware
        ``check_clicked_inside_or_blocking`` covered step 1's side of
        the click-block, but the window_stack was still inflated by the
        hidden window, causing the symptom the user reported (End Turn
        and zoom unresponsive after Esc-close).
        """
        self.is_blocking = False
        wm = getattr(self, "_window_manager", None)
        if wm is not None:
            try:
                wm.unregister_modal(self)
            except ValueError:
                pass  # Intentional broad ignore: idempotent unregister.
        # Remove from pygame_gui window_stack — mirrors what kill() does.
        stack = getattr(self, "window_stack", None)
        if stack is not None:
            try:
                stack.remove_window(self)
            except (ValueError, KeyError):
                pass  # Intentional broad ignore: idempotent stack removal.
        super().hide(hide_contents=hide_contents)

    def show(self) -> None:
        """Show the modal after a previous hide(), restoring full input
        ownership and z-top placement.

        PROJ-411 Task 2.8: consolidated reuse-show logic on the base
        class. Mirrors ``hide()`` step-for-step in reverse.

        Obs 3 (PROJ-411 follow-up): after the recursive un-hide cascade
        from pygame_gui's ``UIWindow.show()`` -> ``UIContainer.show(True)``
        propagates through every descendant, subclasses that own a
        ``VirtualTable`` row pool need a chance to re-assert per-row
        visibility (rows beyond ``row_count`` get un-hidden by the
        cascade). The ``_post_show_hook`` extension point runs after
        z-stack restoration so subclass overrides can call
        ``virtual_table.force_update()`` + ``update_visible_rows()``
        without racing against pygame_gui's container show pass.
        """
        super().show()
        self.is_blocking = True
        wm = getattr(self, "_window_manager", None)
        if wm is not None:
            wm.register_modal(self)
        stack = getattr(self, "window_stack", None)
        if stack is not None:
            # add_new_window appends without dedup; remove first if
            # already present to keep the stack invariant.
            try:
                stack.remove_window(self)
            except (ValueError, KeyError):
                pass  # Intentional broad ignore.
            stack.add_new_window(self)
        self._post_show_hook()

    def _post_show_hook(self) -> None:
        """Extension point invoked at the end of ``show()``.

        Default is a no-op. Subclasses owning a ``VirtualTable`` override
        to re-assert row-pool visibility after pygame_gui's recursive
        ``UIContainer.show(True)`` cascade re-exposes individually-hidden
        descendants (Obs 3 — stale row-pool widgets leaking onto the
        screen on re-open).

        See ``BuildQueueScreen.show()`` (build_queue_screen.py) for the
        canonical pattern: ``virtual_table.force_update()`` followed by
        ``virtual_table.update_visible_rows()``.
        """
        return None

    def check_clicked_inside_or_blocking(self, event) -> bool:
        """Skip the pygame_gui focus/block check when hidden.

        PROJ-411 Task 2.6: when a reusable PROJ-411 window is hidden,
        pygame_gui's default ``check_clicked_inside_or_blocking`` still
        runs because the window remains in the sprite group. The default
        implementation calls ``hover_point()`` which collides on rect
        only (no visibility check), so a 90%-screen hidden window
        consumes every left-click in its rect — blocking the strategy
        view's End Turn button, hex clicks, etc.

        By short-circuiting to ``False`` when hidden, hidden modal
        windows become transparent to input. Killed modals are removed
        from the sprite group entirely so this method is never reached
        for them; the override is therefore safe for non-reusable
        subclasses too.
        """
        if not self.visible:
            return False
        return super().check_clicked_inside_or_blocking(event)


class DismissableModalDialog(StrategyModalWindow):
    """Strategy modal that closes itself when its ``_dismiss_button`` is pressed.

    Cluster 7 (PROJ-465): owns the character-for-character identical
    ``process_event`` previously duplicated in :class:`DefeatDialog` and
    :class:`TurnFailedDialog`. Subclasses build their own body and a
    ``self._dismiss_button`` (or set it to ``None`` under bypass-init);
    this base handles the dismiss click and delegates everything else to
    :class:`StrategyModalWindow`.
    """

    def process_event(self, event: "Any") -> bool:
        """Handle the dismiss-button click.

        Returns ``True`` if this dialog consumed the event so pygame_gui
        does not deliver it elsewhere; otherwise delegates to the base
        class.
        """
        if (
            event.type == pygame_gui.UI_BUTTON_PRESSED
            and getattr(self, "_dismiss_button", None) is not None
            and event.ui_element is self._dismiss_button
        ):
            self.kill()
            return True
        return super().process_event(event)
