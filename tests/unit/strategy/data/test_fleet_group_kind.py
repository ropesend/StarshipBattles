"""PROJ-FMS-A Phase 4: Fleet.group_kind + command-validation invariant."""
from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.data.fleet import Fleet
from game.strategy.engine.handlers.base import BaseCommandHandler


class TestFleetGroupKind:
    def test_default_is_fleet(self):
        f = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        assert f.group_kind == "fleet"
        assert f.can_strategic_move is True

    def test_mine_group_rejects_strategic_move(self):
        """PROJ-431 Phase 2: ``"mine_group"`` is no longer a legal
        ``Fleet.group_kind``. The constructor must reject it — a
        :class:`MineGroup` is a sibling type, not a Fleet.
        """
        with pytest.raises(ValueError):
            Fleet(fleet_id=2, owner_id=0, location=HexCoord(0, 0),
                  group_kind="mine_group")

    def test_invalid_group_kind_raises(self):
        with pytest.raises(ValueError):
            Fleet(fleet_id=3, owner_id=0, location=HexCoord(0, 0),
                  group_kind="armada")

    def test_serialize_deserialize_roundtrip(self):
        f = Fleet(fleet_id=4, owner_id=0, location=HexCoord(2, 1),
                  group_kind="fighter_group")
        d = f.to_dict()
        assert d["group_kind"] == "fighter_group"
        f2 = Fleet.from_dict(d)
        assert f2.group_kind == "fighter_group"

    def test_save_format_predates_group_kind_defaults_to_fleet(self):
        """Old saves without ``group_kind`` deserialize to "fleet"."""
        d = {
            "id": 99, "owner_id": 0,
            "location": {"q": 0, "r": 0},
            "speed": 5.0,
            "ships": [],
        }
        f = Fleet.from_dict(d)
        assert f.group_kind == "fleet"


class TestRejectIfNonFleetGroupHelper:
    def test_returns_none_for_real_fleet(self):
        f = Fleet(fleet_id=10, owner_id=0, location=HexCoord(0, 0))
        result = BaseCommandHandler._reject_if_non_fleet_group(f, "Move")
        assert result is None

    def test_mine_group_kind_no_longer_legal_on_fleet(self):
        """PROJ-431 Phase 2: ``"mine_group"`` was removed from
        ``Fleet.group_kind``'s legal-values set. The guard is moot for
        mines because they are not ``Fleet``s anymore — they cannot
        reach a fleet-typed handler parameter.
        """
        with pytest.raises(ValueError):
            Fleet(fleet_id=11, owner_id=0, location=HexCoord(0, 0),
                  group_kind="mine_group")

    def test_returns_error_for_satellite_group(self):
        f = Fleet(fleet_id=12, owner_id=0, location=HexCoord(0, 0),
                  group_kind="satellite_group")
        result = BaseCommandHandler._reject_if_non_fleet_group(f, "Build")
        assert isinstance(result, ValidationResult)
        assert not result.is_valid

    def test_returns_error_for_fighter_group(self):
        f = Fleet(fleet_id=13, owner_id=0, location=HexCoord(0, 0),
                  group_kind="fighter_group")
        result = BaseCommandHandler._reject_if_non_fleet_group(f, "Warp")
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
