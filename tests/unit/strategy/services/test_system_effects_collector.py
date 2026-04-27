"""Tests for collect_system_effects() — aggregates system-scope ability effects.

Collects all system-scope abilities from empire-owned colonies in a star system,
returning structured effect data for UI display.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)
from game.strategy.services.system_effects_collector import collect_system_effects


def _make_facility(instance_id, design_data, component_states=None, is_operational=True):
    facility = MagicMock()
    facility.instance_id = instance_id
    facility.name = f"Facility-{instance_id}"
    facility.design_data = design_data
    facility.is_operational = is_operational
    facility.component_states = component_states or {}

    def get_activation_state(key):
        data = facility.component_states.get(key)
        if data is None:
            return ComponentActivationState()
        return ComponentActivationState.from_dict(data)

    facility.get_activation_state = get_activation_state
    return facility


def _make_planet(name, planet_id, facilities=None, owner_id=1):
    planet = MagicMock()
    planet.name = name
    planet.id = planet_id
    planet.owner_id = owner_id
    planet.facilities = facilities or []
    return planet


def _make_system(name, planets):
    system = MagicMock()
    system.name = name
    system.planets = planets
    return system


def _stabilizer_design(comp_id, ability_name, scope="system"):
    """Design with an activatable system-scope ability."""
    return {
        "layers": {
            "OUTER": [{
                "id": comp_id,
                "abilities": {
                    ability_name: {
                        "scope": scope,
                        "energy_drain_rate": 50.0,
                        "activation_time": 250,
                        "deactivation_time": 150,
                    }
                }
            }]
        }
    }


def _harvest_booster_design(comp_id, resource_type, multiplier=1.3):
    """Design with a passive system-scope ResourceHarvestBooster."""
    return {
        "layers": {
            "OUTER": [{
                "id": comp_id,
                "abilities": {
                    "ResourceHarvestBooster": {
                        "resource_type": resource_type,
                        "multiplier": multiplier,
                        "scope": "system",
                        "stack_group": f"harvest_boost_{resource_type}_system",
                    }
                }
            }]
        }
    }


class TestCollectSystemEffects:
    """Tests for collect_system_effects."""

    def test_empty_system_returns_empty(self):
        system = _make_system("Empty", [])
        result = collect_system_effects(system, empire_id=1)
        assert result == []

    def test_no_owned_colonies_returns_empty(self):
        planet = _make_planet("Foreign", 1, owner_id=2)
        system = _make_system("Test", [planet])
        result = collect_system_effects(system, empire_id=1)
        assert result == []

    def test_activatable_ability_active(self):
        """Active GeologicStabilizer shows as active."""
        fac = _make_facility("fac-1", _stabilizer_design("geo_sys", "GeologicStabilizer"),
                             component_states={
                                 "OUTER:0:geo_sys": ComponentActivationState(
                                     phase=ActivationPhase.ACTIVE,
                                     ability_name="GeologicStabilizer",
                                     energy_drain_rate=50.0,
                                 ).to_dict()
                             })
        planet = _make_planet("Akkadia I", 1, facilities=[fac])
        system = _make_system("Akkadia", [planet])

        result = collect_system_effects(system, empire_id=1)

        assert len(result) == 1
        effect = result[0]
        assert effect['ability_name'] == "GeologicStabilizer"
        assert effect['status'] == "Active"
        assert len(effect['providers']) == 1
        assert effect['providers'][0]['planet_name'] == "Akkadia I"
        assert effect['providers'][0]['facility_name'] == "Facility-fac-1"

    def test_activatable_ability_inactive(self):
        """Inactive stabilizer still shows in results."""
        fac = _make_facility("fac-1", _stabilizer_design("geo_sys", "GeologicStabilizer"))
        planet = _make_planet("Akkadia I", 1, facilities=[fac])
        system = _make_system("Akkadia", [planet])

        result = collect_system_effects(system, empire_id=1)

        assert len(result) == 1
        assert result[0]['status'] == "Inactive"

    def test_activatable_ability_activating_shows_progress(self):
        """Activating stabilizer shows remaining ticks."""
        fac = _make_facility("fac-1", _stabilizer_design("geo_sys", "GeologicStabilizer"),
                             component_states={
                                 "OUTER:0:geo_sys": ComponentActivationState(
                                     phase=ActivationPhase.ACTIVATING,
                                     progress_ticks=50,
                                     required_ticks=250,
                                     ability_name="GeologicStabilizer",
                                 ).to_dict()
                             })
        planet = _make_planet("Akkadia I", 1, facilities=[fac])
        system = _make_system("Akkadia", [planet])

        result = collect_system_effects(system, empire_id=1)

        assert len(result) == 1
        assert result[0]['status'] == "Activating (200)"

    def test_two_facilities_same_ability_both_shown(self):
        """Two GeologicStabilizers from different facilities: both appear as providers."""
        fac1 = _make_facility("fac-1", _stabilizer_design("geo_sector", "GeologicStabilizer"),
                              component_states={
                                  "OUTER:0:geo_sector": ComponentActivationState(
                                      phase=ActivationPhase.ACTIVE,
                                      ability_name="GeologicStabilizer",
                                  ).to_dict()
                              })
        fac2 = _make_facility("fac-2", _stabilizer_design("geo_system", "GeologicStabilizer"),
                              component_states={
                                  "OUTER:0:geo_system": ComponentActivationState(
                                      phase=ActivationPhase.INACTIVE,
                                      ability_name="GeologicStabilizer",
                                  ).to_dict()
                              })
        planet = _make_planet("Akkadia I", 1, facilities=[fac1, fac2])
        system = _make_system("Akkadia", [planet])

        result = collect_system_effects(system, empire_id=1)

        assert len(result) == 1  # Grouped into one effect
        assert result[0]['ability_name'] == "GeologicStabilizer"
        assert result[0]['status'] == "Active"  # At least one is active
        assert len(result[0]['providers']) == 2

    def test_passive_harvest_booster(self):
        """Passive ResourceHarvestBooster shows with multiplier value."""
        fac = _make_facility("fac-1",
                             _harvest_booster_design("hb_metals", "metals", multiplier=1.3),
                             is_operational=True)
        planet = _make_planet("Akkadia I", 1, facilities=[fac])
        system = _make_system("Akkadia", [planet])

        result = collect_system_effects(system, empire_id=1)

        assert len(result) == 1
        effect = result[0]
        assert effect['ability_name'] == "ResourceHarvestBooster"
        assert effect['resource_type'] == "metals"
        assert effect['status'] == "Active"
        assert effect['aggregate_value'] == pytest.approx(1.3)

    def test_two_harvest_boosters_same_stack_group_max(self):
        """Two boosters in same stack_group: aggregate uses MAX (1.3, not 1.69)."""
        fac1 = _make_facility("fac-1", _harvest_booster_design("hb1", "metals", 1.3))
        fac2 = _make_facility("fac-2", _harvest_booster_design("hb2", "metals", 1.3))
        p1 = _make_planet("Akkadia I", 1, facilities=[fac1])
        p2 = _make_planet("Akkadia II", 2, facilities=[fac2])
        system = _make_system("Akkadia", [p1, p2])

        result = collect_system_effects(system, empire_id=1)

        metals_effect = [e for e in result if e.get('resource_type') == 'metals']
        assert len(metals_effect) == 1
        assert metals_effect[0]['aggregate_value'] == pytest.approx(1.3)
        assert len(metals_effect[0]['providers']) == 2

    def test_multiple_ability_types(self):
        """System with stabilizer + harvest booster: both appear as separate effects."""
        fac1 = _make_facility("fac-1", _stabilizer_design("stellar", "StellarStabilizer"),
                              component_states={
                                  "OUTER:0:stellar": ComponentActivationState(
                                      phase=ActivationPhase.ACTIVE,
                                      ability_name="StellarStabilizer",
                                  ).to_dict()
                              })
        fac2 = _make_facility("fac-2", _harvest_booster_design("hb_metals", "metals", 1.3))
        planet = _make_planet("Akkadia I", 1, facilities=[fac1, fac2])
        system = _make_system("Akkadia", [planet])

        result = collect_system_effects(system, empire_id=1)

        ability_names = {e['ability_name'] for e in result}
        assert "StellarStabilizer" in ability_names
        assert "ResourceHarvestBooster" in ability_names

    def test_non_operational_facility_excluded(self):
        """Non-operational facility's abilities are not collected."""
        fac = _make_facility("fac-1", _stabilizer_design("geo", "GeologicStabilizer"),
                             is_operational=False)
        planet = _make_planet("Akkadia I", 1, facilities=[fac])
        system = _make_system("Akkadia", [planet])

        result = collect_system_effects(system, empire_id=1)
        assert result == []

    def test_planet_scope_ability_excluded(self):
        """Abilities with scope='planet' are NOT included in system effects."""
        design = {
            "layers": {
                "OUTER": [{
                    "id": "geo_local",
                    "abilities": {
                        "GeologicStabilizer": {
                            "scope": "planet",
                            "energy_drain_rate": 25.0,
                            "activation_time": 50,
                            "deactivation_time": 10,
                        }
                    }
                }]
            }
        }
        fac = _make_facility("fac-1", design)
        planet = _make_planet("Akkadia I", 1, facilities=[fac])
        system = _make_system("Akkadia", [planet])

        result = collect_system_effects(system, empire_id=1)
        assert result == []

    def test_sector_scope_excluded_from_system_effects(self):
        """Sector-scoped abilities should NOT appear in system effects."""
        design = {
            "layers": {
                "OUTER": [{
                    "id": "shield_sup_sector",
                    "abilities": {
                        "ShieldModifier": {
                            "multiplier": 0.50,
                            "scope": "enemy_sector",
                            "stack_group": "shield_suppressor_sector",
                            "energy_drain_rate": 30.0,
                            "activation_time": 15,
                            "deactivation_time": 5,
                        }
                    }
                }]
            }
        }
        fac = _make_facility("fac-1", design)
        planet = _make_planet("Test I", 1, facilities=[fac])
        system = _make_system("Test", [planet])

        result = collect_system_effects(system, empire_id=1)
        assert result == []

    def test_allied_sector_scope_excluded_from_system_effects(self):
        """allied_sector scope should NOT appear in system effects."""
        design = {
            "layers": {
                "OUTER": [{
                    "id": "shield_boost_sector",
                    "abilities": {
                        "ShieldModifier": {
                            "multiplier": 1.50,
                            "scope": "allied_sector",
                            "stack_group": "shield_booster_sector",
                            "energy_drain_rate": 30.0,
                            "activation_time": 15,
                            "deactivation_time": 5,
                        }
                    }
                }]
            }
        }
        fac = _make_facility("fac-1", design)
        planet = _make_planet("Test I", 1, facilities=[fac])
        system = _make_system("Test", [planet])

        result = collect_system_effects(system, empire_id=1)
        assert result == []


class TestCollectSectorEffects:
    """Tests for collect_sector_effects."""

    def test_sector_scope_included(self):
        """Sector-scoped abilities should appear in sector effects."""
        from game.strategy.services.system_effects_collector import collect_sector_effects

        design = {
            "layers": {
                "OUTER": [{
                    "id": "shield_sup_sector",
                    "abilities": {
                        "ShieldModifier": {
                            "multiplier": 0.50,
                            "scope": "enemy_sector",
                            "stack_group": "shield_suppressor_sector",
                            "energy_drain_rate": 30.0,
                            "activation_time": 15,
                            "deactivation_time": 5,
                        }
                    }
                }]
            }
        }
        fac = _make_facility("fac-1", design)
        planet = _make_planet("Test I", 1, facilities=[fac])
        planet.location = MagicMock()
        system = _make_system("Test", [planet])

        hex_coord = MagicMock()
        system.global_location = MagicMock()
        system.global_location.__add__ = lambda self, other: hex_coord
        hex_coord.__eq__ = lambda self, other: True
        hex_coord.__hash__ = lambda self: 0

        result = collect_sector_effects(system, hex_coord, empire_id=1)
        assert len(result) == 1
        assert result[0]['ability_name'] == 'ShieldModifier'

    def test_system_scope_excluded_from_sector_effects(self):
        """System-scoped abilities should NOT appear in sector effects."""
        from game.strategy.services.system_effects_collector import collect_sector_effects

        fac = _make_facility("fac-1", _stabilizer_design("geo_sys", "GeologicStabilizer", scope="system"))
        planet = _make_planet("Test I", 1, facilities=[fac])
        planet.location = MagicMock()
        system = _make_system("Test", [planet])

        hex_coord = MagicMock()
        system.global_location = MagicMock()
        system.global_location.__add__ = lambda self, other: hex_coord
        hex_coord.__eq__ = lambda self, other: True
        hex_coord.__hash__ = lambda self: 0

        result = collect_sector_effects(system, hex_coord, empire_id=1)
        assert result == []


# ---------------------------------------------------------------------------
# PROJ-300 Phase 4 — kind discriminator, damage_type grouping, helpers,
# storm-source integration.
# ---------------------------------------------------------------------------


class TestKindDiscriminator:
    """PROJ-300: each effect carries a `kind` field disambiguating aggregate."""

    def test_multiplier_ability_kind(self):
        from game.strategy.services.system_effects_collector import collect_system_effects

        fac = _make_facility("f-1", _stabilizer_design("geo", "GeologicStabilizer"),
                             component_states={"OUTER:0:geo": ComponentActivationState(
                                 phase=ActivationPhase.ACTIVE,
                                 ability_name="GeologicStabilizer",
                                 energy_drain_rate=50.0,
                             ).to_dict()})
        planet = _make_planet("P", 1, facilities=[fac])
        system = _make_system("S", [planet])

        result = collect_system_effects(system, empire_id=1)
        assert result and result[0]['kind'] == 'multiplier'

    def test_rate_ability_kind_via_storm(self):
        """Storm-projected EnvironmentalDamage flows through with kind=rate."""
        from game.core.hex_math import HexCoord
        from game.strategy.data.storm import Storm, StormEffect
        from game.strategy.services.system_effects_collector import collect_sector_effects

        storm = Storm(
            name="Plasma Storm",
            storm_type="plasma_storm",
            location=HexCoord(0, 0),
            hex_offsets=frozenset({HexCoord(0, 0)}),
            effects=StormEffect(damage_per_tick=0.005),
        )
        system = _make_system("S", [])
        system.storms = [storm]
        system.global_location = HexCoord(0, 0)

        result = collect_sector_effects(system, HexCoord(0, 0), empire_id=1)
        env_damage = [e for e in result if e['ability_name'] == 'EnvironmentalDamage']
        assert env_damage
        assert env_damage[0]['kind'] == 'rate'
        assert env_damage[0]['aggregate_value'] == pytest.approx(0.5)
        assert env_damage[0]['damage_type'] == 'environmental'


class TestDamageTypeGrouping:
    """PROJ-300: EnvironmentalDamage groups per damage_type."""

    def test_plasma_and_radiation_are_separate_groups(self):
        """Two different damage_types yield two effect rows that SUM."""
        from game.core.hex_math import HexCoord
        from game.strategy.data.storm import Storm, StormEffect
        from game.strategy.services.system_effects_collector import collect_sector_effects

        # We can't get distinct damage_types from the legacy StormEffect path
        # since it only emits one default damage_type. So construct storms with
        # the new abilities-dict shape directly (Phase 5 readiness).
        from dataclasses import dataclass, field
        from typing import Any, FrozenSet

        @dataclass
        class _StormWithAbilities:
            name: str
            abilities: dict
            occupied_hexes: FrozenSet = frozenset({HexCoord(0, 0)})

        plasma = _StormWithAbilities(
            name="Plasma Alpha",
            abilities={"EnvironmentalDamage": {"rate": 0.5, "damage_type": "plasma", "scope": "sector"}},
        )
        radiation = _StormWithAbilities(
            name="Radiation Belt",
            abilities={"EnvironmentalDamage": {"rate": 0.8, "damage_type": "radiation", "scope": "sector"}},
        )
        system = _make_system("S", [])
        system.storms = [plasma, radiation]
        system.global_location = HexCoord(0, 0)

        result = collect_sector_effects(system, HexCoord(0, 0), empire_id=1)
        env = [e for e in result if e['ability_name'] == 'EnvironmentalDamage']
        # Two groups (plasma + radiation), aggregate values per-group.
        damage_types = sorted(e['damage_type'] for e in env)
        assert damage_types == ['plasma', 'radiation']
        plasma_row = next(e for e in env if e['damage_type'] == 'plasma')
        radiation_row = next(e for e in env if e['damage_type'] == 'radiation')
        assert plasma_row['aggregate_value'] == pytest.approx(0.5)
        assert radiation_row['aggregate_value'] == pytest.approx(0.8)


class TestHelpers:
    """find_sector_effect + aggregate_value_or."""

    def test_find_sector_effect_by_ability_name(self):
        from game.strategy.services.system_effects_collector import find_sector_effect
        effects = [
            {'ability_name': 'ShieldModifier', 'aggregate_value': 0.5},
            {'ability_name': 'ThrustModifier', 'aggregate_value': 0.7},
        ]
        e = find_sector_effect(effects, 'ThrustModifier')
        assert e and e['aggregate_value'] == 0.7

    def test_find_sector_effect_returns_none_when_absent(self):
        from game.strategy.services.system_effects_collector import find_sector_effect
        assert find_sector_effect([], 'ShieldModifier') is None

    def test_find_sector_effect_with_filter(self):
        from game.strategy.services.system_effects_collector import find_sector_effect
        effects = [
            {'ability_name': 'EnvironmentalDamage', 'damage_type': 'plasma', 'aggregate_value': 0.5},
            {'ability_name': 'EnvironmentalDamage', 'damage_type': 'radiation', 'aggregate_value': 0.8},
        ]
        e = find_sector_effect(effects, 'EnvironmentalDamage', damage_type='radiation')
        assert e['aggregate_value'] == 0.8

    def test_aggregate_value_or_returns_value(self):
        from game.strategy.services.system_effects_collector import aggregate_value_or
        effects = [{'ability_name': 'X', 'aggregate_value': 1.5}]
        assert aggregate_value_or(effects, 'X', 99.9) == 1.5

    def test_aggregate_value_or_returns_default_when_absent(self):
        from game.strategy.services.system_effects_collector import aggregate_value_or
        assert aggregate_value_or([], 'X', 1.0) == 1.0


class TestProviderUniversalFields:
    """PROJ-300: every provider carries source_kind/source_label/source_id/owner_id."""

    def test_facility_provider_has_universal_fields(self):
        from game.strategy.services.system_effects_collector import collect_system_effects

        fac = _make_facility("f-1", _stabilizer_design("geo", "GeologicStabilizer"),
                             component_states={"OUTER:0:geo": ComponentActivationState(
                                 phase=ActivationPhase.ACTIVE,
                                 ability_name="GeologicStabilizer",
                                 energy_drain_rate=50.0,
                             ).to_dict()})
        planet = _make_planet("Tarsis IV", 1, facilities=[fac])
        system = _make_system("S", [planet])

        result = collect_system_effects(system, empire_id=1)
        provider = result[0]['providers'][0]
        assert provider['source_kind'] == 'facility'
        assert 'Facility-f-1' in provider['source_label']
        assert provider['source_id'].startswith('facility:')
        assert provider['owner_id'] == 1
        # Legacy fields still present for back-compat.
        assert provider['planet_name'] == 'Tarsis IV'
        assert provider['facility_name'] == 'Facility-f-1'

    def test_storm_provider_has_universal_fields(self):
        from game.core.hex_math import HexCoord
        from game.strategy.data.storm import Storm, StormEffect
        from game.strategy.services.system_effects_collector import collect_sector_effects

        storm = Storm(
            name="Ion Storm Alpha",
            storm_type="ion_storm",
            location=HexCoord(0, 0),
            hex_offsets=frozenset({HexCoord(0, 0)}),
            effects=StormEffect(shield_capacity_mult=0.5),
        )
        system = _make_system("S", [])
        system.storms = [storm]
        system.global_location = HexCoord(0, 0)

        result = collect_sector_effects(system, HexCoord(0, 0), empire_id=1)
        assert result
        provider = result[0]['providers'][0]
        assert provider['source_kind'] == 'storm'
        assert provider['source_label'] == 'Ion Storm Alpha'
        assert provider['source_id'] == 'storm:Ion Storm Alpha'
        assert provider['owner_id'] is None  # Storms are ownerless.
