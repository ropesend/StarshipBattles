"""
Unit tests for the stat contributor registry.

Covers register/unregister round-trips and the priority lookup helper in
isolation; the end-to-end extension test in
``tests/unit/simulation/entities/test_stat_contributor_extension.py`` covers
the full ship pipeline; the unified-pipeline acceptance tests in
``test_registry_pipeline.py`` cover replacement / append / phase-ordering /
default-managed behavior.

PROJ-360 audit (2026-05-05): updated for the contributor signature
``(ship, comp, acc) -> None`` (EXT-12) and per-ability dedup (EXT-01).
PROJ-367 Phase 2: migrated to handle-based unregister; suppression
frozenset (``BUILTIN_HANDLED_ABILITIES``) is gone — replacement is
implicit via ``RegistrationConflictPolicy.REPLACE_*``.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.simulation.entities.stat_contributors.registry import (
    CREW_PRIORITY_DEFAULT,
    RegistrationConflictError,
    RegistrationConflictPolicy,
    STAT_CONTRIBUTOR_REGISTRY,
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
    stat_handles: list = []  # PROJ-367 Phase 2: handle-based.
    yield crew_added, stat_handles
    for n in crew_added:
        unregister_crew_priority(n)
    for h in stat_handles:
        try:
            unregister_stat_contributor(h)
        except Exception:  # Intentional broad catch: cleanup is best-effort across test failures
            pass


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

    def test_unregister_returns_to_default(self):
        comp = MagicMock()
        comp.has_ability = lambda name: name == "FakeRoundtrip"

        register_crew_priority("FakeRoundtrip", 2)
        assert lookup_crew_priority(comp) == 2
        unregister_crew_priority("FakeRoundtrip")
        assert lookup_crew_priority(comp) == CREW_PRIORITY_DEFAULT

    def test_unregister_unknown_is_noop(self):
        unregister_crew_priority("NeverRegistered")  # must not raise


class TestStatContributorRegistration:
    """PROJ-367 Phase 2 — handle-based registration."""

    def test_active_entry_invokes_registered_contributor_when_ability_matches(
        self, cleanup
    ):
        _, stat_handles = cleanup
        calls: list = []

        def fn(ship, comp, acc):
            calls.append((ship, comp, acc))

        h = register_stat_contributor("FakeStatAbility", fn)
        stat_handles.append(h)

        ship = MagicMock()
        comp = MagicMock()
        comp.has_ability = lambda name: name == "FakeStatAbility"
        acc: dict = {}

        # Iterate the registry exactly the way ship_stats.py does.
        for entry in STAT_CONTRIBUTOR_REGISTRY.iter_for(comp):
            if entry.ability_name == "FakeStatAbility":
                entry.contributor(ship, comp, acc)
        assert calls == [(ship, comp, acc)]

    def test_iter_skips_when_ability_missing(self, cleanup):
        _, stat_handles = cleanup
        calls: list = []

        def fn(ship, comp, acc):
            calls.append((ship, comp, acc))

        h = register_stat_contributor("FakeMissingAbility", fn)
        stat_handles.append(h)

        ship = MagicMock()
        comp = MagicMock()
        comp.has_ability = lambda _name: False

        for entry in STAT_CONTRIBUTOR_REGISTRY.iter_for(comp):
            entry.contributor(ship, comp, {})
        assert calls == []

    def test_double_registration_with_error_policy_raises(self, cleanup):
        """PROJ-367 Phase 2: ``policy=ERROR`` raises on conflict.

        Default policy (``REPLACE_WARN``) replaces silently with a log; tests
        for that path live in ``test_registry_pipeline.py``.
        """
        _, stat_handles = cleanup

        def fn(ship, comp, acc):  # pragma: no cover — never called
            pass

        h1 = register_stat_contributor("FakeDup", fn)
        stat_handles.append(h1)

        with pytest.raises(RegistrationConflictError):
            register_stat_contributor(
                "FakeDup", fn, policy=RegistrationConflictPolicy.ERROR
            )


class TestBuiltinReplacement:
    """PROJ-367 Phase 2: replacement is implicit; no suppression frozenset.

    Registering for a built-in ability with the default policy
    (``REPLACE_WARN``) replaces the default; with ``policy=ERROR`` it
    raises. Tests for the full replace/append/phase-order semantics live
    in ``test_registry_pipeline.py``.
    """

    def test_register_for_builtin_ability_replaces_default(self, cleanup):
        _, stat_handles = cleanup

        def fn(ship, comp, acc):  # pragma: no cover
            pass

        h = register_stat_contributor(
            "ShieldProjection", fn, policy=RegistrationConflictPolicy.REPLACE_SILENT
        )
        stat_handles.append(h)

        active = STAT_CONTRIBUTOR_REGISTRY.get_active_entry("ShieldProjection")
        assert active.contributor is fn
        assert not active.is_default

    def test_register_for_builtin_ability_with_error_policy_raises(self):
        def fn(ship, comp, acc):  # pragma: no cover
            pass

        with pytest.raises(RegistrationConflictError):
            register_stat_contributor(
                "ShieldProjection", fn, policy=RegistrationConflictPolicy.ERROR
            )
