"""PROJ-327 Phase 4 — smoke tests for ``StrategyScreenComposition``.

Pins the protocol contract: every ``make_*`` slot returns the right
production type from the default factory, and every slot returns the
test-side ``MagicMock`` from ``MockStrategyScreenComposition``. Adding a
new sub-object to ``StrategyScreen`` should fail one of these tests until
the slot is added to both the production factory and the mock fixture.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.ui.screens.strategy_build_queue_manager import StrategyBuildQueueManager
from game.ui.screens.strategy_camera_nav import CameraNavigator
from game.ui.screens.strategy_colonization import ColonizationSystem
from game.ui.screens.strategy_fleet_ops import FleetOperations
from game.ui.screens.strategy_game_state_manager import StrategyGameStateManager
from game.ui.screens.strategy_input_handler import StrategyInputHandler
from game.ui.screens.strategy_renderer import StrategyRenderer
from game.ui.screens.strategy_screen_composition import (
    StrategyScreenCompositionFactory,
)
from game.ui.screens.strategy_superweapons import SuperweaponOperations
from tests.fixtures.strategy_screen_composition import MockStrategyScreenComposition


def _stub_screen():
    """Build the minimal stub that the production ``make_*`` methods read.

    They read ``screen``, ``screen._facade``, and ``screen.input_mapper``.
    """
    screen = MagicMock(name="screen")
    screen._facade = MagicMock(name="facade")
    screen.input_mapper = MagicMock(name="input_mapper")
    return screen


class TestDefaultFactoryProductionTypes:
    """Default factory produces real production sub-object instances."""

    def test_make_renderer_returns_strategy_renderer(self):
        factory = StrategyScreenCompositionFactory()
        result = factory.make_renderer(_stub_screen())
        assert isinstance(result, StrategyRenderer)

    def test_make_camera_navigator_returns_camera_navigator(self):
        factory = StrategyScreenCompositionFactory()
        result = factory.make_camera_navigator(_stub_screen())
        assert isinstance(result, CameraNavigator)

    def test_make_fleet_ops_returns_fleet_operations(self):
        factory = StrategyScreenCompositionFactory()
        result = factory.make_fleet_ops(_stub_screen())
        assert isinstance(result, FleetOperations)

    def test_make_colonization_returns_colonization_system(self):
        factory = StrategyScreenCompositionFactory()
        result = factory.make_colonization(_stub_screen())
        assert isinstance(result, ColonizationSystem)

    def test_make_superweapons_returns_superweapon_operations(self):
        factory = StrategyScreenCompositionFactory()
        result = factory.make_superweapons(_stub_screen())
        assert isinstance(result, SuperweaponOperations)

    def test_make_build_queue_manager_returns_build_queue_manager(self):
        factory = StrategyScreenCompositionFactory()
        result = factory.make_build_queue_manager(_stub_screen())
        assert isinstance(result, StrategyBuildQueueManager)

    def test_make_game_state_manager_returns_game_state_manager(self):
        factory = StrategyScreenCompositionFactory()
        result = factory.make_game_state_manager(_stub_screen())
        assert isinstance(result, StrategyGameStateManager)

    def test_make_input_handler_returns_input_handler(self):
        factory = StrategyScreenCompositionFactory()
        result = factory.make_input_handler(_stub_screen())
        assert isinstance(result, StrategyInputHandler)


class TestMockCompositionReturnsSameInstancePerSlot:
    """MockStrategyScreenComposition returns the pre-stored mock per slot."""

    @pytest.mark.parametrize(
        "slot_attr,method_name",
        [
            ("renderer", "make_renderer"),
            ("camera_nav", "make_camera_navigator"),
            ("fleet_ops", "make_fleet_ops"),
            ("colonization", "make_colonization"),
            ("superweapons", "make_superweapons"),
            ("build_queue", "make_build_queue_manager"),
            ("game_state", "make_game_state_manager"),
            ("input_handler", "make_input_handler"),
        ],
    )
    def test_make_returns_pre_stored_mock(self, slot_attr, method_name):
        comp = MockStrategyScreenComposition()
        screen = MagicMock(name="screen")
        result = getattr(comp, method_name)(screen)
        assert result is getattr(comp, slot_attr)


class TestMockCompositionPopulate:
    """`populate(screen)` wires all 8 sub-object attributes onto a screen."""

    def test_populate_sets_all_eight_slots(self):
        comp = MockStrategyScreenComposition()
        screen = MagicMock(name="screen")

        comp.populate(screen)

        assert screen._renderer is comp.renderer
        assert screen._camera_nav is comp.camera_nav
        assert screen._fleet_ops is comp.fleet_ops
        assert screen._colonization is comp.colonization
        assert screen._superweapons is comp.superweapons
        assert screen._build_queue is comp.build_queue
        assert screen._game_state is comp.game_state
        assert screen._input is comp.input_handler
