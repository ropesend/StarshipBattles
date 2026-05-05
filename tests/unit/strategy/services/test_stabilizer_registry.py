"""Characterization tests for stabilizer_registry (PROJ-336).

Per Decision D-005, `find_abilities_in_scope` is mocked via monkeypatch so
the iteration order across `STABILIZERS x empires x scopes` is observable.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.data.order_types import OrderType
import game.strategy.services.stabilizer_registry as stab_module
from game.strategy.services.stabilizer_registry import (
    StabilizerSpec,
    find_blocking_stabilizer,
)


# Sentinels for empire identity in mocks.
def _empire(empire_id: int) -> MagicMock:
    e = MagicMock()
    e.id = empire_id
    return e


def _patch_scanner(monkeypatch, fn):
    """Replace the lazily-imported `find_abilities_in_scope` symbol.

    `find_blocking_stabilizer` does `from ... import find_abilities_in_scope`
    inside its body, so we patch the source module.
    """
    from game.strategy.services import strategic_ability_scanner as scanner_mod
    monkeypatch.setattr(scanner_mod, "find_abilities_in_scope", fn)


class TestEarlyReturnPaths:
    def test_returns_none_when_reference_planet_is_none(self, monkeypatch):
        # D-007 observation: this short-circuits BEFORE checking order_type.
        called = []

        def fake_scanner(*a, **kw):
            called.append((a, kw))
            return True

        _patch_scanner(monkeypatch, fake_scanner)

        result = find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET,
            reference_planet=None,
            galaxy=MagicMock(),
            empires=[_empire(1)],
        )
        assert result is None
        assert called == []  # scanner never invoked

    def test_returns_none_when_order_type_not_in_any_spec_blocks(self, monkeypatch):
        scanner = MagicMock(return_value=True)
        _patch_scanner(monkeypatch, scanner)

        result = find_blocking_stabilizer(
            OrderType.MOVE,
            reference_planet=MagicMock(),
            galaxy=MagicMock(),
            empires=[_empire(1)],
        )
        assert result is None
        # No spec.blocks contains MOVE, so the inner loops never run.
        scanner.assert_not_called()

    def test_returns_none_when_no_empire_has_active_stabilizer(self, monkeypatch):
        _patch_scanner(monkeypatch, MagicMock(return_value=False))

        result = find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET,
            reference_planet=MagicMock(),
            galaxy=MagicMock(),
            empires=[_empire(1), _empire(2)],
        )
        assert result is None

    def test_returns_none_when_empires_iterable_is_empty(self, monkeypatch):
        scanner = MagicMock(return_value=True)
        _patch_scanner(monkeypatch, scanner)

        result = find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET,
            reference_planet=MagicMock(),
            galaxy=MagicMock(),
            empires=[],
        )
        assert result is None
        scanner.assert_not_called()


class TestPositiveMatches:
    def test_returns_geologic_spec_for_implode_planet_when_active(self, monkeypatch):
        _patch_scanner(monkeypatch, MagicMock(return_value=True))
        result = find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET, MagicMock(), MagicMock(), [_empire(1)]
        )
        assert result is not None
        assert result.ability_name == "GeologicStabilizer"

    def test_returns_stellar_spec_for_stellerate_star_when_active(self, monkeypatch):
        _patch_scanner(monkeypatch, MagicMock(return_value=True))
        result = find_blocking_stabilizer(
            OrderType.STELLERATE_STAR, MagicMock(), MagicMock(), [_empire(1)]
        )
        assert result is not None
        assert result.ability_name == "StellarStabilizer"

    def test_returns_stellar_spec_for_create_dyson_sphere_when_active(self, monkeypatch):
        _patch_scanner(monkeypatch, MagicMock(return_value=True))
        result = find_blocking_stabilizer(
            OrderType.CREATE_DYSON_SPHERE, MagicMock(), MagicMock(), [_empire(1)]
        )
        assert result is not None
        assert result.ability_name == "StellarStabilizer"

    def test_returns_warpfield_spec_for_open_warp_point_when_active(self, monkeypatch):
        _patch_scanner(monkeypatch, MagicMock(return_value=True))
        result = find_blocking_stabilizer(
            OrderType.OPEN_WARP_POINT, MagicMock(), MagicMock(), [_empire(1)]
        )
        assert result is not None
        assert result.ability_name == "WarpFieldStabilizer"


class TestIterationOrder:
    def test_first_empire_with_match_wins_over_later_empire(self, monkeypatch):
        # Empire 1 has the active stabilizer; empire 2 also does. Per the
        # `for empire in empires` loop, empire 1 must short-circuit the search.
        empire_a = _empire(1)
        empire_b = _empire(2)

        seen_empires: list = []

        def fake_scanner(ability_name, ref_planet, galaxy, empire, scope, **kw):
            seen_empires.append(empire)
            return empire is empire_a

        _patch_scanner(monkeypatch, fake_scanner)

        result = find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET, MagicMock(), MagicMock(), [empire_a, empire_b]
        )
        assert result is not None
        assert result.ability_name == "GeologicStabilizer"
        # First call is empire_a; loop returns immediately on hit, so empire_b
        # is never queried.
        assert seen_empires == [empire_a]

    def test_geologic_spec_matched_before_stellar_when_both_block_order_type(
        self, monkeypatch
    ):
        """MAJ-005 fix — pins STABILIZERS outer-loop ordering.

        Construct a synthetic STABILIZERS tuple where Geologic AND Stellar
        both block the same OrderType, and matching active stabilizers exist
        for both. The outer `for spec in STABILIZERS` loop visits Geologic
        first, so Geologic must be returned. Reordering the tuple would
        change this answer — that's the regression this test catches.
        """
        synthetic = (
            StabilizerSpec(
                ability_name="GeologicStabilizer",
                scopes=("planet",),
                blocks=(OrderType.IMPLODE_PLANET,),
            ),
            StabilizerSpec(
                ability_name="StellarStabilizer",
                scopes=("system",),
                blocks=(OrderType.IMPLODE_PLANET,),  # synthetic overlap
            ),
        )
        monkeypatch.setattr(stab_module, "STABILIZERS", synthetic)
        _patch_scanner(monkeypatch, MagicMock(return_value=True))

        result = find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET, MagicMock(), MagicMock(), [_empire(1)]
        )
        assert result is not None
        assert result.ability_name == "GeologicStabilizer"

    def test_geologic_scope_iteration_order_planet_then_sector_then_system(
        self, monkeypatch
    ):
        # No empire has anything active (scanner always False); pin that the
        # call sequence walks `spec.scopes` in declared order per empire.
        scope_calls: list = []

        def fake_scanner(ability_name, ref_planet, galaxy, empire, scope, **kw):
            if ability_name == "GeologicStabilizer":
                scope_calls.append(scope)
            return False

        _patch_scanner(monkeypatch, fake_scanner)

        find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET, MagicMock(), MagicMock(), [_empire(1)]
        )
        assert scope_calls == ["planet", "sector", "system"]


class TestScannerKwargs:
    def test_calls_find_abilities_in_scope_with_require_active_true(self, monkeypatch):
        captured: list = []

        def fake_scanner(*args, **kwargs):
            captured.append(kwargs)
            return False

        _patch_scanner(monkeypatch, fake_scanner)

        find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET, MagicMock(), MagicMock(), [_empire(1)]
        )
        assert captured  # at least one call
        for kw in captured:
            assert kw["require_active"] is True

    def test_passes_component_registry_through_to_scanner_unchanged(self, monkeypatch):
        captured_registries: list = []

        def fake_scanner(*args, **kwargs):
            captured_registries.append(kwargs.get("registries"))
            return False

        _patch_scanner(monkeypatch, fake_scanner)

        # Case 1: None passes through.
        find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET, MagicMock(), MagicMock(), [_empire(1)],
            component_registry=None,
        )
        assert captured_registries[0] is None

        # Case 2: arbitrary sentinel passes through unchanged.
        sentinel = object()
        captured_registries.clear()
        find_blocking_stabilizer(
            OrderType.IMPLODE_PLANET, MagicMock(), MagicMock(), [_empire(1)],
            component_registry=sentinel,
        )
        assert captured_registries[0] is sentinel


# PROJ-353A Tier-7 (T2.8): the previous `TestStabilizersTuple` class
# pinned the literal contents of the `STABILIZERS` tuple. That was
# vacuous — it re-asserted the module's source code rather than any
# behavior. The three behaviors that *actually* depend on STABILIZERS'
# contents and ordering are already pinned elsewhere in this file:
#
# - GeologicStabilizer + IMPLODE_PLANET → see
#   `test_returns_geologic_spec_for_implode_planet_when_active`.
# - StellarStabilizer + STELLERATE_STAR / CREATE_DYSON_SPHERE → see
#   `test_returns_stellar_spec_for_stellerate_star_when_active` and
#   `test_returns_stellar_spec_for_create_dyson_sphere_when_active`.
# - WarpFieldStabilizer + OPEN_WARP_POINT → see
#   `test_returns_warpfield_spec_for_open_warp_point_when_active`.
# - Definition-order priority → see
#   `test_geologic_spec_matched_before_stellar_when_both_block_order_type`.
#
# Adding/removing a stabilizer requires adding a behavioral test in the
# pattern above, not editing this file.
