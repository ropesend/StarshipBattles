"""Tests for StormAbilitySource (PROJ-300 Phase 3)."""
from dataclasses import dataclass
from typing import Any, FrozenSet

import pytest

from game.core.hex_math import HexCoord
from game.core.protocols import IAbilitySource, is_ability_source
from game.strategy.data.storm import Storm, StormEffect
from game.strategy.services.ability_sources import StormAbilitySource


def _make_storm(name="Ion Storm Alpha", storm_type="ion_storm",
                shield_capacity_mult=1.0, thrust_mult=1.0,
                strategic_mult=1.0, damage_per_tick=0.0,
                fuel_drain_per_tick=0.0):
    return Storm(
        name=name,
        storm_type=storm_type,
        location=HexCoord(0, 0),
        hex_offsets=frozenset({HexCoord(0, 0), HexCoord(1, 0)}),
        effects=StormEffect(
            shield_capacity_mult=shield_capacity_mult,
            thrust_mult=thrust_mult,
            strategic_mult=strategic_mult,
            damage_per_tick=damage_per_tick,
            fuel_drain_per_tick=fuel_drain_per_tick,
        ),
    )


def test_source_kind_is_storm():
    src = StormAbilitySource(storm=_make_storm())
    assert src.source_kind == 'storm'


def test_source_label_is_storm_name():
    src = StormAbilitySource(storm=_make_storm(name="Ion Storm Alpha"))
    assert src.source_label == "Ion Storm Alpha"


def test_source_id_stable_and_prefixed():
    storm = _make_storm(name="Ion Storm Alpha")
    a = StormAbilitySource(storm=storm)
    b = StormAbilitySource(storm=storm)
    assert a.source_id == b.source_id
    assert a.source_id.startswith("storm:")


def test_owner_id_is_none():
    src = StormAbilitySource(storm=_make_storm())
    assert src.owner_id is None


def test_get_abilities_translates_legacy_shield():
    src = StormAbilitySource(storm=_make_storm(shield_capacity_mult=0.5))
    abilities = src.get_abilities()
    assert "ShieldModifier" in abilities
    assert abilities["ShieldModifier"]["multiplier"] == 0.5
    assert abilities["ShieldModifier"]["scope"] == "sector"


def test_get_abilities_translates_legacy_shield_alone():
    src = StormAbilitySource(storm=_make_storm(shield_capacity_mult=0.5))
    abilities = src.get_abilities()
    assert abilities["ShieldModifier"]["multiplier"] == 0.5
    assert "StrategicSpeedModifier" not in abilities  # neutral default


def test_get_abilities_translates_legacy_strategic_speed():
    src = StormAbilitySource(storm=_make_storm(strategic_mult=0.4))
    abilities = src.get_abilities()
    assert abilities["StrategicSpeedModifier"]["multiplier"] == 0.4


def test_get_abilities_translates_legacy_thrust():
    src = StormAbilitySource(storm=_make_storm(thrust_mult=0.6))
    abilities = src.get_abilities()
    assert abilities["ThrustModifier"]["multiplier"] == 0.6


def test_get_abilities_translates_legacy_damage_per_tick_to_per_turn():
    """Legacy data was per-tick; framework speaks per-turn (x100)."""
    src = StormAbilitySource(storm=_make_storm(damage_per_tick=0.005))
    abilities = src.get_abilities()
    assert abilities["EnvironmentalDamage"]["rate"] == pytest.approx(0.5)
    assert abilities["EnvironmentalDamage"]["damage_type"] == "environmental"


def test_get_abilities_translates_fuel_drain_per_tick_to_per_turn():
    src = StormAbilitySource(storm=_make_storm(fuel_drain_per_tick=0.001))
    abilities = src.get_abilities()
    assert abilities["FuelDrain"]["rate"] == pytest.approx(0.1)


def test_get_abilities_skips_neutral_values():
    """A storm with default (no-effect) fields produces no abilities."""
    src = StormAbilitySource(storm=_make_storm())  # all defaults
    assert src.get_abilities() == {}


def test_get_abilities_uses_new_dict_when_present():
    """Phase 5 readiness: if storm.abilities exists, use it directly."""
    @dataclass
    class _StormWithAbilities:
        name: str = "Plasma Storm"
        abilities: Any = None
        occupied_hexes: FrozenSet = frozenset()

        def __post_init__(self):
            if self.abilities is None:
                self.abilities = {
                    "EnvironmentalDamage": {"rate": 0.5, "damage_type": "plasma", "scope": "sector"},
                }

    storm = _StormWithAbilities()
    src = StormAbilitySource(storm=storm)
    assert src.get_abilities() == storm.abilities


def test_affects_hex_true_for_occupied():
    storm = _make_storm()
    src = StormAbilitySource(storm=storm)
    # storm covers HexCoord(0,0) and HexCoord(1,0) (location 0,0 + offsets)
    assert src.affects_hex(HexCoord(0, 0)) is True
    assert src.affects_hex(HexCoord(1, 0)) is True


def test_affects_hex_false_outside():
    src = StormAbilitySource(storm=_make_storm())
    assert src.affects_hex(HexCoord(99, 99)) is False


def test_get_activation_state_is_none():
    src = StormAbilitySource(storm=_make_storm())
    assert src.get_activation_state("ShieldModifier") is None


def test_satisfies_iability_source_protocol():
    src = StormAbilitySource(storm=_make_storm())
    assert isinstance(src, IAbilitySource)
    assert is_ability_source(src)
