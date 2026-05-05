"""
PROJ-367 Phase 2 — registry-as-pipeline acceptance tests.

Pins behavior of the unified Phase-3 stat-contributor pipeline:

- Built-ins are registry entries (seeded at module import as defaults).
- Modders register the same way; replacement is implicit on conflict
  (`RegistrationConflictPolicy.REPLACE_WARN` default; `REPLACE_SILENT` /
  `APPEND` / `ERROR` are the alternative policies).
- Replacement entries inherit ``phase_order=99`` (modder default) so they
  fire AFTER non-replaced built-ins (which use 10..50).
- ``RegistrationHandle`` makes APPEND entries individually addressable.
- ``unregister_stat_contributor(handle)`` after a REPLACE_* restores the
  underlying default; unregistering a default by handle raises
  ``CannotUnregisterDefaultError``.
- ``reset_stat_contributor_registry()`` is idempotent (clear AND re-seed
  defaults).

These tests are TDD-first for Phase 2 — they fail on the pre-Phase 2 code
and pin the Phase 2 contract.
"""
from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Replacement / append / phase-ordering / handle round-trip
# ---------------------------------------------------------------------------


def test_register_returns_handle():
    """``register_stat_contributor`` returns a ``RegistrationHandle``."""
    from game.simulation.entities.stat_contributors.registry import (
        RegistrationHandle,
        register_stat_contributor,
        unregister_stat_contributor,
    )

    def fn(ship, comp, acc):  # pragma: no cover — never invoked
        pass

    handle = register_stat_contributor("FakeAbilityA", fn)
    try:
        assert isinstance(handle, RegistrationHandle)
        assert handle.ability_name == "FakeAbilityA"
    finally:
        unregister_stat_contributor(handle)


def test_replace_silent_replaces_default_with_no_warning(caplog):
    """REPLACE_SILENT: new entry replaces the built-in default; no warning."""
    from game.simulation.entities.stat_contributors.registry import (
        RegistrationConflictPolicy,
        STAT_CONTRIBUTOR_REGISTRY,
        register_stat_contributor,
        unregister_stat_contributor,
    )

    def fn(ship, comp, acc):  # pragma: no cover
        pass

    with caplog.at_level(logging.WARNING):
        handle = register_stat_contributor(
            "ShieldProjection", fn, policy=RegistrationConflictPolicy.REPLACE_SILENT
        )
    try:
        # Replacement is recorded as the active entry for ShieldProjection.
        active = STAT_CONTRIBUTOR_REGISTRY.get_active_entry("ShieldProjection")
        assert active.contributor is fn
        # No warning for SILENT.
        assert not any(
            "ShieldProjection" in r.getMessage() for r in caplog.records
            if r.levelno >= logging.WARNING
        )
    finally:
        unregister_stat_contributor(handle)


def test_replace_warn_emits_log(caplog):
    """REPLACE_WARN (default policy) logs a warning naming the ability."""
    from game.simulation.entities.stat_contributors.registry import (
        register_stat_contributor,
        unregister_stat_contributor,
    )

    def fn(ship, comp, acc):  # pragma: no cover
        pass

    with caplog.at_level(logging.WARNING, logger="game.simulation.entities.stat_contributors.registry"):
        handle = register_stat_contributor("ShieldProjection", fn)
    try:
        msg = " ".join(r.getMessage() for r in caplog.records)
        assert "ShieldProjection" in msg
    finally:
        unregister_stat_contributor(handle)


def test_error_policy_raises_on_conflict():
    """ERROR policy raises on registering for an existing ability."""
    from game.simulation.entities.stat_contributors.registry import (
        RegistrationConflictError,
        RegistrationConflictPolicy,
        register_stat_contributor,
    )

    def fn(ship, comp, acc):  # pragma: no cover
        pass

    with pytest.raises(RegistrationConflictError):
        register_stat_contributor(
            "ShieldProjection", fn, policy=RegistrationConflictPolicy.ERROR
        )


def test_append_policy_keeps_default_and_addressable_handle():
    """APPEND adds a second entry; default + appended both fire; handle removes only appended."""
    from game.simulation.entities.stat_contributors.registry import (
        RegistrationConflictPolicy,
        STAT_CONTRIBUTOR_REGISTRY,
        register_stat_contributor,
        unregister_stat_contributor,
    )

    calls: list[str] = []

    def fn_appended(ship, comp, acc):
        calls.append("appended")

    handle = register_stat_contributor(
        "ShieldProjection", fn_appended, policy=RegistrationConflictPolicy.APPEND
    )
    try:
        all_entries = STAT_CONTRIBUTOR_REGISTRY.get_entries("ShieldProjection")
        assert len(all_entries) == 2  # default + appended
        # The appended entry is identifiable by handle.entry_id.
        assert any(e.entry_id == handle.entry_id for e in all_entries)
    finally:
        unregister_stat_contributor(handle)
        # Default still there.
        all_entries_after = STAT_CONTRIBUTOR_REGISTRY.get_entries("ShieldProjection")
        assert len(all_entries_after) == 1
        assert all_entries_after[0].is_default


def test_unregister_replace_restores_default():
    """After REPLACE_*, unregister restores the underlying default entry."""
    from game.simulation.entities.stat_contributors.registry import (
        RegistrationConflictPolicy,
        STAT_CONTRIBUTOR_REGISTRY,
        register_stat_contributor,
        unregister_stat_contributor,
    )

    def fn(ship, comp, acc):  # pragma: no cover
        pass

    default_before = STAT_CONTRIBUTOR_REGISTRY.get_active_entry("ShieldProjection")
    assert default_before.is_default
    handle = register_stat_contributor(
        "ShieldProjection", fn, policy=RegistrationConflictPolicy.REPLACE_SILENT
    )
    assert STAT_CONTRIBUTOR_REGISTRY.get_active_entry("ShieldProjection").contributor is fn
    unregister_stat_contributor(handle)
    after = STAT_CONTRIBUTOR_REGISTRY.get_active_entry("ShieldProjection")
    assert after.is_default
    assert after.contributor is default_before.contributor


def test_unregister_default_by_handle_raises():
    """Defaults cannot be unregistered by handle (managed via reset/seed)."""
    from game.simulation.entities.stat_contributors.registry import (
        CannotUnregisterDefaultError,
        STAT_CONTRIBUTOR_REGISTRY,
        unregister_stat_contributor,
    )

    default = STAT_CONTRIBUTOR_REGISTRY.get_active_entry("ShieldProjection")
    handle = default.as_handle()
    with pytest.raises(CannotUnregisterDefaultError):
        unregister_stat_contributor(handle)


def test_replacement_inherits_modder_phase_order_99():
    """A replacement (default policy=REPLACE_WARN) inherits phase_order=99 unless overridden."""
    from game.simulation.entities.stat_contributors.registry import (
        STAT_CONTRIBUTOR_REGISTRY,
        register_stat_contributor,
        unregister_stat_contributor,
    )

    def fn(ship, comp, acc):  # pragma: no cover
        pass

    handle = register_stat_contributor("ShieldProjection", fn)
    try:
        active = STAT_CONTRIBUTOR_REGISTRY.get_active_entry("ShieldProjection")
        assert active.phase_order == 99
    finally:
        unregister_stat_contributor(handle)


def test_phase_order_iteration_order():
    """``iter_for(comp)`` yields entries in ascending ``phase_order``."""
    from game.simulation.entities.stat_contributors.registry import (
        RegistrationConflictPolicy,
        STAT_CONTRIBUTOR_REGISTRY,
        register_stat_contributor,
        unregister_stat_contributor,
    )

    fired: list[str] = []

    def fn_low(ship, comp, acc):
        fired.append("low")

    def fn_high(ship, comp, acc):
        fired.append("high")

    h_low = register_stat_contributor(
        "_FakePhaseOrderA",
        fn_low,
        phase_order=5,
    )
    h_high = register_stat_contributor(
        "_FakePhaseOrderB",
        fn_high,
        phase_order=99,
    )
    try:
        # Component reports both abilities present.
        comp = MagicMock()
        comp.has_ability = lambda name: name in {"_FakePhaseOrderA", "_FakePhaseOrderB"}
        for entry in STAT_CONTRIBUTOR_REGISTRY.iter_for(comp):
            entry.contributor(None, comp, None)
        # _FakePhaseOrderA (phase 5) fires before _FakePhaseOrderB (phase 99).
        assert fired.index("low") < fired.index("high")
    finally:
        unregister_stat_contributor(h_low)
        unregister_stat_contributor(h_high)


def test_reset_re_seeds_defaults():
    """``reset_stat_contributor_registry`` clears AND re-seeds default entries."""
    from game.simulation.entities.stat_contributors.registry import (
        STAT_CONTRIBUTOR_REGISTRY,
        register_stat_contributor,
        reset_stat_contributor_registry,
        unregister_stat_contributor,
    )

    def fn(ship, comp, acc):  # pragma: no cover
        pass

    # Add a non-default entry.
    handle = register_stat_contributor("_FakeNonDefault", fn)
    assert STAT_CONTRIBUTOR_REGISTRY.get_active_entry("_FakeNonDefault") is not None

    reset_stat_contributor_registry()

    # Modder entry gone.
    assert STAT_CONTRIBUTOR_REGISTRY.get_active_entry("_FakeNonDefault") is None
    # Defaults present again — ShieldProjection is a known default.
    sp = STAT_CONTRIBUTOR_REGISTRY.get_active_entry("ShieldProjection")
    assert sp is not None
    assert sp.is_default


# ---------------------------------------------------------------------------
# Replacement-vs-non-replaced ordering through `_phase_stats_aggregation`
# ---------------------------------------------------------------------------


def test_replace_shield_projection_avoids_double_count(fresh_registries):
    """End-to-end: registering for ShieldProjection replaces the built-in
    so ``ship.max_shields`` reflects ONLY the replacement (no double-count)."""
    from game.core.json_utils import load_json
    from game.core.paths import Paths
    from game.simulation.entities.ship import Ship
    from game.simulation.entities.stat_contributors.registry import (
        RegistrationConflictPolicy,
        register_stat_contributor,
        unregister_stat_contributor,
    )

    def fn(ship, comp, acc):
        # Set to a sentinel value if any ShieldProjection-bearing component
        # is encountered. (The replacement REPLACES the built-in's add of
        # capacity from ShieldProjection abilities.)
        acc["max_shields"] = 999.0

    handle = register_stat_contributor(
        "ShieldProjection", fn, policy=RegistrationConflictPolicy.REPLACE_SILENT
    )
    try:
        designs = Paths.get_starter_designs_dir()
        ship = Ship.from_dict(
            load_json(str(designs / "qs_battleship.json")), registries=fresh_registries
        )
        ship.recalculate_stats()
        # The replacement set acc["max_shields"]=999 (no double-count from
        # built-in default + replacement).
        assert ship.max_shields == 999.0
    finally:
        unregister_stat_contributor(handle)


def test_no_builtin_handled_abilities_export():
    """Phase 2 deletion: BUILTIN_HANDLED_ABILITIES / suppression helpers retired."""
    from game.simulation.entities.stat_contributors import registry as reg

    assert not hasattr(reg, "BUILTIN_HANDLED_ABILITIES"), (
        "BUILTIN_HANDLED_ABILITIES should be deleted in Phase 2"
    )
    assert not hasattr(reg, "is_builtin_suppressed_for"), (
        "is_builtin_suppressed_for should be deleted in Phase 2"
    )
    assert not hasattr(reg, "apply_registered_contributors"), (
        "apply_registered_contributors should be deleted in Phase 2"
    )
