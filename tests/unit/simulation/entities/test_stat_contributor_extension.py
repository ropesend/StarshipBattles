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

import math
from unittest.mock import MagicMock

import pytest

from game.core.constants import LayerType
from game.core.json_utils import load_json
from game.core.paths import Paths
from game.simulation.entities.ship import Ship
from game.simulation.entities.stat_contributors.registry import (
    RegistrationConflictPolicy,
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

    PROJ-367 Phase 2: ``add_stat`` now uses the handle-based API and the
    default policy ``REPLACE_SILENT`` (built-in defaults are seeded for
    every ability and we don't want every test to log a deprecation
    warning). Domain tag dropped — ``RegistrationConflictPolicy`` covers
    every legacy use case the ``domain`` field once papered over.
    """
    added_crew_abilities: list[str] = []
    stat_handles: list = []

    def add_crew(name: str, priority: int) -> None:
        register_crew_priority(name, priority)
        added_crew_abilities.append(name)

    def add_stat(name: str, fn, *, policy=RegistrationConflictPolicy.REPLACE_SILENT) -> None:
        h = register_stat_contributor(name, fn, policy=policy)
        stat_handles.append(h)

    yield add_crew, add_stat

    for name in added_crew_abilities:
        unregister_crew_priority(name)
    for h in stat_handles:
        try:
            unregister_stat_contributor(h)
        except Exception:  # Intentional broad catch: cleanup best-effort across test failures
            pass


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

        def fake_contributor(ship, comp, acc):
            # Stamp a list onto the ship to prove invocation order.
            if not hasattr(ship, "fake_contributor_calls"):
                ship.fake_contributor_calls = []
            ship.fake_contributor_calls.append(comp)
            invocations.append(comp)

        # PROJ-367 Phase 2: this fake contributor REPLACES the
        # built-in defense handling for ShieldProjection — implicit via
        # ``RegistrationConflictPolicy.REPLACE_SILENT`` (default for the
        # ``add_stat`` test fixture).
        add_stat("ShieldProjection", fake_contributor)

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

    def test_registering_shield_projection_does_not_double_count(
        self, fresh_registries, clean_extension_registry
    ):
        """PROJ-360 audit EXT-01 + EXT-02 critical regression test.

        Registering a contributor for ``ShieldProjection`` (an ability the
        built-in ``defense.aggregate_defense`` already handles) MUST NOT
        cause ``ship.max_shields`` to be double-counted. The audit found
        that the prior implementation invoked both the built-in handler
        and the registered contributor, silently double-applying capacity.

        The fix: a registered contributor on a built-in ability suppresses
        the built-in. So ``max_shields`` after registration is determined
        purely by the registered contributor (here: a 7x multiplier on
        each shield's capacity, deliberately picked to be unmistakable).

        The two halves of the assertion:

        - The registered contributor DID run (proves the hook fires).
        - ``max_shields`` equals contributor-only output, not
          contributor+built-in. If the built-in were also firing,
          ``max_shields`` would include the baseline 1x sum on top of
          our 7x.
        """
        _, add_stat = clean_extension_registry

        # First pass: baseline `max_shields` from the built-in defense
        # handler alone (no registered contributor).
        design = load_json(
            str(Paths.get_starter_designs_dir() / "qs_battleship.json")
        )
        baseline_ship = Ship.from_dict(design, registries=fresh_registries)
        baseline_ship.recalculate_stats()
        baseline_max_shields = baseline_ship.max_shields
        assert baseline_max_shields > 0, (
            "Pre-condition failed: qs_battleship has no shield capacity. "
            "The audit regression test depends on the battleship carrying "
            "shields — fixture drift."
        )

        # Second pass: register a ShieldProjection contributor that adds
        # 7x the natural capacity. With the EXT-02 fix the built-in is
        # suppressed and only this contributor runs.
        invocations: list = []

        def replacing_contributor(ship, comp, acc):
            for ab in comp.get_abilities("ShieldProjection"):
                acc["max_shields"] += ab.capacity * 7
                invocations.append(ab.capacity)

        add_stat("ShieldProjection", replacing_contributor)

        replaced_ship = Ship.from_dict(design, registries=fresh_registries)
        replaced_ship.recalculate_stats()

        # 1. The registered contributor MUST have fired.
        assert invocations, (
            "Registered ShieldProjection contributor was not invoked — "
            "the registry hook regressed."
        )

        # 2. baseline_max_shields = 1x sum of capacities (built-in only).
        #    With suppression, replaced ship sees 7x sum, NOT 1x + 7x = 8x.
        expected_replaced = baseline_max_shields * 7
        assert math.isclose(
            replaced_ship.max_shields, expected_replaced, rel_tol=1e-9
        ), (
            f"EXT-01/EXT-02 regression: max_shields={replaced_ship.max_shields}, "
            f"expected 7x baseline ({expected_replaced}) but got "
            f"{replaced_ship.max_shields}. If this is 8x baseline "
            f"({baseline_max_shields * 8}), the built-in is firing alongside "
            f"the registered contributor — double-counting bug."
        )

    def test_registered_contributor_receives_acc_dict(
        self, fresh_registries, clean_extension_registry
    ):
        """PROJ-360 audit EXT-12: registered contributors receive the
        accumulator dict, identical to built-in contributors.

        We register a non-builtin ability and assert the contributor sees
        the in-progress ``acc`` dict (verified by reading a built-in
        accumulator key like ``thrust`` that other contributors have
        already written to).
        """
        _, add_stat = clean_extension_registry

        seen_acc_types: list = []

        def acc_inspecting_contributor(ship, comp, acc):
            # The acc dict is a real `dict`; built-in contributors have
            # already written to it by the time we run.
            seen_acc_types.append(type(acc))
            assert isinstance(acc, dict), (
                f"Registered contributor expected acc=dict, got {type(acc)}"
            )
            # Built-in keys must exist (initialized at phase start).
            assert "thrust" in acc and "max_shields" in acc, (
                f"acc dict missing built-in keys; got keys={list(acc.keys())}"
            )

        add_stat("ShieldProjection", acc_inspecting_contributor)

        design = load_json(
            str(Paths.get_starter_designs_dir() / "qs_battleship.json")
        )
        ship = Ship.from_dict(design, registries=fresh_registries)
        ship.recalculate_stats()

        assert seen_acc_types, (
            "EXT-12 regression: acc-inspecting contributor never ran."
        )
        assert all(t is dict for t in seen_acc_types), (
            f"EXT-12: contributor saw non-dict acc on at least one call: "
            f"{seen_acc_types}"
        )

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

        def counting_contributor(ship, comp, acc):
            invocation_counts.append(comp)

        add_stat("ShieldProjection", counting_contributor)

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
