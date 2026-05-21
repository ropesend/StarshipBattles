"""Tests for fleet capability aggregation helpers."""

from dataclasses import dataclass
from typing import Any

import pytest

from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator


@dataclass
class _Registries:
    components: dict[str, Any]


@dataclass
class _Ship:
    design_data: dict[str, Any]
    _registries: _Registries | None = None


class _Fleet:
    def __init__(self, ships: list[_Ship]) -> None:
        self._ships = ships

    def get_combat_capable_ships(self) -> list[_Ship]:
        return self._ships


def test_list_abilities_returns_empty_list_without_combat_capable_ships():
    calculator = FleetCapabilityCalculator(_Fleet([]), component_registry={})

    assert calculator.list_abilities() == []


def test_list_abilities_returns_unique_abilities_from_all_ships():
    registry = {
        "laser": {"abilities": {"BeamWeapon": {"damage": 10}, "PointDefense": True}},
        "shield": {"abilities": {"ShieldProjection": {"capacity": 100}}},
        "engine": {"abilities": {"StrategicMovement": 2}},
    }
    ships = [
        _Ship({"layers": {"OUTER": [{"id": "laser"}, {"id": "shield"}]}}),
        _Ship({"layers": {"CORE": [{"id": "laser"}, {"id": "engine"}]}}),
    ]
    calculator = FleetCapabilityCalculator(_Fleet(ships), component_registry=registry)

    assert set(calculator.list_abilities()) == {
        "BeamWeapon",
        "PointDefense",
        "ShieldProjection",
        "StrategicMovement",
    }


def test_list_abilities_can_use_first_ship_registries_when_not_injected():
    registry = {
        "warp_drive": {"abilities": {"WarpJump": {"max_tonnage": 1000}}},
    }
    ship = _Ship(
        {"layers": {"CORE": ["warp_drive"]}},
        _registries=_Registries(registry),
    )
    calculator = FleetCapabilityCalculator(_Fleet([ship]))

    assert calculator.list_abilities() == ["WarpJump"]


def test_list_abilities_requires_registry_when_ships_are_present():
    ship = _Ship({"layers": {"CORE": ["warp_drive"]}})
    calculator = FleetCapabilityCalculator(_Fleet([ship]))

    # PROJ-466: missing-registry now raises ValidationException, not ValueError.
    from game.core.exceptions import ValidationException

    with pytest.raises(ValidationException, match="requires a component registry"):
        calculator.list_abilities()
