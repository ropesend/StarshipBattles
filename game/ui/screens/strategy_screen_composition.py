"""PROJ-327 Phase 4 — StrategyScreen sub-object composition factory.

`StrategyScreen` orchestrates 8 collaborator sub-objects (renderer, camera
navigator, fleet ops, colonization, superweapons, build queue manager, game
state manager, input handler). Historically `__init__` constructed each
inline, which forced tests to either:

1. Run the full `StrategyScreen.__init__` (heavy: pygame imports, asset
   loading, real Camera, real StrategyUI), or
2. Bypass `__init__` via ``patch.object(StrategyScreen, '__init__', lambda
   self, *a, **kw: None)`` and ``StrategyScreen.__new__(StrategyScreen)``,
   then manually populate every attribute the production code reads.

Option (2) is the brittle "bypass-init + repaint" pattern flagged in the
PROJ-322 OpenCode review and tracked as PROJ-322 Task 3.25.

The Compositional Construction pattern (PROJ-327 Phase 4) splits the seam
*before* `__init__` runs: `StrategyScreen.__init__` accepts an optional
``composition: StrategyScreenComposition`` parameter. Default to the
production `StrategyScreenCompositionFactory` (existing wiring moved
verbatim). Tests pass a ``MockStrategyScreenComposition`` from
``tests/fixtures/strategy_screen_composition.py`` to substitute any
sub-object without monkey-patching ``__init__`` or ``__new__``.

Same shape as PROJ-325's `DefaultRaceSetupDelegateFactory` (RaceSetupScreen
delegates) and PROJ-322's `make_ui_widget` factory. See
``docs/02_PATTERNS.md`` § "Compositional Construction".
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from game.ui.screens.strategy_build_queue_manager import StrategyBuildQueueManager
from game.ui.screens.strategy_camera_nav import CameraNavigator
from game.ui.screens.strategy_colonization import ColonizationSystem
from game.ui.screens.strategy_fleet_ops import FleetOperations
from game.ui.screens.strategy_game_state_manager import StrategyGameStateManager
from game.ui.screens.strategy_input_handler import StrategyInputHandler
from game.ui.screens.strategy_renderer import StrategyRenderer
from game.ui.screens.strategy_superweapons import SuperweaponOperations

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen


class StrategyScreenComposition(Protocol):
    """Factory protocol for `StrategyScreen`'s 8 sub-object collaborators.

    Each ``make_*`` method receives the partially-initialized screen (state
    + facade + camera + ui already populated) and returns the constructed
    sub-object. Production wiring lives in `StrategyScreenCompositionFactory`;
    tests substitute via `MockStrategyScreenComposition`.
    """

    def make_renderer(self, screen: "StrategyScreen") -> StrategyRenderer: ...

    def make_camera_navigator(self, screen: "StrategyScreen") -> CameraNavigator: ...

    def make_fleet_ops(self, screen: "StrategyScreen") -> FleetOperations: ...

    def make_colonization(self, screen: "StrategyScreen") -> ColonizationSystem: ...

    def make_superweapons(self, screen: "StrategyScreen") -> SuperweaponOperations: ...

    def make_build_queue_manager(
        self, screen: "StrategyScreen"
    ) -> StrategyBuildQueueManager: ...

    def make_game_state_manager(
        self, screen: "StrategyScreen"
    ) -> StrategyGameStateManager: ...

    def make_input_handler(self, screen: "StrategyScreen") -> StrategyInputHandler: ...


class StrategyScreenCompositionFactory:
    """Default production composition — wires the sub-object graph verbatim.

    Each ``make_*`` method calls the same constructor `StrategyScreen.__init__`
    used inline pre-PROJ-327. Behaviour is unchanged; the only delta is
    that the wiring lives behind a swappable seam.
    """

    def make_renderer(self, screen: "StrategyScreen") -> StrategyRenderer:
        return StrategyRenderer(screen)

    def make_camera_navigator(self, screen: "StrategyScreen") -> CameraNavigator:
        return CameraNavigator(screen)

    def make_fleet_ops(self, screen: "StrategyScreen") -> FleetOperations:
        return FleetOperations(screen, screen._facade)

    def make_colonization(self, screen: "StrategyScreen") -> ColonizationSystem:
        return ColonizationSystem(screen, screen._facade)

    def make_superweapons(self, screen: "StrategyScreen") -> SuperweaponOperations:
        return SuperweaponOperations(screen, screen._facade)

    def make_build_queue_manager(
        self, screen: "StrategyScreen"
    ) -> StrategyBuildQueueManager:
        return StrategyBuildQueueManager(screen)

    def make_game_state_manager(
        self, screen: "StrategyScreen"
    ) -> StrategyGameStateManager:
        return StrategyGameStateManager(screen)

    def make_input_handler(self, screen: "StrategyScreen") -> StrategyInputHandler:
        return StrategyInputHandler(screen, input_mapper=screen.input_mapper)


__all__ = ["StrategyScreenComposition", "StrategyScreenCompositionFactory"]
