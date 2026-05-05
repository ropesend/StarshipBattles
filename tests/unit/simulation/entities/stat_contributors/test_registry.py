"""
Unit tests for the stat contributor registry.

Covers register/unregister round-trips and the priority lookup helper in
isolation; the end-to-end extension test in
``tests/unit/simulation/entities/test_stat_contributor_extension.py`` covers
the full ship pipeline.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.simulation.entities.stat_contributors.registry import (
    CREW_PRIORITY_DEFAULT,
    apply_registered_contributors,
    lookup_crew_priority,
    register_crew_priority,
    register_stat_contributor,
    unregister_crew_priority,
    unregister_stat_contributor,
)


@pytest.fixture
def cleanup():
    """Track and undo any registrations done during the test."""
    crew_added: list[str] = []
    stat_added: list[tuple[str, str]] = []
    yield crew_added, stat_added
    for n in crew_added:
        unregister_crew_priority(n)
    for n, d in stat_added:
        unregister_stat_contributor(n, domain=d)


class TestLookupCrewPriority:
    def test_default_for_unknown_ability(self):
        comp = MagicMock()
        comp.has_ability = lambda _name: False
        assert lookup_crew_priority(comp) == CREW_PRIORITY_DEFAULT

    def test_command_ability_returns_zero(self):
        comp = MagicMock()
        comp.has_ability = lambda name: name == "CommandAndControl"
        assert lookup_crew_priority(comp) == 0


class TestRegisterCrewPriority:
    def test_register_then_lookup(self, cleanup):
        crew_added, _ = cleanup
        comp = MagicMock()
        comp.has_ability = lambda name: name == "FakeUnitTestAbility"

        register_crew_priority("FakeUnitTestAbility", 2)
        crew_added.append("FakeUnitTestAbility")

        assert lookup_crew_priority(comp) == 2

    def test_unregister_returns_to_default(self, cleanup):
        comp = MagicMock()
        comp.has_ability = lambda name: name == "FakeRoundtrip"

        register_crew_priority("FakeRoundtrip", 2)
        assert lookup_crew_priority(comp) == 2
        unregister_crew_priority("FakeRoundtrip")
        assert lookup_crew_priority(comp) == CREW_PRIORITY_DEFAULT

    def test_unregister_unknown_is_noop(self):
        unregister_crew_priority("NeverRegistered")  # must not raise


class TestStatContributorRegistration:
    def test_apply_invokes_registered_contributor_when_ability_matches(self, cleanup):
        _, stat_added = cleanup
        calls: list = []

        def fn(ship, comp):
            calls.append((ship, comp))

        register_stat_contributor("FakeStatAbility", fn, domain="ut")
        stat_added.append(("FakeStatAbility", "ut"))

        ship = MagicMock()
        comp = MagicMock()
        comp.has_ability = lambda name: name == "FakeStatAbility"

        apply_registered_contributors(ship, comp)
        assert calls == [(ship, comp)]

    def test_apply_skips_when_ability_missing(self, cleanup):
        _, stat_added = cleanup
        calls: list = []

        def fn(ship, comp):
            calls.append((ship, comp))

        register_stat_contributor("FakeMissingAbility", fn, domain="ut")
        stat_added.append(("FakeMissingAbility", "ut"))

        ship = MagicMock()
        comp = MagicMock()
        comp.has_ability = lambda _name: False

        apply_registered_contributors(ship, comp)
        assert calls == []

    def test_double_registration_raises(self, cleanup):
        _, stat_added = cleanup

        def fn(ship, comp):  # pragma: no cover — never called
            pass

        register_stat_contributor("FakeDup", fn, domain="ut")
        stat_added.append(("FakeDup", "ut"))

        with pytest.raises(ValueError, match="already registered"):
            register_stat_contributor("FakeDup", fn, domain="ut")

    def test_same_ability_different_domain_is_allowed(self, cleanup):
        _, stat_added = cleanup

        def fn(ship, comp):  # pragma: no cover
            pass

        register_stat_contributor("FakeMultiDomain", fn, domain="ut1")
        stat_added.append(("FakeMultiDomain", "ut1"))
        register_stat_contributor("FakeMultiDomain", fn, domain="ut2")
        stat_added.append(("FakeMultiDomain", "ut2"))
