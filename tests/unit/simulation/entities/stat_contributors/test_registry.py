"""
Unit tests for the stat contributor registry.

Covers register/unregister round-trips and the priority lookup helper in
isolation; the end-to-end extension test in
``tests/unit/simulation/entities/test_stat_contributor_extension.py`` covers
the full ship pipeline.

PROJ-360 audit (2026-05-05): updated for the new contributor signature
``(ship, comp, acc) -> None`` (EXT-12) and per-ability dedup (EXT-01). The
``test_same_ability_different_domain_is_allowed`` test was removed — it
codified the old per-(ability, domain) dedup which the audit identified as
a double-counting bug.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.simulation.entities.stat_contributors.registry import (
    CREW_PRIORITY_DEFAULT,
    apply_registered_contributors,
    is_builtin_suppressed_for,
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

        def fn(ship, comp, acc):
            calls.append((ship, comp, acc))

        register_stat_contributor("FakeStatAbility", fn, domain="ut")
        stat_added.append(("FakeStatAbility", "ut"))

        ship = MagicMock()
        comp = MagicMock()
        comp.has_ability = lambda name: name == "FakeStatAbility"
        acc: dict = {}

        apply_registered_contributors(ship, comp, acc)
        assert calls == [(ship, comp, acc)]

    def test_apply_skips_when_ability_missing(self, cleanup):
        _, stat_added = cleanup
        calls: list = []

        def fn(ship, comp, acc):
            calls.append((ship, comp, acc))

        register_stat_contributor("FakeMissingAbility", fn, domain="ut")
        stat_added.append(("FakeMissingAbility", "ut"))

        ship = MagicMock()
        comp = MagicMock()
        comp.has_ability = lambda _name: False

        apply_registered_contributors(ship, comp, {})
        assert calls == []

    def test_double_registration_raises(self, cleanup):
        """Per-ability dedup (PROJ-360 audit EXT-01): re-registering an
        ability — even with a different domain tag — must fail."""
        _, stat_added = cleanup

        def fn(ship, comp, acc):  # pragma: no cover — never called
            pass

        register_stat_contributor("FakeDup", fn, domain="ut")
        stat_added.append(("FakeDup", "ut"))

        with pytest.raises(ValueError, match="already registered"):
            register_stat_contributor("FakeDup", fn, domain="ut")
        # Different domain tag does NOT escape the dedup guard anymore.
        with pytest.raises(ValueError, match="already registered"):
            register_stat_contributor("FakeDup", fn, domain="other-domain")


class TestBuiltinSuppression:
    """PROJ-360 audit EXT-02: a registered contributor for a built-in
    ability suppresses the corresponding built-in handler."""

    def test_unregistered_ability_is_not_suppressed(self):
        assert is_builtin_suppressed_for("ShieldProjection") is False

    def test_registering_builtin_ability_flags_it_as_suppressed(self, cleanup):
        _, stat_added = cleanup

        def fn(ship, comp, acc):  # pragma: no cover — never called
            pass

        register_stat_contributor("ShieldProjection", fn, domain="ext_ut")
        stat_added.append(("ShieldProjection", "ext_ut"))
        assert is_builtin_suppressed_for("ShieldProjection") is True

    def test_unregistering_clears_suppression(self):
        def fn(ship, comp, acc):  # pragma: no cover
            pass

        register_stat_contributor("ShieldRegeneration", fn, domain="ext_ut")
        assert is_builtin_suppressed_for("ShieldRegeneration") is True
        unregister_stat_contributor("ShieldRegeneration")
        assert is_builtin_suppressed_for("ShieldRegeneration") is False

    def test_non_builtin_ability_is_never_suppressed(self, cleanup):
        _, stat_added = cleanup

        def fn(ship, comp, acc):  # pragma: no cover
            pass

        register_stat_contributor("FakeNonBuiltin", fn, domain="ext_ut")
        stat_added.append(("FakeNonBuiltin", "ext_ut"))
        # The ability isn't in BUILTIN_HANDLED_ABILITIES so suppression
        # never fires regardless of registration state.
        assert is_builtin_suppressed_for("FakeNonBuiltin") is False
