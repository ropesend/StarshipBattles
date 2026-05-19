"""
PROJ-436 Phase 0: tests for the unified Container substrate.

Covers:
- ContainableKind enum
- ContainerPolicy dataclass
- Container three-slice model (resources / items / population)
- Mass-cap accounting across all three slices
- Policy filtering (accepts())
- add() / remove() returning AddResult / RemoveResult
- to_dict() / from_dict() round-trip
- contents() unified read view
"""
from __future__ import annotations

import pytest

from game.strategy.data.container import (
    AddResult,
    Container,
    ContainerPolicy,
    RemoveResult,
)
from game.strategy.data.containable import (
    ContainableKind,
    ItemContainable,
    ItemRef,
    PopulationContainable,
    ResourceContainable,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _any_policy() -> ContainerPolicy:
    """Policy accepting any kind / any type id."""
    return ContainerPolicy(
        allowed_kinds=frozenset({
            ContainableKind.RESOURCE,
            ContainableKind.ITEM,
            ContainableKind.POPULATION,
        }),
        allowed_type_ids=None,
    )


def _metals() -> ResourceContainable:
    return ResourceContainable("metals")


def _energy() -> ResourceContainable:
    return ResourceContainable("energy")


def _human() -> PopulationContainable:
    return PopulationContainable("human")


def _fighter(design_id: str = "qs_fighter", instance_id: str = "i-1", mass: float = 100.0) -> ItemContainable:
    return ItemContainable(ItemRef(design_id=design_id, instance_id=instance_id, mass=mass))


# ---------------------------------------------------------------------------
# Empty / construction
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_empty_container_mass_used_zero(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        assert c.mass_used == 0.0
        assert c.mass_remaining == 100.0

    def test_empty_container_contents_empty(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        assert tuple(c.contents()) == ()

    def test_capacity_mass_must_be_non_negative(self):
        with pytest.raises(ValueError):
            Container(capacity_mass=-1.0, policy=_any_policy())


# ---------------------------------------------------------------------------
# Resource slice
# ---------------------------------------------------------------------------


class TestResourceSlice:
    def test_add_resource_updates_mass_used(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        result = c.add(_metals(), 500.0)  # 500 * 0.01 = 5.0 mass
        assert result is AddResult.OK
        assert c.mass_used == pytest.approx(5.0)
        assert c.mass_remaining == pytest.approx(95.0)
        assert c.get_resource("metals") == pytest.approx(500.0)

    def test_add_resource_accumulates(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        c.add(_metals(), 100.0)
        c.add(_metals(), 200.0)
        assert c.get_resource("metals") == pytest.approx(300.0)

    def test_add_resource_energy_uses_user_directive_mass(self):
        # energy mass_per_unit = 1.0 per user directive
        c = Container(capacity_mass=10.0, policy=_any_policy())
        result = c.add(_energy(), 5.0)
        assert result is AddResult.OK
        assert c.mass_used == pytest.approx(5.0)

    def test_remove_resource(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        c.add(_metals(), 500.0)
        result = c.remove(_metals(), 200.0)
        assert result is RemoveResult.OK
        assert c.get_resource("metals") == pytest.approx(300.0)
        assert c.mass_used == pytest.approx(3.0)

    def test_remove_resource_not_enough(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        c.add(_metals(), 100.0)
        result = c.remove(_metals(), 500.0)
        assert result is RemoveResult.NOT_ENOUGH
        assert c.get_resource("metals") == pytest.approx(100.0)  # unchanged

    def test_get_resource_missing_returns_zero(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        assert c.get_resource("organics") == 0.0

    def test_remove_rejects_negative_resource_quantity(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        c.add(_metals(), 500.0)
        with pytest.raises(ValueError, match="non-negative"):
            c.remove(_metals(), -3.0)

    def test_remove_does_not_grow_storage_on_negative_quantity(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        c.add(_metals(), 500.0)
        with pytest.raises(ValueError):
            c.remove(_metals(), -3.0)
        assert c.get_resource("metals") == pytest.approx(500.0)


# ---------------------------------------------------------------------------
# Items slice
# ---------------------------------------------------------------------------


class TestItemsSlice:
    def test_add_item(self):
        c = Container(capacity_mass=1000.0, policy=_any_policy())
        f = _fighter(mass=100.0)
        result = c.add(f, 1)
        assert result is AddResult.OK
        assert c.mass_used == pytest.approx(100.0)
        items = c.get_items()
        assert len(items) == 1
        assert items[0].design_id == "qs_fighter"

    def test_add_multiple_items_with_identity(self):
        c = Container(capacity_mass=1000.0, policy=_any_policy())
        c.add(_fighter("qs_fighter", "i-1", 100.0), 1)
        c.add(_fighter("qs_fighter", "i-2", 100.0), 1)
        c.add(_fighter("qs_satellite", "s-1", 50.0), 1)
        items = c.get_items()
        assert len(items) == 3
        assert {it.instance_id for it in items} == {"i-1", "i-2", "s-1"}
        assert c.mass_used == pytest.approx(250.0)

    def test_remove_item_by_instance_id(self):
        c = Container(capacity_mass=1000.0, policy=_any_policy())
        c.add(_fighter("qs_fighter", "i-1", 100.0), 1)
        c.add(_fighter("qs_fighter", "i-2", 100.0), 1)
        target = ItemContainable(ItemRef("qs_fighter", "i-1", 100.0))
        result = c.remove(target, 1)
        assert result is RemoveResult.OK
        assert len(c.get_items()) == 1
        assert c.get_items()[0].instance_id == "i-2"

    def test_remove_item_not_found(self):
        c = Container(capacity_mass=1000.0, policy=_any_policy())
        c.add(_fighter("qs_fighter", "i-1", 100.0), 1)
        target = ItemContainable(ItemRef("qs_fighter", "missing", 100.0))
        result = c.remove(target, 1)
        assert result is RemoveResult.NOT_ENOUGH

    def test_add_item_quantity_must_be_one(self):
        c = Container(capacity_mass=1000.0, policy=_any_policy())
        with pytest.raises(ValueError):
            c.add(_fighter(mass=100.0), 2)


# ---------------------------------------------------------------------------
# Population slice
# ---------------------------------------------------------------------------


class TestPopulationSlice:
    def test_add_population_uses_user_directive_mass(self):
        # 10 individuals per ton == 0.1 mass per individual per user directive
        c = Container(capacity_mass=100.0, policy=_any_policy())
        result = c.add(_human(), 500)
        assert result is AddResult.OK
        assert c.mass_used == pytest.approx(50.0)
        assert c.get_population("human") == 500

    def test_population_count_must_be_integer(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        with pytest.raises(TypeError):
            c.add(_human(), 5.5)

    def test_population_per_species(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        c.add(_human(), 100)
        c.add(PopulationContainable("vulcan"), 50)
        assert c.get_population("human") == 100
        assert c.get_population("vulcan") == 50

    def test_remove_population(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        c.add(_human(), 500)
        result = c.remove(_human(), 200)
        assert result is RemoveResult.OK
        assert c.get_population("human") == 300

    def test_remove_population_not_enough(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        c.add(_human(), 100)
        result = c.remove(_human(), 200)
        assert result is RemoveResult.NOT_ENOUGH
        assert c.get_population("human") == 100

    def test_remove_rejects_negative_population_quantity(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        c.add(_human(), 100)
        with pytest.raises(ValueError, match="non-negative"):
            c.remove(_human(), -2)


# ---------------------------------------------------------------------------
# Mixed slices share the mass cap
# ---------------------------------------------------------------------------


class TestSharedMassCap:
    def test_three_slice_mass_total(self):
        c = Container(capacity_mass=1000.0, policy=_any_policy())
        c.add(_metals(), 1000.0)  # 10.0 mass
        c.add(_fighter(mass=100.0), 1)  # 100.0 mass
        c.add(_human(), 100)  # 10.0 mass
        assert c.mass_used == pytest.approx(120.0)

    def test_capacity_exceeded_rejects(self):
        c = Container(capacity_mass=10.0, policy=_any_policy())
        c.add(_metals(), 500.0)  # 5.0 mass
        result = c.add(_metals(), 1000.0)  # would add 10.0, exceed cap
        assert result is AddResult.REJECTED_CAPACITY
        assert c.get_resource("metals") == pytest.approx(500.0)  # unchanged

    def test_capacity_exactly_full_accepts(self):
        c = Container(capacity_mass=10.0, policy=_any_policy())
        result = c.add(_metals(), 1000.0)  # exactly 10.0 mass
        assert result is AddResult.OK
        assert c.mass_remaining == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Policy filtering
# ---------------------------------------------------------------------------


class TestPolicy:
    def test_kind_filter_rejects(self):
        policy = ContainerPolicy(
            allowed_kinds=frozenset({ContainableKind.RESOURCE}),
            allowed_type_ids=None,
        )
        c = Container(capacity_mass=100.0, policy=policy)
        result = c.add(_fighter(mass=10.0), 1)
        assert result is AddResult.REJECTED_POLICY
        assert len(c.get_items()) == 0

    def test_kind_filter_accepts_allowed(self):
        policy = ContainerPolicy(
            allowed_kinds=frozenset({ContainableKind.RESOURCE}),
            allowed_type_ids=None,
        )
        c = Container(capacity_mass=100.0, policy=policy)
        result = c.add(_metals(), 100.0)
        assert result is AddResult.OK

    def test_type_id_filter_rejects(self):
        policy = ContainerPolicy(
            allowed_kinds=frozenset({ContainableKind.RESOURCE}),
            allowed_type_ids=frozenset({"metals"}),
        )
        c = Container(capacity_mass=100.0, policy=policy)
        result = c.add(_energy(), 5.0)
        assert result is AddResult.REJECTED_POLICY

    def test_type_id_filter_accepts(self):
        policy = ContainerPolicy(
            allowed_kinds=frozenset({ContainableKind.RESOURCE}),
            allowed_type_ids=frozenset({"metals"}),
        )
        c = Container(capacity_mass=100.0, policy=policy)
        result = c.add(_metals(), 100.0)
        assert result is AddResult.OK

    def test_accepts_returns_bool(self):
        policy = ContainerPolicy(
            allowed_kinds=frozenset({ContainableKind.RESOURCE}),
            allowed_type_ids=frozenset({"metals"}),
        )
        c = Container(capacity_mass=100.0, policy=policy)
        assert c.accepts(_metals()) is True
        assert c.accepts(_energy()) is False
        assert c.accepts(_fighter(mass=10.0)) is False


# ---------------------------------------------------------------------------
# Unified contents() read
# ---------------------------------------------------------------------------


class TestContents:
    def test_contents_yields_all_three_slices(self):
        c = Container(capacity_mass=1000.0, policy=_any_policy())
        c.add(_metals(), 500.0)
        c.add(_fighter(mass=100.0), 1)
        c.add(_human(), 100)
        entries = tuple(c.contents())
        kinds = {e.kind for e in entries}
        assert kinds == {
            ContainableKind.RESOURCE,
            ContainableKind.ITEM,
            ContainableKind.POPULATION,
        }

    def test_contents_entry_carries_mass_total(self):
        c = Container(capacity_mass=1000.0, policy=_any_policy())
        c.add(_metals(), 1000.0)  # 10.0 mass
        entries = [e for e in c.contents() if e.kind is ContainableKind.RESOURCE]
        assert len(entries) == 1
        assert entries[0].type_id == "metals"
        assert entries[0].quantity == pytest.approx(1000.0)
        assert entries[0].mass_total == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_empty_round_trip(self):
        c = Container(capacity_mass=100.0, policy=_any_policy())
        data = c.to_dict()
        rebuilt = Container.from_dict(data)
        assert rebuilt.capacity_mass == c.capacity_mass
        assert rebuilt.mass_used == 0.0

    def test_three_slice_round_trip(self):
        c = Container(capacity_mass=1000.0, policy=_any_policy())
        c.add(_metals(), 500.0)
        c.add(_fighter("qs_fighter", "i-1", 100.0), 1)
        c.add(_human(), 200)
        data = c.to_dict()
        rebuilt = Container.from_dict(data)
        assert rebuilt.get_resource("metals") == pytest.approx(500.0)
        assert rebuilt.get_population("human") == 200
        items = rebuilt.get_items()
        assert len(items) == 1
        assert items[0].instance_id == "i-1"
        assert items[0].mass == pytest.approx(100.0)
        assert rebuilt.mass_used == pytest.approx(c.mass_used)

    def test_policy_round_trip(self):
        policy = ContainerPolicy(
            allowed_kinds=frozenset({ContainableKind.RESOURCE}),
            allowed_type_ids=frozenset({"metals", "fuel"}),
        )
        c = Container(capacity_mass=100.0, policy=policy)
        data = c.to_dict()
        rebuilt = Container.from_dict(data)
        assert rebuilt.policy.allowed_kinds == frozenset({ContainableKind.RESOURCE})
        assert rebuilt.policy.allowed_type_ids == frozenset({"metals", "fuel"})
