"""PROJ-325 Phase 3 — RaceSetup delegate factory + bundle.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``):

The two-stage UIWindow construction pattern separates *cheap* state and
delegate construction from the heavy ``pygame_gui.elements.UIWindow``
shell + widget tree. ``DefaultRaceSetupDelegateFactory`` builds the
``RaceSetupDelegates`` bundle (view_model + renderer + controller +
input_handler + llm_service) before the bypass point so tests can
exercise real delegate behaviour without a live pygame display.

The factory is a tiny dependency-injection seam: ``RaceSetupScreen``
calls ``(delegate_factory or DefaultRaceSetupDelegateFactory()).build(self)``
in its ``__init__``. Tests can pass a custom factory to swap any
delegate without monkey-patching.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from game.ui.screens.race_setup.controller import RaceSetupController
from game.ui.screens.race_setup.input_handler import RaceSetupInputHandler
from game.ui.screens.race_setup.llm_dialog_service import LLMDialogService
from game.ui.screens.race_setup.renderer import RaceSetupRenderer
from game.ui.screens.race_setup.view_model import RaceSetupViewModel

if TYPE_CHECKING:
    from game.ui.screens.race_setup.screen import RaceSetupScreen


@dataclass(frozen=True)
class RaceSetupDelegates:
    """Bundle of MVVM delegates for ``RaceSetupScreen``.

    Each delegate is a *cheap* collaborator in the PROJ-325 sense: its
    constructor does not create ``pygame_gui`` elements or require a
    live display. Construction-time pygame imports inside the delegate
    classes are fine; what matters is that no UI widgets are
    instantiated until a method is called.
    """

    view_model: RaceSetupViewModel
    renderer: RaceSetupRenderer
    controller: RaceSetupController
    input_handler: RaceSetupInputHandler
    llm_service: LLMDialogService


class DefaultRaceSetupDelegateFactory:
    """Default factory — wires the production delegate graph.

    The screen is the local composition root. The factory's job is just
    to keep the wiring out of ``__init__`` so the screen reads as the
    two-stage pattern (state, delegates, bypass-or-shell, builder).
    """

    def build(self, screen: "RaceSetupScreen") -> RaceSetupDelegates:
        view_model = RaceSetupViewModel(is_editing=screen.is_editing)
        renderer = RaceSetupRenderer(screen=screen)
        controller = RaceSetupController(
            screen=screen,
            view_model=view_model,
            renderer=renderer,
            race_config=screen.race_config,
            race_library=screen.race_library,
            race_registry=screen.race_registry,
            on_complete_callback=screen.on_complete_callback,
            on_cancel_callback=screen.on_cancel_callback,
        )
        llm_service = LLMDialogService(
            view_model=view_model,
            renderer=renderer,
        )
        input_handler = RaceSetupInputHandler(screen=screen)
        return RaceSetupDelegates(
            view_model=view_model,
            renderer=renderer,
            controller=controller,
            input_handler=input_handler,
            llm_service=llm_service,
        )


__all__ = ["RaceSetupDelegates", "DefaultRaceSetupDelegateFactory"]
