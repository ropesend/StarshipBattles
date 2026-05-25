"""PROJ-333 Phase 1: ConsumableManagementEngine surface-gap characterization.

Supplements the three existing test files (initialization, consumption,
auto_disable) with the precise behavioral edges flagged in PROJ-333
design.md: validation paths, the hard-coded `/100.0` divisor (not the
TICKS_PER_TURN constant), the consume-fail → auto-disable handoff,
and layer-format / trigger-mismatch / unknown-id branches in
`_auto_disable_components_for_resource`.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.exceptions import ValidationException
from game.core.registry import GameRegistries
from game.strategy.engine.consumable_management_engine import (
    ConsumableManagementEngine,
    ResourceDepletion,
)


# ---------------------------------------------------------------------------
# init / validate_tick_inputs
# ---------------------------------------------------------------------------


def test_init_raises_validation_when_registries_none():
    """Strict DI: None registries blow up at construction time."""
    with pytest.raises(ValidationException) as exc_info:
        ConsumableManagementEngine(registries=None)
    assert "registries is required" in str(exc_info.value)


def test_validate_tick_inputs_raises_when_fleet_ships_is_none(mock_registries, mock_empire, mock_fleet):
    """`fleet.ships is None` → ValidationException before mutation."""
    mock_fleet.ships = None
    engine = ConsumableManagementEngine(registries=mock_registries)
    with pytest.raises(ValidationException):
        engine.process_per_turn_consumption(1, [mock_empire])


# ---------------------------------------------------------------------------
# Per-tick consumption gating
# ---------------------------------------------------------------------------


def test_non_combat_capable_ship_is_skipped(mock_registries, mock_empire, mock_fleet, mock_ship):
    """`is_combat_capable() == False` skips the ship entirely (no consume call)."""
    mock_ship.is_combat_capable.return_value = False
    mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 999.0}
    engine = ConsumableManagementEngine(registries=mock_registries)
    engine.process_per_turn_consumption(1, [mock_empire])
    mock_ship.consume_resource.assert_not_called()


def test_zero_cost_resource_is_skipped(mock_registries, mock_empire, mock_fleet, mock_ship):
    """A resource with `total_cost <= 0` is not consumed."""
    mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 0.0}
    engine = ConsumableManagementEngine(registries=mock_registries)
    engine.process_per_turn_consumption(1, [mock_empire])
    mock_ship.consume_resource.assert_not_called()


def test_per_tick_consumption_is_one_hundredth_of_per_turn_total(
    mock_registries, mock_empire, mock_fleet, mock_ship,
):
    """Each tick consumes `total_cost / 100.0` (hard-coded, not TICKS_PER_TURN)."""
    mock_ship.get_all_resource_costs_per_turn.return_value = {"power": 250.0}
    mock_ship.consume_resource.return_value = True
    engine = ConsumableManagementEngine(registries=mock_registries)

    engine.process_per_turn_consumption(1, [mock_empire])
    mock_ship.consume_resource.assert_called_once_with("power", 2.5)


# ---------------------------------------------------------------------------
# Auto-disable on consume_resource() == False
# ---------------------------------------------------------------------------


def test_failed_consume_resource_triggers_auto_disable_and_returns_depletion(
    mock_empire, mock_fleet, mock_ship,
):
    """`consume_resource → False` produces a `ResourceDepletion` entry whose
    ``components_disabled`` reflects the real auto-disable scan.

    PROJ-491 Task 1.10: removed the prior
    ``patch.object(engine, '_auto_disable_components_for_resource')`` mock;
    instead, wire a real component definition with a ``ResourceConsumption``
    per_turn fuel ability into the registry and let the engine perform the
    real disable scan. Public-surface assertions verify both the
    ``ResourceDepletion`` shape and that ``set_component_enabled`` fired
    for the matching component.
    """
    mock_ship.name = "Argo"
    mock_ship.get_all_resource_costs_per_turn.return_value = {"fuel": 100.0}
    mock_ship.consume_resource.return_value = False

    # Real component definition that the auto-disable scan should pick up.
    engine_comp_def = MagicMock()
    engine_comp_def.abilities = {
        "ResourceConsumption": [{"trigger": "per_turn", "resource": "fuel"}],
    }
    mock_ship.design_data = {"layers": {"core": [{"id": "engine_1"}]}}

    engine = _make_engine_with_components({"engine_1": engine_comp_def})

    result = engine.process_per_turn_consumption(1, [mock_empire])

    assert len(result) == 1
    assert isinstance(result[0], ResourceDepletion)
    assert result[0].ship_name == "Argo"
    assert result[0].resource_type == "fuel"
    assert result[0].components_disabled == ["engine_1"]
    mock_ship.set_component_enabled.assert_called_with("engine_1", False)


# ---------------------------------------------------------------------------
# _auto_disable_components_for_resource layer-format dispatch
# ---------------------------------------------------------------------------


def _make_engine_with_components(comp_map: dict) -> ConsumableManagementEngine:
    return ConsumableManagementEngine(
        registries=GameRegistries(
            components=comp_map, modifiers={}, vehicle_classes={}, resources={},
        )
    )


def test_auto_disable_handles_layers_as_list_format(mock_ship):
    """Layer value as a plain list of component-entries is iterated."""
    comp_def = MagicMock()
    comp_def.abilities = {
        "ResourceConsumption": [{"trigger": "per_turn", "resource": "power"}],
    }
    mock_ship.design_data = {"layers": {"core": [{"id": "reactor"}]}}
    engine = _make_engine_with_components({"reactor": comp_def})

    disabled = engine._auto_disable_components_for_resource(mock_ship, "power")

    assert "reactor" in disabled
    mock_ship.set_component_enabled.assert_called_with("reactor", False)


def test_auto_disable_handles_layers_as_dict_with_components_key(mock_ship):
    """Layer value as `{'components': [...]}` is also iterated."""
    comp_def = MagicMock()
    comp_def.abilities = {
        "ResourceConsumption": [{"trigger": "per_turn", "resource": "power"}],
    }
    mock_ship.design_data = {
        "layers": {"core": {"components": [{"id": "reactor"}]}},
    }
    engine = _make_engine_with_components({"reactor": comp_def})

    disabled = engine._auto_disable_components_for_resource(mock_ship, "power")
    assert "reactor" in disabled


def test_auto_disable_skips_unknown_component_id(mock_ship):
    """Component id absent from registry is silently skipped."""
    mock_ship.design_data = {"layers": {"core": [{"id": "ghost"}]}}
    engine = _make_engine_with_components({})

    disabled = engine._auto_disable_components_for_resource(mock_ship, "power")
    assert disabled == []
    mock_ship.set_component_enabled.assert_not_called()


def test_auto_disable_only_targets_per_turn_trigger_for_matching_resource(mock_ship):
    """Mismatched trigger OR mismatched resource → component is NOT disabled."""
    wrong_trigger = MagicMock()
    wrong_trigger.abilities = {
        "ResourceConsumption": [{"trigger": "on_fire", "resource": "power"}],
    }
    wrong_resource = MagicMock()
    wrong_resource.abilities = {
        "ResourceConsumption": [{"trigger": "per_turn", "resource": "fuel"}],
    }
    correct = MagicMock()
    correct.abilities = {
        "ResourceConsumption": [{"trigger": "per_turn", "resource": "power"}],
    }

    mock_ship.design_data = {
        "layers": {
            "core": [
                {"id": "trigger_mismatch"},
                {"id": "resource_mismatch"},
                {"id": "match"},
            ],
        },
    }
    engine = _make_engine_with_components({
        "trigger_mismatch": wrong_trigger,
        "resource_mismatch": wrong_resource,
        "match": correct,
    })

    disabled = engine._auto_disable_components_for_resource(mock_ship, "power")
    assert disabled == ["match"]


def test_auto_disable_iterates_all_matching_components_in_single_call(mock_ship):
    """Multiple matching components are ALL disabled in one tick.

    PROJ-333 design.md Observation 8: auto-disable iterates ALL components
    matching the depleted resource per ship per tick. Two reactors both
    consuming `power` per_turn must both be disabled in a single call,
    and `set_component_enabled(comp_id, False)` must be called for each.
    """
    comp_def = MagicMock()
    comp_def.abilities = {
        "ResourceConsumption": [{"trigger": "per_turn", "resource": "power"}],
    }
    # Two distinct registry entries, both matching, plus a third
    # split across a second layer to prove cross-layer iteration.
    mock_ship.design_data = {
        "layers": {
            "core": [{"id": "reactor_a"}, {"id": "reactor_b"}],
            "aux": [{"id": "reactor_c"}],
        },
    }
    engine = _make_engine_with_components({
        "reactor_a": comp_def,
        "reactor_b": comp_def,
        "reactor_c": comp_def,
    })

    disabled = engine._auto_disable_components_for_resource(mock_ship, "power")

    assert disabled == ["reactor_a", "reactor_b", "reactor_c"]
    assert mock_ship.set_component_enabled.call_count == 3
    mock_ship.set_component_enabled.assert_any_call("reactor_a", False)
    mock_ship.set_component_enabled.assert_any_call("reactor_b", False)
    mock_ship.set_component_enabled.assert_any_call("reactor_c", False)
