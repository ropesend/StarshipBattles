"""PROJ-431 Phase 3 — Fleet.group_kind + `_reject_if_non_fleet_group` are GONE.

This module used to pin the contract that ``Fleet.group_kind`` exists,
defaults to ``"fleet"``, and rejects non-fleet values; and that the
:func:`BaseCommandHandler._reject_if_non_fleet_group` guard returns a
:class:`ValidationResult` for fighter/satellite groups.

PROJ-431 Phase 3 (2026-05-17) deleted both. Deployed mines / fighters /
satellites are typed sibling models (:class:`MineGroup`,
:class:`FighterWing`, :class:`SatelliteConstellation`) on
``empire.deployed_groups`` — they are structurally not :class:`Fleet`s
and never reach a fleet-typed handler parameter.

The tests here pin the *absence* of the deleted surface so a future
regression that re-adds either symbol fails loudly.
"""
from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.engine.handlers.base import BaseCommandHandler


class TestFleetGroupKindDeleted:
    def test_fleet_has_no_group_kind_attribute(self):
        f = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        assert not hasattr(f, "group_kind")

    def test_can_strategic_move_always_true(self):
        f = Fleet(fleet_id=2, owner_id=0, location=HexCoord(0, 0))
        assert f.can_strategic_move is True

    def test_fleet_init_rejects_legacy_group_kind_kwarg(self):
        with pytest.raises(TypeError):
            Fleet(
                fleet_id=3, owner_id=0, location=HexCoord(0, 0),
                group_kind="fleet",  # type: ignore[call-arg]
            )

    def test_to_dict_does_not_emit_group_kind(self):
        f = Fleet(fleet_id=4, owner_id=0, location=HexCoord(2, 1))
        data = f.to_dict()
        assert "group_kind" not in data

    def test_from_dict_silently_ignores_legacy_group_kind(self):
        """Phase 3 disposable-saves contract: legacy saves with
        ``group_kind`` deserialise without error; the field is dropped."""
        d = {
            "id": 99, "owner_id": 0,
            "location": {"q": 0, "r": 0},
            "speed": 5.0,
            "ships": [],
            "group_kind": "fighter_group",  # legacy
        }
        f = Fleet.from_dict(d)
        assert not hasattr(f, "group_kind")


class TestRejectIfNonFleetGroupDeleted:
    def test_helper_no_longer_exists(self):
        assert not hasattr(
            BaseCommandHandler, "_reject_if_non_fleet_group"
        )
