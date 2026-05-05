"""
Unit tests for the defense stat contributor.

Targets ``aggregate_defense`` (per-component) plus the post-aggregation
helpers ``apply_armor_and_repair_scores`` and ``init_armor_pool``. Golden
tests pin the integrated semantics; these tests cover edge cases at the
contributor seam.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.constants import LayerType
from game.simulation.entities.stat_contributors import defense


def _make_shield_projection(capacity: float):
    ab = MagicMock()
    ab.capacity = capacity
    return ab


def _make_shield_regeneration(rate: float):
    ab = MagicMock()
    ab.rate = rate
    return ab


def _make_resource_consumption(resource_type: str, amount: float):
    """Duck-typed ResourceConsumption — `is_resource_consumption` checks
    for the four named attrs (`trigger`, `resource_type`, `amount`,
    `check_available`)."""
    ab = MagicMock(spec=["trigger", "resource_type", "amount", "check_available"])
    ab.trigger = "continuous"
    ab.resource_type = resource_type
    ab.amount = amount
    ab.check_available = lambda *_a, **_kw: True
    return ab


def _empty_acc() -> dict:
    return {"max_shields": 0, "shield_regen": 0, "shield_cost": 0}


def _make_ship_with_armor_layer(armor_present: bool = True):
    ship = MagicMock()
    if armor_present:
        armor = MagicMock()
        armor.max_hp_pool = 0
        armor.hp_pool = 0
        ship.layers = {LayerType.ARMOR: armor}
    else:
        ship.layers = {}
    return ship


def _make_component(
    *,
    abilities_dict: dict | None = None,
    abilities_by_name: dict | None = None,
    ability_instances: list | None = None,
    has_ability_set: set | None = None,
    max_hp: float = 100.0,
):
    comp = MagicMock()
    comp.abilities = abilities_dict or {}
    comp.get_abilities = lambda name: (abilities_by_name or {}).get(name, [])
    comp.ability_instances = ability_instances or []
    comp.has_ability = lambda name: name in (has_ability_set or set())
    comp.max_hp = max_hp
    return comp


class TestArmorPoolAggregation:
    def test_armor_component_adds_max_hp_to_pool(self):
        ship = _make_ship_with_armor_layer()
        acc = _empty_acc()
        comp = _make_component(abilities_dict={"Armor": True}, max_hp=250.0)
        defense.aggregate_defense(ship, comp, acc)
        assert ship.layers[LayerType.ARMOR].max_hp_pool == 250.0

    def test_no_armor_layer_does_not_crash(self):
        ship = _make_ship_with_armor_layer(armor_present=False)
        acc = _empty_acc()
        comp = _make_component(abilities_dict={"Armor": True}, max_hp=250.0)
        defense.aggregate_defense(ship, comp, acc)
        # No layers entry — no crash
        assert acc["max_shields"] == 0


class TestShieldAggregation:
    def test_shield_projection_sums_capacity(self):
        ship = _make_ship_with_armor_layer()
        acc = _empty_acc()
        comp = _make_component(
            abilities_by_name={
                "ShieldProjection": [
                    _make_shield_projection(500.0),
                    _make_shield_projection(300.0),
                ]
            }
        )
        defense.aggregate_defense(ship, comp, acc)
        assert acc["max_shields"] == 800.0

    def test_shield_regeneration_sums_rate(self):
        ship = _make_ship_with_armor_layer()
        acc = _empty_acc()
        comp = _make_component(
            abilities_by_name={
                "ShieldRegeneration": [
                    _make_shield_regeneration(2.0),
                    _make_shield_regeneration(1.5),
                ]
            },
            has_ability_set={"ShieldRegeneration"},
            ability_instances=[],
        )
        defense.aggregate_defense(ship, comp, acc)
        assert acc["shield_regen"] == 3.5

    def test_shield_energy_cost_only_counts_once_first_match_wins(self):
        """Legacy behavior: first energy ResourceConsumption breaks the loop.

        PROJ-360 audit EXT-05: defense now uses
        ``get_abilities("ResourceConsumption")`` instead of scanning all
        ``ability_instances``. The "first match wins" semantics is
        preserved — the consumption list is consumed in order and the
        loop breaks on the first energy match.
        """
        ship = _make_ship_with_armor_layer()
        acc = _empty_acc()
        first = _make_resource_consumption("energy", 5.0)
        second = _make_resource_consumption("energy", 7.0)
        comp = _make_component(
            abilities_by_name={"ResourceConsumption": [first, second]},
            has_ability_set={"ShieldRegeneration"},
        )
        defense.aggregate_defense(ship, comp, acc)
        assert acc["shield_cost"] == 5.0  # not 12.0

    def test_shield_energy_cost_skipped_without_shield_regen(self):
        ship = _make_ship_with_armor_layer()
        acc = _empty_acc()
        comp = _make_component(
            abilities_by_name={
                "ResourceConsumption": [_make_resource_consumption("energy", 5.0)],
            },
            has_ability_set=set(),  # no ShieldRegeneration -> skip
        )
        defense.aggregate_defense(ship, comp, acc)
        assert acc["shield_cost"] == 0

    def test_shield_energy_cost_filters_by_resource_type(self):
        """EXT-05: only ResourceConsumption(energy) is summed; fuel etc.
        are skipped even though the gate (ShieldRegeneration) is present."""
        ship = _make_ship_with_armor_layer()
        acc = _empty_acc()
        fuel_cost = _make_resource_consumption("fuel", 9.0)
        energy_cost = _make_resource_consumption("energy", 4.0)
        comp = _make_component(
            abilities_by_name={
                "ResourceConsumption": [fuel_cost, energy_cost],
            },
            has_ability_set={"ShieldRegeneration"},
        )
        defense.aggregate_defense(ship, comp, acc)
        assert acc["shield_cost"] == 4.0


class TestArmorAndRepairPostAggregation:
    def test_emissive_armor_only_counts_active_components(self):
        active = MagicMock()
        active.is_active = True
        inactive = MagicMock()
        inactive.is_active = False

        # Patch get_ability_total so the test exercises the active-pool filter,
        # not the registry contents. We feed a recognizable identity into
        # the aggregator and read back the totals it produces.
        ship = MagicMock()
        from unittest.mock import patch

        with patch(
            "game.simulation.entities.stat_contributors.defense.get_ability_total",
            side_effect=lambda pool, name: (len(pool), name),
        ):
            defense.apply_armor_and_repair_scores(ship, [active, inactive])
        # active pool is filtered to length 1 for armor abilities
        assert ship.emissive_armor == (1, "EmissiveArmor")
        assert ship.shield_regenerating_armor == (1, "ShieldRegeneratingArmor")
        # repair_rate uses the FULL pool (len 2) — destroyed comps still repair? legacy behavior
        assert ship.repair_rate == (2, "ShipRepair")


class TestArmorPoolInit:
    def test_init_fills_empty_pool(self):
        ship = _make_ship_with_armor_layer()
        ship.layers[LayerType.ARMOR].max_hp_pool = 500
        ship.layers[LayerType.ARMOR].hp_pool = 0
        defense.init_armor_pool(ship)
        assert ship.layers[LayerType.ARMOR].hp_pool == 500

    def test_init_does_not_overwrite_damaged_pool(self):
        ship = _make_ship_with_armor_layer()
        ship.layers[LayerType.ARMOR].max_hp_pool = 500
        ship.layers[LayerType.ARMOR].hp_pool = 200  # damaged
        defense.init_armor_pool(ship)
        assert ship.layers[LayerType.ARMOR].hp_pool == 200

    def test_init_skipped_when_no_armor_layer(self):
        ship = _make_ship_with_armor_layer(armor_present=False)
        defense.init_armor_pool(ship)  # must not crash
