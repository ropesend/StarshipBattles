"""
Integration tests for design loading + warp capability.

These tests guard against a bug where formula-driven ability attributes
(WarpJump.max_tonnage, EmissiveArmor, ShieldRegeneratingArmor) ended up
frozen at a default fallback value (1000) instead of the value derived
from the ship class's max_mass.

Root cause was twofold:
  1. _load_components called add_modifier (which triggers recalculate_stats)
     BEFORE the component was attached to the ship. With comp.ship == None,
     formula evaluation fell back to ship_class_mass=1000, instantiating
     ability instances with the wrong numeric attributes.
  2. Ability.sync_data only refreshed self.data, never re-reading numeric
     attributes from the new (correct) data, leaving the instance frozen
     at the initial wrong value.

These tests load a real Frigate design (max_mass=2000) and assert that
the resulting ship has correct warp_max_tonnage, can warp under its own
mass, and that the WarpJump ability instance reflects the correct value.
"""
import json
import pytest

from game.core.registry import GameRegistries
from game.simulation.components.component import load_components_data, load_modifiers_data
from game.simulation.entities.ship_loader import load_vehicle_classes_data
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_design_stats import calculate_design_stats
from game.strategy.services.component_abilities import has_warp_capability


@pytest.fixture
def real_registries():
    """GameRegistries with real loaded data from data/."""
    minimal = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
    return GameRegistries(
        components=load_components_data(registries=minimal),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={},
    )


@pytest.fixture
def frigate_design():
    """Load the canonical qs_frigate_gc design from disk."""
    with open('data/designs/qs_frigate_gc.json') as f:
        return json.load(f)


class TestFrigateWarpCapability:
    """Frigate (max_mass=2000) must have functional warp capability."""

    def test_frigate_class_max_mass_is_2000(self, real_registries):
        """Sanity: Frigate class is registered with max_mass=2000."""
        frigate = real_registries.vehicle_classes.get('Frigate')
        assert frigate is not None
        assert frigate.get('max_mass') == 2000

    def test_frigate_warp_max_tonnage_equals_class_max_mass(self, real_registries, frigate_design):
        """warp_drive's max_tonnage formula =ship_class_mass must yield 2000."""
        stats = calculate_design_stats(frigate_design, real_registries)
        assert stats['warp_max_tonnage'] == 2000, (
            f"Expected warp_max_tonnage=2000 (Frigate.max_mass), "
            f"got {stats['warp_max_tonnage']}. The ship_class_mass formula "
            f"context likely fell back to the default 1000."
        )

    def test_frigate_can_warp_under_own_mass(self, real_registries, frigate_design):
        """The Frigate's mass (~1570) must be <= its warp_max_tonnage (2000)."""
        stats = calculate_design_stats(frigate_design, real_registries)
        assert stats['warp_max_tonnage'] >= stats['mass'], (
            f"Frigate cannot warp itself: mass={stats['mass']} > "
            f"warp_max_tonnage={stats['warp_max_tonnage']}"
        )

    def test_frigate_ship_instance_has_warp(self, real_registries, frigate_design):
        """A loaded Ship instance must report warp capability via the ability instance."""
        ship = Ship.from_dict(frigate_design, registries=real_registries)
        assert ship.warp_max_tonnage == 2000, (
            f"Ship.warp_max_tonnage={ship.warp_max_tonnage}, expected 2000. "
            f"The WarpJump ability instance was likely constructed with the "
            f"fallback value before comp.ship was set, and sync_data did not "
            f"refresh max_tonnage."
        )
        assert ship.warp_max_tonnage >= ship.mass

    def test_warp_jump_instance_reflects_correct_max_tonnage(self, real_registries, frigate_design):
        """The WarpJump ability instance on the warp_drive component must have max_tonnage=2000."""
        ship = Ship.from_dict(frigate_design, registries=real_registries)
        warp_drive = None
        for _layer, comp in ship.iter_components():
            if comp.id == 'warp_drive':
                warp_drive = comp
                break
        assert warp_drive is not None, "warp_drive component not on Frigate"

        warp_jumps = warp_drive.get_abilities('WarpJump')
        assert warp_jumps, "warp_drive has no WarpJump ability instances"
        assert warp_jumps[0].max_tonnage == 2000, (
            f"WarpJump.max_tonnage={warp_jumps[0].max_tonnage}, expected 2000. "
            f"sync_data is failing to refresh formula-derived attributes."
        )

    def test_strategy_layer_reports_warp_capable(self, real_registries, frigate_design):
        """has_warp_capability() in the strategy layer must return True for the Frigate."""
        from game.strategy.data.ship_instance import ShipInstance

        instance = ShipInstance.create(
            design_data=frigate_design,
            owner_id=0,
            registries=real_registries,
        )
        assert has_warp_capability(instance) is True, (
            "Strategy-layer has_warp_capability() reports the Frigate cannot warp"
        )


class TestFrigateCrewRequiredFormulaIsEvaluated:
    """The bridge component's CrewRequired formula must evaluate to a per-class
    value on the actual ability instance (not just in the abilities dict).

    Original bug: CrewRequired overrode __init__ to parse data into _base_amount,
    but the base Ability.sync_data was a no-op for numeric attributes. So the
    instance was constructed with the stale data parsed at registry-load time
    (numeric value 0 for an unevaluated formula string), and never refreshed
    when the abilities dict re-evaluated to the correct numeric value.

    Fix: migrate CrewRequired to use the _parse_attrs template method, which
    the base Ability class wires into both __init__ and sync_data.

    Coupled change: the bridge formula was tuned from
    `=ceil(5 * sqrt(ship_class_mass / 1000))` down to
    `=ceil(sqrt(ship_class_mass / 1000))` to keep production designs balanced
    after CrewRequired starts demanding crew correctly.
    """

    def test_frigate_bridge_crew_required_matches_tuned_formula(self, real_registries, frigate_design):
        """Bridge on Frigate (max_mass=2000) → ceil(sqrt(2)) = 2 crew."""
        ship = Ship.from_dict(frigate_design, registries=real_registries)
        bridge = next((c for _, c in ship.iter_components() if c.id == 'bridge'), None)
        assert bridge is not None

        crew_reqs = bridge.get_abilities('RequiresMaintenance')
        assert crew_reqs, "bridge has no RequiresMaintenance ability instance"
        # ceil(sqrt(2000/1000)) = ceil(1.414) = 2
        assert crew_reqs[0]._base_amount == 2, (
            f"RequiresMaintenance._base_amount={crew_reqs[0]._base_amount}, expected 2 "
            f"from =ceil(sqrt(ship_class_mass / 1000)) with ship_class_mass=2000. "
            f"Either the formula in components.json is wrong, or RequiresMaintenance's "
            f"sync_data is not refreshing formula-derived attributes."
        )


class TestSyncDataRefreshesFormulaAttributes:
    """Direct test for the sync_data staleness bug.

    Reproduces the in-process scenario: a component is recalculated once
    with no ship (default ship_class_mass), then again with a ship whose
    max_mass_budget differs. The ability instance must reflect the latest
    value, not stay frozen at the first.
    """

    def test_warp_jump_sync_data_updates_max_tonnage(self, real_registries):
        """Calling recalculate_stats with a different ship context must update WarpJump.max_tonnage."""
        warp_drive = real_registries.components['warp_drive'].clone()

        # First recalc: explicit context with ship_class_mass=1000 (Escort-equivalent)
        warp_drive.ship = None
        warp_drive.recalculate_stats({'ship_class_mass': 1000})
        first_warp = warp_drive.get_abilities('WarpJump')
        assert first_warp, "WarpJump should instantiate when context is provided"
        assert first_warp[0].max_tonnage == 1000

        # Second recalc: ship with max_mass_budget=2000 → instance must refresh
        class FakeShip:
            max_mass_budget = 2000
        warp_drive.ship = FakeShip()
        warp_drive.recalculate_stats()
        second_warp = warp_drive.get_abilities('WarpJump')
        assert second_warp[0].max_tonnage == 2000, (
            f"WarpJump.max_tonnage stayed at {second_warp[0].max_tonnage} "
            f"after recalc with ship_class_mass=2000. "
            f"sync_data is not refreshing numeric attributes from updated data."
        )
