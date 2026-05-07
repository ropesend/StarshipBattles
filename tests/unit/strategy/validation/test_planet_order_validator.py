"""Tests for planet order validation helpers."""

from dataclasses import dataclass
from typing import Any

from game.strategy.validation.planet_order_validator import _facility_has_ability


@dataclass
class _Facility:
    design_data: dict[str, Any]


def test_facility_has_ability_from_inline_component_abilities():
    facility = _Facility(
        design_data={
            "layers": {
                "CORE": [
                    {"id": "inline_shield", "abilities": {"PlanetaryShield": True}},
                ],
            },
        },
    )

    assert _facility_has_ability(facility, "PlanetaryShield") is True


def test_facility_has_ability_from_dict_component_registry_lookup():
    facility = _Facility(
        design_data={
            "layers": {
                "CORE": [
                    {"id": "shield_generator"},
                ],
            },
        },
    )
    registry = {
        "shield_generator": {"abilities": {"PlanetaryShield": {"upkeep": 2}}},
    }

    assert _facility_has_ability(facility, "PlanetaryShield", registry) is True


def test_facility_has_ability_from_string_component_registry_lookup():
    facility = _Facility(
        design_data={
            "layers": {
                "CORE": {
                    "components": ["stabilizer"],
                },
            },
        },
    )
    registry = {
        "stabilizer": {"abilities": {"GeologicStabilizer": True}},
    }

    assert _facility_has_ability(facility, "GeologicStabilizer", registry) is True


def test_facility_has_ability_returns_false_without_matching_ability():
    facility = _Facility(
        design_data={
            "layers": {
                "CORE": [
                    {"id": "reactor"},
                    "missing_from_registry",
                    123,
                ],
            },
        },
    )
    registry = {
        "reactor": {"abilities": {"ResourceGeneration": {"resource": "fuel"}}},
    }

    assert _facility_has_ability(facility, "PlanetaryShield", registry) is False
