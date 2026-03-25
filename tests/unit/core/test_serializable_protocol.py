"""Tests for the Serializable protocol definition."""
from typing import Any, Dict

from game.core.protocols import ISerializable


class _GoodSerializable:
    """Minimal class that satisfies ISerializable."""

    def to_dict(self) -> Dict[str, Any]:
        return {"key": "value"}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "_GoodSerializable":
        return cls()


class _MissingFromDict:
    """Class missing from_dict (not serializable)."""

    def to_dict(self) -> Dict[str, Any]:
        return {}


class _MissingToDict:
    """Class missing to_dict (not serializable)."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "_MissingToDict":
        return cls()


class TestISerializableProtocol:
    """Verify the ISerializable protocol for type checking."""

    def test_isinstance_check_passes(self):
        obj = _GoodSerializable()
        assert isinstance(obj, ISerializable)

    def test_isinstance_check_fails_missing_from_dict(self):
        obj = _MissingFromDict()
        assert not isinstance(obj, ISerializable)

    def test_isinstance_check_fails_missing_to_dict(self):
        obj = _MissingToDict()
        assert not isinstance(obj, ISerializable)

    def test_battle_state_dataclasses_satisfy_protocol(self):
        """Verify that existing battle state dataclasses satisfy ISerializable."""
        from game.simulation.battle_state import (
            ComponentState, ShipState, ProjectileState,
            BattleState, BattleResults,
        )
        # These are dataclasses with to_dict/from_dict - they should pass
        # We check the class, not instances, since from_dict is a classmethod
        assert hasattr(ComponentState, 'to_dict')
        assert hasattr(ComponentState, 'from_dict')
        assert hasattr(ShipState, 'to_dict')
        assert hasattr(ShipState, 'from_dict')
        assert hasattr(BattleState, 'to_dict')
        assert hasattr(BattleState, 'from_dict')
        assert hasattr(BattleResults, 'to_dict')
        assert hasattr(BattleResults, 'from_dict')
        assert hasattr(ProjectileState, 'to_dict')
        assert hasattr(ProjectileState, 'from_dict')
