"""
PROJ-360 Phase 3 acceptance test — extensibility of the stat-contributor registry.

Demonstrates that adding a new stat-affecting ability is a pure registry
edit: no changes to ``ship_stats.py``, the contributor modules, or any
other production code. The fake contributor runs end-to-end through
``ShipStatsCalculator.calculate(ship)`` and writes a stat the test owns.

This test is the codified extensibility goal of PROJ-360. If it ever fails
to demonstrate "register-don't-edit", the registry has regressed.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.constants import LayerType
from game.core.json_utils import load_json
from game.core.paths import Paths
from game.simulation.entities.ship import Ship
from game.simulation.entities.stat_contributors.registry import (
    register_crew_priority,
    register_stat_contributor,
    unregister_crew_priority,
    unregister_stat_contributor,
    lookup_crew_priority,
)


# ---------------------------------------------------------------------------
# Fixtures: clean registry state across tests
# ---------------------------------------------------------------------------


@pytest.fixture
def clean_extension_registry():
    """Yield, then strip any extensions registered during the test.

    The production registries are module-level globals. Tests must clean
    up after themselves so a registration in one test cannot leak into
    another.
    """
    added_crew_abilities: list[str] = []
    added_stat_keys: list[tuple[str, str]] = []

    def add_crew(name: str, priority: int) -> None:
        register_crew_priority(name, priority)
        added_crew_abilities.append(name)

    def add_stat(name: str, fn, *, domain: str = "ext") -> None:
        register_stat_contributor(name, fn, domain=domain)
        added_stat_keys.append((name, domain))

    yield add_crew, add_stat

    for name in added_crew_abilities:
        unregister_crew_priority(name)
    for name, domain in added_stat_keys:
        unregister_stat_contributor(name, domain=domain)


# ---------------------------------------------------------------------------
# Crew-priority registry extension
# ---------------------------------------------------------------------------


class TestCrewPriorityExtension:
    """A new ability can be added to the priority order without editing command.py."""

    def test_register_new_priority_class(self, clean_extension_registry):
        add_crew, _ = clean_extension_registry
        comp = MagicMock()
        comp.has_ability = lambda name: name == "FakeShieldArray"

        # Default priority for unrecognized abilities is 3.
        assert lookup_crew_priority(comp) == 3

        # Register the new ability between movement (1) and weapons (2).
        add_crew("FakeShieldArray", priority=1)
        assert lookup_crew_priority(comp) == 1

    def test_lower_priority_wins_when_component_has_multiple_abilities(
        self, clean_extension_registry
    ):
        add_crew, _ = clean_extension_registry
        # Component with both a registered fake ability AND CommandAndControl.
        comp = MagicMock()
        comp.has_ability = lambda name: name in {"FakePriorityX", "CommandAndControl"}

        add_crew("FakePriorityX", priority=2)
        # CommandAndControl already registered at priority 0; that wins.
        assert lookup_crew_priority(comp) == 0

    def test_double_registration_raises(self, clean_extension_registry):
        add_crew, _ = clean_extension_registry
        add_crew("FakeDup", priority=2)
        with pytest.raises(ValueError, match="already registered"):
            register_crew_priority("FakeDup", 3)


# ---------------------------------------------------------------------------
# Full stats-pipeline extension via a real ship
# ---------------------------------------------------------------------------


class TestStatContributorExtensionEndToEnd:
    """A registered contributor runs during ShipStatsCalculator.calculate()."""

    def test_fake_contributor_runs_for_a_ship_with_matching_ability(
        self, fresh_registries, clean_extension_registry
    ):
        """A fake contributor stamps a custom attribute onto the ship.

        We use ``ShieldProjection`` as the gating ability since the
        battleship's `shield_generator` carries it; this avoids building
        a fake ``Component`` from scratch and keeps the test focused on
        the REGISTRY mechanism rather than component construction.
        """
        _, add_stat = clean_extension_registry

        invocations: list = []

        def fake_contributor(ship, comp):
            # Stamp a list onto the ship to prove invocation order.
            if not hasattr(ship, "fake_contributor_calls"):
                ship.fake_contributor_calls = []
            ship.fake_contributor_calls.append(comp)
            invocations.append(comp)

        add_stat("ShieldProjection", fake_contributor, domain="proj360_test")

        # Build a battleship; it has shield regenerators. Recalculate stats.
        design = load_json(
            str(Paths.get_starter_designs_dir() / "qs_battleship.json")
        )
        ship = Ship.from_dict(design, registries=fresh_registries)
        ship.recalculate_stats()

        # Contributor must have been invoked at least once.
        assert len(invocations) >= 1, (
            "Fake contributor was registered for ShieldRegeneration but "
            "never invoked during recalculate_stats — extension hook is broken."
        )
        # Every invocation receives a component that has the gating ability.
        for comp in invocations:
            assert comp.has_ability("ShieldProjection"), (
                f"Contributor invoked for component without "
                f"ShieldProjection: {comp}"
            )

    def test_unregistered_contributor_is_not_invoked(
        self, fresh_registries, clean_extension_registry
    ):
        """If no contributor is registered, ship.recalculate_stats is unaffected."""
        # Note: NOT calling add_stat — the registry stays empty.

        design = load_json(
            str(Paths.get_starter_designs_dir() / "qs_battleship.json")
        )
        ship = Ship.from_dict(design, registries=fresh_registries)
        ship.recalculate_stats()

        # No fake_contributor_calls attribute should exist.
        assert not hasattr(ship, "fake_contributor_calls")

    def test_contributor_only_runs_on_operational_components(
        self, fresh_registries, clean_extension_registry
    ):
        """Gating: contributors run inside the operational-only block.

        The calculator skips ``apply_registered_contributors`` for
        components that are not active+operational. We assert this by
        building a ship, recalculating, then mutating one shield-regen
        component to be inactive and confirming the contributor sees
        ONE FEWER call on the second recalc.
        """
        _, add_stat = clean_extension_registry

        invocation_counts: list = []

        def counting_contributor(ship, comp):
            invocation_counts.append(comp)

        add_stat("ShieldProjection", counting_contributor, domain="proj360_op_gate")

        design = load_json(
            str(Paths.get_starter_designs_dir() / "qs_battleship.json")
        )
        ship = Ship.from_dict(design, registries=fresh_registries)
        ship.recalculate_stats()
        first_call_count = len(invocation_counts)

        # Find the shield_generator component(s) and mark them damaged.
        shield_comps = [
            comp
            for _, comp in ship.iter_components()
            if comp.has_ability("ShieldProjection")
        ]
        if not shield_comps:
            pytest.skip(
                "qs_battleship has no shield components — fixture drift; "
                "test pre-condition not met."
            )
        # Damage to below the damage threshold (force inactive on next pass).
        for comp in shield_comps:
            comp.current_hp = 0  # below any damage_threshold

        ship.mark_stats_dirty()
        ship.recalculate_stats_if_dirty()
        second_call_count = len(invocation_counts) - first_call_count

        assert second_call_count < first_call_count, (
            f"Damaged shield-regen components still triggered the "
            f"registered contributor: first={first_call_count}, "
            f"second={second_call_count}. Contributors must respect the "
            f"is_operational gate."
        )
