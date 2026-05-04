"""PROJ-331 Phase 2b: characterization tests for `BattleController.start_from_spec`.

Pins observable behavior of the unified spec-in entry point (PROJ-270
Phase 10): registry-provider fallback, RuntimeError on missing builder,
default-config construction, boundary fallback, and ship_id_map population.

Per D-005: `start_engine_from_spec` is patched at the import location
inside `start_from_spec` so the controller's wiring is the unit under
test. Real engine construction is out of scope.
"""
from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from game.simulation.battle_config import BattleConfig
from game.simulation.battle_controller import BattleController
from game.simulation.combat.boundary import UnboundedRegion
from game.simulation.services.battle_service import BattleServiceResult


def _make_spec(*, boundary=None):
    """Construct a `MagicMock` BattleSpec with the fields start_from_spec reads."""
    spec = MagicMock(name="BattleSpec")
    spec.seed = 42
    spec.end_condition = MagicMock(name="end_condition")
    spec.absolute_max_ticks = 1000
    spec.boundary = boundary
    spec.modifier_stack = MagicMock(name="modifier_stack")
    spec.post_battle_hook = None
    return spec


def _make_engine(*, ships=()):
    engine = MagicMock(name="BattleEngine")
    engine.ships = list(ships)
    engine.projectiles = []
    engine.tick_counter = 0
    engine.end_condition = None
    return engine


def _make_engine_ship(ship_id):
    s = MagicMock(name=f"Ship_{ship_id}")
    s.id = ship_id
    s.team_id = 0
    return s


@pytest.fixture
def mock_service():
    service = Mock()
    service.adopt_started_engine.return_value = BattleServiceResult(success=True)
    return service


@pytest.fixture
def controller(mock_service):
    return BattleController(service=mock_service)


# ---------------------------------------------------------------------------
# Builder / registry-provider gating
# ---------------------------------------------------------------------------


class TestStartFromSpecBuilderGating:
    def test_start_from_spec_raises_runtimeerror_when_no_ship_builder_and_no_registry_provider(
        self, controller,
    ):
        spec = _make_spec()
        with pytest.raises(RuntimeError) as exc_info:
            controller.start_from_spec(
                spec, ai_factory=Mock(),
                ship_builder=None, registry_provider=None,
            )
        # PROJ-252 message fragment.
        assert "PROJ-252" in str(exc_info.value) or "registry_provider" in str(exc_info.value)

    def test_start_from_spec_uses_explicit_ship_builder_when_provided(
        self, controller,
    ):
        spec = _make_spec()
        explicit_builder = Mock(name="explicit_builder")
        ai_factory = Mock()
        engine = _make_engine()

        with patch(
            "game.simulation.battle_runner.start_engine_from_spec",
            return_value=(engine, {}),
        ) as mock_start, patch(
            "game.simulation.battle_runner.build_context_ship_builder",
        ) as mock_build_ctx, patch.object(
            controller._state_manager, "capture_state", return_value=Mock(),
        ):
            controller.start_from_spec(
                spec, ai_factory=ai_factory,
                ship_builder=explicit_builder,
            )

        # build_context_ship_builder was NOT used (explicit takes precedence).
        mock_build_ctx.assert_not_called()
        # start_engine_from_spec received the explicit builder.
        kwargs = mock_start.call_args.kwargs
        assert kwargs["ship_builder"] is explicit_builder

    def test_start_from_spec_falls_back_to_context_builder_when_registry_provider_supplied(
        self, controller,
    ):
        spec = _make_spec()
        registry_provider = Mock(name="registry_provider")
        ai_factory = Mock()
        engine = _make_engine()
        ctx_builder = Mock(name="context_builder")

        with patch(
            "game.simulation.battle_runner.start_engine_from_spec",
            return_value=(engine, {}),
        ), patch(
            "game.simulation.battle_runner.build_context_ship_builder",
            return_value=ctx_builder,
        ) as mock_build_ctx, patch.object(
            controller._state_manager, "capture_state", return_value=Mock(),
        ):
            controller.start_from_spec(
                spec, ai_factory=ai_factory,
                ship_builder=None, registry_provider=registry_provider,
            )

        mock_build_ctx.assert_called_once_with(registry_provider=registry_provider)


# ---------------------------------------------------------------------------
# Config / boundary defaults
# ---------------------------------------------------------------------------


class TestStartFromSpecConfigAndBoundary:
    def test_start_from_spec_constructs_default_battleconfig_when_config_none(
        self, controller,
    ):
        spec = _make_spec()
        engine = _make_engine()

        with patch(
            "game.simulation.battle_runner.start_engine_from_spec",
            return_value=(engine, {}),
        ), patch.object(
            controller._state_manager, "capture_state", return_value=Mock(),
        ):
            controller.start_from_spec(
                spec, ai_factory=Mock(),
                ship_builder=Mock(),
                config=None,
            )

        assert controller._config is not None
        assert controller._config.seed == spec.seed
        assert controller._config.absolute_max_ticks == spec.absolute_max_ticks

    def test_start_from_spec_uses_provided_battleconfig_when_supplied(
        self, controller,
    ):
        spec = _make_spec()
        engine = _make_engine()
        explicit_config = BattleConfig(seed=99, absolute_max_ticks=500)

        with patch(
            "game.simulation.battle_runner.start_engine_from_spec",
            return_value=(engine, {}),
        ), patch.object(
            controller._state_manager, "capture_state", return_value=Mock(),
        ):
            controller.start_from_spec(
                spec, ai_factory=Mock(),
                ship_builder=Mock(),
                config=explicit_config,
            )

        assert controller._config is explicit_config

    def test_start_from_spec_constructs_unbounded_region_when_spec_has_no_boundary(
        self, controller,
    ):
        spec = _make_spec(boundary=None)
        engine = _make_engine()

        with patch(
            "game.simulation.battle_runner.start_engine_from_spec",
            return_value=(engine, {}),
        ), patch.object(
            controller._state_manager, "capture_state", return_value=Mock(),
        ):
            controller.start_from_spec(
                spec, ai_factory=Mock(),
                ship_builder=Mock(),
            )

        assert isinstance(controller._retreat_manager.boundary, UnboundedRegion)

    def test_start_from_spec_uses_spec_boundary_when_present(
        self, controller,
    ):
        # Use a MagicMock standing in for a BoundaryRegion — start_from_spec
        # only checks `spec.boundary is not None` and forwards the object
        # to RetreatManager. We assert identity-preservation, not type.
        rect = MagicMock(name="RectBoundary")
        spec = _make_spec(boundary=rect)
        engine = _make_engine()

        with patch(
            "game.simulation.battle_runner.start_engine_from_spec",
            return_value=(engine, {}),
        ), patch.object(
            controller._state_manager, "capture_state", return_value=Mock(),
        ):
            controller.start_from_spec(
                spec, ai_factory=Mock(),
                ship_builder=Mock(),
            )

        assert controller._retreat_manager.boundary is rect


# ---------------------------------------------------------------------------
# Ship-id map
# ---------------------------------------------------------------------------


class TestStartFromSpecShipIdMap:
    def test_start_from_spec_populates_ship_id_map_from_engine_ships(
        self, controller,
    ):
        spec = _make_spec()
        ships = [
            _make_engine_ship("ship_a"),
            _make_engine_ship("ship_b"),
            _make_engine_ship("ship_c"),
        ]
        engine = _make_engine(ships=ships)

        with patch(
            "game.simulation.battle_runner.start_engine_from_spec",
            return_value=(engine, {}),
        ), patch.object(
            controller._state_manager, "capture_state", return_value=Mock(),
        ):
            controller.start_from_spec(
                spec, ai_factory=Mock(),
                ship_builder=Mock(),
            )

        assert len(controller._ship_id_map) == 3
        # Each engine ship.id maps to itself.
        for s in ships:
            assert controller._ship_id_map[s.id] == s.id
