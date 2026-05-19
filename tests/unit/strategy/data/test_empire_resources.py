"""Tests for Empire resource pool functionality (PROJ-75 Phase 1).

PROJ-436 Phase 5 rewrite: the legacy ``_fleet_resource_pool`` durable
storage and the ``Empire.add_resources`` / ``Empire.consume_resources``
mutators that wrote against it have been deleted. ``Empire.resource_pool``
is now a pure aggregation query over ``self.colonies[*].stockpile``.
The retained read APIs (``resource_pool`` / ``has_resources`` /
``get_resource``) are tested through colony seeding.
"""
import pytest

from game.strategy.data.empire import Empire
from tests.fixtures.strategy_entities import create_test_planet


@pytest.fixture
def empire():
    """Create a basic empire for testing."""
    return Empire(empire_id=1, name="Test Empire", color=(255, 0, 0))


def _seed_colony(empire: Empire, stockpile: dict, *, name: str = "Colony") -> None:
    """Attach a colony with the given stockpile to the empire.

    PROJ-436 Phase 5: tests seed the resource pool by writing to a
    colony's stockpile, since the legacy fleet-side ``_fleet_resource_pool``
    has been deleted.
    """
    colony = create_test_planet(
        has_facilities=False,
        has_population=False,
        name=name,
        _stockpile=dict(stockpile),
    )
    empire.colonies.append(colony)


class TestEmpireResourcePoolInit:
    """Test resource pool initialization."""

    def test_resource_pool_initializes_as_empty_dict(self, empire):
        assert empire.resource_pool == {}

    def test_max_storage_initializes_as_empty_dict(self, empire):
        assert empire.max_storage == {}


class TestHasResources:
    """Test has_resources() reads the aggregated resource_pool."""

    def test_has_resources_single_type_sufficient(self, empire):
        _seed_colony(empire, {"metals": 500.0})
        assert empire.has_resources({"metals": 300.0}) is True

    def test_has_resources_single_type_insufficient(self, empire):
        _seed_colony(empire, {"metals": 100.0})
        assert empire.has_resources({"metals": 300.0}) is False

    def test_has_resources_multiple_types_all_sufficient(self, empire):
        _seed_colony(empire, {"metals": 500.0, "organics": 300.0})
        assert empire.has_resources({"metals": 200.0, "organics": 100.0}) is True

    def test_has_resources_multiple_types_one_insufficient(self, empire):
        """Returns False if ANY resource is insufficient."""
        _seed_colony(empire, {"metals": 500.0, "organics": 50.0})
        assert empire.has_resources({"metals": 200.0, "organics": 100.0}) is False

    def test_has_resources_empty_costs(self, empire):
        """Empty costs dict always returns True."""
        assert empire.has_resources({}) is True

    def test_has_resources_missing_type(self, empire):
        """Missing resource type treated as 0."""
        assert empire.has_resources({"metals": 100.0}) is False


class TestGetResource:
    """Test get_resource() reads the aggregated resource_pool."""

    def test_get_resource_existing(self, empire):
        _seed_colony(empire, {"metals": 500.0})
        assert empire.get_resource("metals") == 500.0

    def test_get_resource_missing_returns_zero(self, empire):
        assert empire.get_resource("metals") == 0.0


class TestEmpireResourceSerialization:
    """Test to_dict/from_dict for resource fields.

    PROJ-436 Phase 5: ``resource_pool`` is no longer a serialised
    durable shape — it derives from ``self.colonies[*].stockpile``.
    Only ``max_storage`` remains as a serialised top-level resource
    field on the Empire.
    """

    def test_to_dict_does_not_emit_resource_pool_key(self, empire):
        """PROJ-436 Phase 5: the empire-level ``resource_pool`` key is gone."""
        data = empire.to_dict()
        assert "resource_pool" not in data

    def test_to_dict_includes_max_storage(self, empire):
        empire.max_storage = {"metals": 10000.0}
        data = empire.to_dict()
        assert data["max_storage"] == {"metals": 10000.0}

    def test_from_dict_restores_max_storage(self, empire):
        empire.max_storage = {"metals": 10000.0}
        data = empire.to_dict()

        restored = Empire.from_dict(data)
        assert restored.max_storage == {"metals": 10000.0}
        # PROJ-436 Phase 5: with no colonies, resource_pool is empty
        # (no fleet-side pool exists anymore to back it).
        assert restored.resource_pool == {}

    def test_from_dict_handles_missing_fields(self):
        """Old saves without resource fields get safe defaults."""
        data = {
            "id": 1,
            "name": "Old Empire",
            "color": [255, 0, 0],
        }
        restored = Empire.from_dict(data)
        assert restored.resource_pool == {}
        assert restored.max_storage == {}

    def test_from_dict_ignores_legacy_resource_pool_key(self):
        """PROJ-436 Phase 5: pre-Phase-5 saves that carry the legacy
        ``resource_pool`` top-level key are silently ignored.

        Per CLAUDE.md "no save-file migration" rule old saves are
        disposable — the new save shape simply omits the key, and
        ``from_dict`` does not resurrect the deleted field.
        """
        data = {
            "id": 1,
            "name": "Legacy",
            "color": [255, 0, 0],
            "resource_pool": {"metals": 999.0},  # legacy pre-Phase-5 shape
        }
        restored = Empire.from_dict(data)
        # The legacy key is dropped; with no colonies the aggregate is empty.
        assert restored.resource_pool == {}
        assert not hasattr(restored, "_fleet_resource_pool"), (
            "PROJ-436 Phase 5: legacy `_fleet_resource_pool` must not "
            "be resurrected from old saves."
        )

    def test_to_dict_empty_storage(self, empire):
        """Empty max_storage is still serialized."""
        data = empire.to_dict()
        assert data["max_storage"] == {}


class TestResourcePoolPureAggregation:
    """Test that resource_pool is a pure computed aggregate of colony stockpiles.

    PROJ-436 Phase 5: ``resource_pool`` walks ``self.colonies[*].stockpile``
    only — there is no longer a fleet-side summand.
    """

    def test_resource_pool_sums_colony_stockpiles(self):
        """resource_pool returns sum of all colony stockpiles."""
        empire = Empire(empire_id=1, name="Test", color=(255, 0, 0))
        colony1 = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 100.0, "organics": 50.0},
        )
        colony2 = create_test_planet(
            has_facilities=False, has_population=False,
            name="Colony2",
            _stockpile={"metals": 200.0, "fuel": 30.0},
        )
        empire.colonies = [colony1, colony2]

        pool = empire.resource_pool
        assert pool["metals"] == pytest.approx(300.0)
        assert pool["organics"] == pytest.approx(50.0)
        assert pool["fuel"] == pytest.approx(30.0)

    def test_resource_pool_empty_with_no_colonies(self):
        """resource_pool returns empty dict with no colonies."""
        empire = Empire(empire_id=1, name="Test", color=(255, 0, 0))
        assert empire.resource_pool == {}

    def test_resource_pool_is_not_mutable(self):
        """Mutating the returned dict doesn't affect the empire."""
        empire = Empire(empire_id=1, name="Test", color=(255, 0, 0))
        _seed_colony(empire, {"metals": 100.0})

        pool = empire.resource_pool
        pool["metals"] = 999.0  # Mutate the returned dict

        # Should not affect the actual aggregate
        assert empire.resource_pool["metals"] == 100.0

    def test_resource_pool_has_no_fleet_side_durable_state(self):
        """PROJ-436 Phase 5 deletion guard at the data-class boundary.

        Constructing a fresh Empire does not produce a fleet-side
        resource pool attribute; the aggregate over zero colonies is
        empty. This complements the static-guard test in
        ``tests/static_guards/test_no_legacy_storage_fields.py``.
        """
        empire = Empire(empire_id=1, name="Test", color=(255, 0, 0))
        assert "_fleet_resource_pool" not in vars(empire)
        assert empire.resource_pool == {}
