"""Characterization tests for game/strategy/data/squadron.py.

PROJ-335 Phase 1. Pins:

- ``add_ship`` / ``remove_ship`` semantics (idempotent add, bool return).
- ``all_ships`` ordering (members + lone_ships, in that order).
- ``to_dict`` discriminator and asymmetric serialization (None
  ``spatial_behavior`` and empty ``spatial_behavior_params`` are omitted).
- ``from_dict`` reconstruction (including BattleRole enum parse).
- ``node_id`` auto-generation when not supplied.

Mode: characterization-only. Ships are stubbed via ``types.SimpleNamespace``
to keep the data-layer tests data-layer-only.
"""
from __future__ import annotations

from types import SimpleNamespace

from game.strategy.data.fleet_hierarchy import BattleRole, CombatPolicy
from game.strategy.data.squadron import Squadron


class TestShipMembership:
    """add_ship / remove_ship / all_ships."""

    def test_add_ship_is_idempotent(self):
        sq = Squadron(name="Alpha")
        ship = SimpleNamespace(id="s1")

        sq.add_ship(ship)
        sq.add_ship(ship)

        assert len(sq.ships) == 1

    def test_remove_ship_returns_true_when_present(self):
        sq = Squadron(name="Alpha")
        ship = SimpleNamespace(id="s1")
        sq.add_ship(ship)

        assert sq.remove_ship(ship) is True
        assert sq.ships == []

    def test_remove_ship_returns_false_when_absent(self):
        sq = Squadron(name="Alpha")
        ship = SimpleNamespace(id="s1")

        assert sq.remove_ship(ship) is False

    def test_all_ships_orders_members_then_lone_ships(self):
        sq = Squadron(name="Alpha")
        member = SimpleNamespace(id="member")
        lone = SimpleNamespace(id="lone")
        sq.add_ship(member)
        sq.add_lone_ship(lone)

        assert sq.all_ships == [member, lone]


class TestNodeId:
    """node_id auto-generation."""

    def test_default_node_id_is_unique_uuid(self):
        a = Squadron(name="Alpha")
        b = Squadron(name="Beta")

        assert a.node_id
        assert b.node_id
        assert a.node_id != b.node_id

    def test_explicit_node_id_is_preserved(self):
        sq = Squadron(name="Alpha", node_id="my-id")
        assert sq.node_id == "my-id"


class TestToDictDiscriminatorAndAsymmetry:
    """``to_dict`` includes 'type' = 'squadron' and omits empty/None
    spatial fields. PROJ-335 D-007: asymmetric serialization is the
    documented design."""

    def test_to_dict_includes_squadron_discriminator(self):
        sq = Squadron(name="Alpha")
        data = sq.to_dict()

        assert data["type"] == "squadron"

    def test_to_dict_omits_spatial_behavior_when_none(self):
        sq = Squadron(name="Alpha", spatial_behavior=None)
        data = sq.to_dict()

        assert "spatial_behavior" not in data

    def test_to_dict_omits_spatial_behavior_params_when_empty(self):
        sq = Squadron(name="Alpha", spatial_behavior_params={})
        data = sq.to_dict()

        assert "spatial_behavior_params" not in data

    def test_to_dict_includes_spatial_behavior_when_set(self):
        sq = Squadron(
            name="Alpha",
            spatial_behavior="formation",
            spatial_behavior_params={"slot": 1},
        )
        data = sq.to_dict()

        assert data["spatial_behavior"] == "formation"
        assert data["spatial_behavior_params"] == {"slot": 1}


class TestFromDictReconstruction:
    """``from_dict`` reconstructs a Squadron with field-equivalent state."""

    def test_round_trip_with_omitted_optional_fields(self):
        original = Squadron(name="Alpha", node_id="id-1")

        restored = Squadron.from_dict(original.to_dict())

        assert restored.name == "Alpha"
        assert restored.node_id == "id-1"
        # Field-by-field, not dict-by-dict (D-007): omitted optional
        # fields reconstruct with their constructor defaults.
        assert restored.spatial_behavior is None
        assert restored.spatial_behavior_params == {}

    def test_round_trip_with_battle_role_enum(self):
        original = Squadron(
            name="Alpha",
            node_id="id-1",
            battle_role=BattleRole.VANGUARD,
        )

        restored = Squadron.from_dict(original.to_dict())

        assert restored.battle_role == BattleRole.VANGUARD

    def test_round_trip_with_combat_policy(self):
        original = Squadron(
            name="Alpha",
            node_id="id-1",
            policy=CombatPolicy(targeting="aggressive", retreat="never"),
        )

        restored = Squadron.from_dict(original.to_dict())

        assert restored.policy.targeting == "aggressive"
        assert restored.policy.movement is None
        assert restored.policy.retreat == "never"

    def test_round_trip_preserves_spatial_behavior_when_set(self):
        original = Squadron(
            name="Alpha",
            node_id="id-1",
            spatial_behavior="formation",
            spatial_behavior_params={"slot": 1, "axis": "x"},
        )

        restored = Squadron.from_dict(original.to_dict())

        assert restored.spatial_behavior == "formation"
        assert restored.spatial_behavior_params == {"slot": 1, "axis": "x"}

    def test_round_trip_preserves_flagship_id(self):
        original = Squadron(
            name="Alpha",
            node_id="id-1",
            flagship_id="ship-99",
        )

        restored = Squadron.from_dict(original.to_dict())

        assert restored.flagship_id == "ship-99"


class TestFromDictMissingRequiredKeys:
    """PROJ-353 Tier-7 (T2.7): coverage gap.

    `Squadron.from_dict` requires `name`. Pin the missing-key behavior
    (KeyError, sister-class symmetry with Order/PlanetaryFacility) and
    extra-key tolerance.
    """

    def test_missing_name_raises_key_error(self):
        import pytest

        with pytest.raises(KeyError) as exc_info:
            Squadron.from_dict({})
        assert "name" in str(exc_info.value)

    def test_extra_keys_are_tolerated(self):
        """Loader must ignore unknown top-level keys for forward
        compatibility — older versions reading newer saves shouldn't
        fall over on a new optional field."""
        sq = Squadron.from_dict({
            "name": "Alpha",
            "node_id": "id-1",
            "_future_key": "x",
            "another_extra": 99,
        })
        assert sq.name == "Alpha"
        assert sq.node_id == "id-1"
