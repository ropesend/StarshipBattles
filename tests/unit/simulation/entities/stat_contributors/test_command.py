"""
Unit tests for the command stat contributor.

Covers ``lookup_crew_priority`` (component priority for crew allocation,
canonical API in ``stat_contributors.registry``),
``track_multiplex`` (max_targets propagation), and the crew/life-support
allocation phase.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.constants import CombatConstants
from game.simulation.components.component_constants import ComponentStatus
from game.simulation.entities.stat_contributors import command
from game.simulation.entities.stat_contributors.registry import (
    lookup_crew_priority,
)


def _make_comp_with_abilities(*has_ability_names: str):
    """Component whose ``has_ability`` returns True for the listed names."""
    comp = MagicMock()
    names = set(has_ability_names)
    comp.has_ability = lambda name: name in names
    return comp


class TestLookupCrewPriority:
    def test_command_is_top_priority(self):
        bridge = _make_comp_with_abilities("CommandAndControl")
        assert lookup_crew_priority(bridge) == 0

    def test_engines_outrank_weapons(self):
        engine = _make_comp_with_abilities("CombatPropulsion")
        thruster = _make_comp_with_abilities("ManeuveringThruster")
        assert lookup_crew_priority(engine) == 1
        assert lookup_crew_priority(thruster) == 1

    def test_weapons_above_other_systems(self):
        weapon = _make_comp_with_abilities("WeaponAbility")
        other = _make_comp_with_abilities()
        assert lookup_crew_priority(weapon) == 2
        assert lookup_crew_priority(other) == 3

    def test_command_wins_when_component_has_multiple_priorities(self):
        """A bridge that ALSO has weapons should still sort to bridge priority."""
        hybrid = _make_comp_with_abilities("CommandAndControl", "WeaponAbility")
        assert lookup_crew_priority(hybrid) == 0


class TestTrackMultiplex:
    """PROJ-367 Phase 1 (closes EXT-07): typed MultiplexTrackingAbility access."""

    @staticmethod
    def _multiplex_comp(slots: int | None):
        """Component whose ``get_abilities("MultiplexTracking")`` returns a list of fakes."""
        comp = MagicMock()
        from types import SimpleNamespace
        if slots is None:
            comp.get_abilities = lambda name: []
        else:
            comp.get_abilities = lambda name: (
                [SimpleNamespace(slots=slots)] if name == "MultiplexTracking" else []
            )
        return comp

    def test_multiplex_zero_or_missing_is_noop(self):
        ship = MagicMock()
        ship.max_targets = 1
        # No ability at all
        command.contribute_multiplex_tracking(ship, self._multiplex_comp(None), {})
        assert ship.max_targets == 1

        # Ability with slots=0
        command.contribute_multiplex_tracking(ship, self._multiplex_comp(0), {})
        assert ship.max_targets == 1

    def test_higher_multiplex_replaces_lower(self):
        ship = MagicMock()
        ship.max_targets = 2
        command.contribute_multiplex_tracking(ship, self._multiplex_comp(5), {})
        assert ship.max_targets == 5

    def test_lower_multiplex_does_not_overwrite_higher(self):
        ship = MagicMock()
        ship.max_targets = 5
        command.contribute_multiplex_tracking(ship, self._multiplex_comp(2), {})
        assert ship.max_targets == 5


def _make_maintenance_required_ability(amount: int):
    ab = MagicMock()
    ab.amount = amount
    return ab


def _make_active_comp(*, maintenance_required: int = 0):
    comp = MagicMock()
    comp.is_active = True
    comp.has_ability = lambda name: False  # ensures lookup_crew_priority returns 3
    comp.get_abilities = lambda name: (
        [_make_maintenance_required_ability(maintenance_required)]
        if name == "RequiresMaintenance" and maintenance_required
        else []
    )
    comp.status = ComponentStatus.ACTIVE
    return comp


class TestAllocateCrewAndLifeSupport:
    def test_zero_demand_passes_through(self):
        ship = MagicMock()
        ship.ship_class = "Frigate"
        pool = [_make_active_comp(maintenance_required=0)]
        command.allocate_crew_and_life_support(
            ship, pool,
            available_crew=0, available_life_support=0, available_maintenance=0,
            vehicle_classes={"Frigate": {"max_mass": 5000}},
        )
        assert ship.crew_onboard == 0
        assert ship.crew_required == 0
        assert ship.max_targets == CombatConstants.DEFAULT_MAX_TARGETS
        assert ship.max_mass_budget == 5000
        assert pool[0].is_active is True

    def test_components_deactivated_when_maintenance_runs_out(self):
        ship = MagicMock()
        ship.ship_class = "Frigate"
        c1 = _make_active_comp(maintenance_required=3)
        c2 = _make_active_comp(maintenance_required=5)  # not enough maintenance
        pool = [c1, c2]
        command.allocate_crew_and_life_support(
            ship, pool,
            available_crew=4, available_life_support=10, available_maintenance=4,
            vehicle_classes={"Frigate": {"max_mass": 5000}},
        )
        assert ship.crew_required == 8  # both demands recorded as maintenance demand
        # First in priority order gets serviced, second is deactivated
        assert c1.is_active is True
        assert c2.is_active is False
        assert c2.status == ComponentStatus.NO_CREW

    def test_life_support_no_longer_silently_clamps(self):
        """QA Observation 5: LS shortage is a design-time validator error,
        not a runtime silent degradation. Runtime ignores life_support
        because the validator guarantees CrewCap <= LSCap.
        """
        ship = MagicMock()
        ship.ship_class = "Frigate"
        c = _make_active_comp(maintenance_required=3)
        pool = [c]
        command.allocate_crew_and_life_support(
            ship, pool,
            available_crew=10, available_life_support=2, available_maintenance=10,
            vehicle_classes={"Frigate": {"max_mass": 5000}},
        )
        # Maintenance was sufficient (10 >= 3); LS shortage does NOT deactivate.
        assert c.is_active is True

    def test_unknown_ship_class_uses_default_mass_budget(self):
        from game.simulation.physics_constants import DEFAULT_MAX_MASS

        ship = MagicMock()
        ship.ship_class = "UnknownClass"
        pool = []
        command.allocate_crew_and_life_support(
            ship, pool,
            available_crew=0, available_life_support=0, available_maintenance=0,
            vehicle_classes={},
        )
        assert ship.max_mass_budget == DEFAULT_MAX_MASS
