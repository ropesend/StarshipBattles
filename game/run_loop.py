"""Main game loop + per-frame event/draw dispatch.

PROJ-309 sub-phase 3.9: extracted from `game/app.py`. Owns the
frame-pump, the exit-dialog handler, and the per-frame update/draw
plumbing. Tightly coupled to `ScreenRouter` (reads `active_scene`) and
`BootstrapResult` (reads `screen`, `clock`, fonts, `ctx.profiler`,
`input_mapper`).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import pygame

from game.core.constants import GameState
from game.core.input_actions import InputAction
from game.exit_dialog import ExitDialog

if TYPE_CHECKING:
    from game.app_bootstrap import BootstrapResult
    from game.core.state_machine import ScreenStateMachine
    from game.screen_router import ScreenRouter

logger = logging.getLogger(__name__)

FPS = 60
BG_COLOR = (10, 10, 20)


class RunLoop:
    """Per-frame event dispatch + scene update/draw + LLM/pygame shutdown."""

    def __init__(
        self,
        boot: "BootstrapResult",
        router: "ScreenRouter",
        state_machine: "ScreenStateMachine",
    ):
        self._boot = boot
        self._router = router
        self._state_machine = state_machine
        self._exit_dialog = ExitDialog()
        self.running = True

    def request_shutdown(self) -> None:
        """Flag the loop to exit on the next iteration."""
        self.running = False

    @property
    def state(self) -> GameState:
        """Current game state — proxy to state machine for convenience."""
        return self._state_machine.state

    def run(self) -> None:
        """Main game loop.

        On exit: waits up to 5s for any in-flight LLM background calls,
        then quits pygame. Returns control to `main()` so the profiler
        history can be saved.
        """
        clock = self._boot.clock
        while self.running:
            frame_time = clock.tick(0) / 1000.0
            if frame_time > 0.1:
                frame_time = 0.1

            events = pygame.event.get()

            if self._router.show_exit_dialog:
                self._handle_exit_dialog_events(events)
            else:
                self._handle_normal_events(events)

            self._update_and_draw(frame_time, events)
            pygame.display.flip()

        # PROJ-296: wait for any in-flight LLM worker threads to finish
        # before tearing down pygame. Bounded by a 5s timeout so a hung
        # remote endpoint can never freeze the game on shutdown.
        from game.services.llm.background import shutdown_all_calls
        shutdown_all_calls(timeout=5.0)

        # PROJ-366 Phase 2: drain background replay-verification work
        # before pygame teardown. Order is `shutdown_all_calls` first
        # because the current code has no LLM dependency in the verifier
        # path (AIControllerFactory constructs local AI controllers
        # directly per `game/ai/ai_factory.py:21-29,83-110`); preserving
        # the existing LLM shutdown invariant before adding the
        # coordinator drain. If a future verifier path invokes LLM work,
        # revisit this order. The ordering test in
        # `test_run_loop_shutdown_ordering.py` pins the invariant by name
        # so any future flip is loud.
        from game.strategy.services.replay_verification_coordinator import (
            shutdown_all_coordinators,
        )
        shutdown_all_coordinators(timeout=5.0)

        pygame.quit()

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def _handle_exit_dialog_events(self, events: list[Any]) -> None:
        """Handle events when exit dialog is shown."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._router.show_exit_dialog = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self._exit_dialog.handle_click(event.pos):
                    self.running = False
                elif self._exit_dialog.handle_cancel(event.pos):
                    self._router.show_exit_dialog = False

    def _handle_normal_events(self, events: list[Any]) -> None:
        """Handle events during normal gameplay.

        PROJ-88 Phase 5: Removed legacy MOUSEBUTTONDOWN/MOUSEWHEEL dispatch.
        These events now flow through _forward_event_to_scene() to each scene's
        handle_event() method, completing the IScene migration.
        """
        for event in events:
            state_before = self.state

            if event.type == pygame.QUIT:
                self._router.show_exit_dialog = True
            elif event.type == pygame.KEYDOWN:
                action = self._boot.input_mapper.resolve(event, contexts=["global"])
                if action == InputAction.GLOBAL_EXIT:
                    self._router.show_exit_dialog = True
                elif action == InputAction.GLOBAL_TOGGLE_PROFILER:
                    active = self._boot.ctx.profiler.toggle()
                    logger.info(f"Profiling {'ENABLED' if active else 'DISABLED'}")
            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event.w, event.h)

            # Forward events to current scene only if state didn't change.
            if self.state != state_before:
                logger.debug(f"State changed from {state_before} to {self.state}")
                continue

            self._forward_event_to_scene(event)

    def _forward_event_to_scene(self, event: Any) -> None:
        """Forward event to the current active scene (PROJ-65: unified dispatch)."""
        # Handle overlay dialogs on menu — these use the menu's ui_manager.
        if self.state == GameState.MENU:
            if self._router.showing_new_game_setup:
                self._router.menu_ui_manager.process_events(event)
                return
            if self._router.showing_load_menu:
                self._router.menu_ui_manager.process_events(event)
                return
            if self._router.showing_race_setup:
                self._router.menu_ui_manager.process_events(event)
                return

        # Unified dispatch to active scene.
        self._router.active_scene.handle_event(event)

    def _handle_resize(self, w: int, h: int) -> None:
        """Handle window resize (PROJ-65: unified dispatch)."""
        self._boot_set_resolution(w, h)
        self._router.update_resolution(w, h)
        # Unified dispatch to active scene.
        self._router.active_scene.handle_resize(w, h)

    def _boot_set_resolution(self, w: int, h: int) -> None:
        """Replace the display surface at the new resolution.

        BootstrapResult is a frozen dataclass; we mutate object members
        only via this helper so the run loop reads consistent state.
        """
        new_surface = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        # Frozen dataclass — bypass via object.__setattr__ for the
        # mutation that pygame's resize semantics force on us.
        object.__setattr__(self._boot, "screen", new_surface)
        object.__setattr__(self._boot, "width", w)
        object.__setattr__(self._boot, "height", h)

    # ------------------------------------------------------------------
    # Update + draw
    # ------------------------------------------------------------------

    def _update_and_draw(self, frame_time: float, events: list[Any]) -> None:
        """Update logic and draw current scene (PROJ-65: unified dispatch).

        PROJ-88 Phase 5: StrategyScreen event dispatch is now fully through
        handle_event(). The update_input() call remains for per-frame keyboard
        polling (arrow keys for panning) and hover logic.
        """
        screen = self._boot.screen
        font_med = self._boot.font_med
        font_large = self._boot.font_large
        ctx = self._boot.ctx
        router = self._router

        # Per-frame input handling (keyboard polling, hover).
        # Scenes that need per-frame keyboard polling expose update_input(dt, events);
        # IScene only mandates handle_event/update/draw/handle_resize.
        if self.state == GameState.STRATEGY:
            router.strategy_scene.update_input(frame_time, events)
        elif self.state in (GameState.RESEARCH_TREE, GameState.GALAXY_TEST):
            router.active_scene.update_input(frame_time, events)

        # Unified update dispatch.
        router.active_scene.update(frame_time)

        # Unified draw dispatch (some scenes have special draw logic).
        if self.state == GameState.BATTLE:
            # BattleScreen handles headless mode internally.
            if not router.battle_scene.headless_mode:
                router.active_scene.draw(screen)
                router.battle_scene.draw_hud(screen, font_med, ctx.profiler.is_active())
        else:
            router.active_scene.draw(screen)

        if router.show_exit_dialog:
            self._exit_dialog.draw(screen, font_large, font_med)
