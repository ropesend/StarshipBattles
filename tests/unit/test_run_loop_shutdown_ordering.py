"""PROJ-366 Phase 2 — RunLoop shutdown ordering invariant.

Pins the order `shutdown_all_calls` -> `shutdown_all_coordinators` ->
`pygame.quit()` so any future flip is loud (the test name itself surfaces
the contract). Per Codex r002: today's order is grounded in the current
AI factory shape (no LLM dependency in the verifier path,
`game/ai/ai_factory.py:21-29,83-110`); revisit if a future verifier path
invokes LLM work.

Per Codex r001 (lazy-import patch targets): the `RunLoop.run()` method
imports both `shutdown_all_calls` and `shutdown_all_coordinators` LOCALLY
inside the function body. Patching `game.run_loop` for those names misses
the local imports — we MUST patch the SOURCE modules:

  * `game.services.llm.background.shutdown_all_calls`
  * `game.strategy.services.replay_verification_coordinator.shutdown_all_coordinators`
"""
from __future__ import annotations

import os
from typing import List
from unittest.mock import patch

# Headless pygame so `pygame.quit()` does not need a display.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def test_shutdown_order_llm_then_coordinator_then_pygame() -> None:
    """`shutdown_all_calls` MUST run before `shutdown_all_coordinators`,
    which MUST run before `pygame.quit()`.

    The test name pins the current ordering. If a future change flips the
    order (e.g. because a future verifier path invokes an LLM), this test
    will fail by name and force a deliberate decision.
    """
    import pygame

    from game.services.llm import background as llm_background_mod
    from game.strategy.services import replay_verification_coordinator as rvc_mod
    from game import run_loop as run_loop_mod

    call_order: List[str] = []

    def record_shutdown_all_calls(timeout: float = 5.0) -> None:
        call_order.append("shutdown_all_calls")

    def record_shutdown_all_coordinators(timeout: float = 5.0) -> None:
        call_order.append("shutdown_all_coordinators")

    def record_pygame_quit() -> None:
        call_order.append("pygame.quit")

    # Construct a RunLoop with stubs sufficient for the loop to immediately
    # exit (running=False). The RunLoop ctor wants `boot`, `router`,
    # `state_machine` — we use lightweight placeholders since `run()` will
    # never enter the frame body.
    class _StubBoot:
        class _Clock:
            def tick(self, _fps):
                return 0
        clock = _Clock()

    class _StubRouter:
        show_exit_dialog = False

    class _StubStateMachine:
        state = None

    rl = run_loop_mod.RunLoop(
        boot=_StubBoot(),  # type: ignore[arg-type]
        router=_StubRouter(),  # type: ignore[arg-type]
        state_machine=_StubStateMachine(),  # type: ignore[arg-type]
    )
    rl.running = False  # exit before entering the frame body

    with patch.object(llm_background_mod, "shutdown_all_calls",
                      record_shutdown_all_calls), \
         patch.object(rvc_mod, "shutdown_all_coordinators",
                      record_shutdown_all_coordinators), \
         patch.object(pygame, "quit", record_pygame_quit):
        rl.run()

    assert call_order == [
        "shutdown_all_calls",
        "shutdown_all_coordinators",
        "pygame.quit",
    ], f"shutdown order broke: {call_order}"
