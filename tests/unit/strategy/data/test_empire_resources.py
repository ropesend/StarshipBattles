"""Tests for Empire resource pool functionality (PROJ-75 Phase 1)."""
import pytest

from game.strategy.data.empire import Empire


@pytest.fixture
def empire():
    """Create a basic empire for testing."""
    return Empire(empire_id=1, name="Test Empire", color=(255, 0, 0))


class TestEmpireResourcePoolInit:
    """Test resource pool initialization."""

    def test_resource_pool_initializes_as_empty_dict(self, empire):
        assert empire.resource_pool == {}

    def test_max_storage_initializes_as_empty_dict(self, empire):
        assert empire.max_storage == {}


class TestAddResources:
    """Test add_resources() method."""

    def test_add_resources_basic(self, empire):
        """Adding resources increases the pool."""
        overflow = empire.add_resources("metals", 500.0)
        assert empire.resource_pool["metals"] == 500.0
        assert overflow == 0.0

    def test_add_resources_accumulates(self, empire):
        """Multiple additions accumulate."""
        empire.add_resources("metals", 300.0)
        empire.add_resources("metals", 200.0)
        assert empire.resource_pool["metals"] == 500.0

    def test_add_resources_respects_max_storage(self, empire):
        """Adding beyond max_storage caps and returns overflow."""
        empire.max_storage["metals"] = 1000.0
        overflow = empire.add_resources("metals", 1200.0)
        assert empire.resource_pool["metals"] == 1000.0
        assert overflow == 200.0

    def test_add_resources_respects_max_storage_with_existing(self, empire):
        """Overflow calculated correctly with existing stock."""
        empire.max_storage["metals"] = 1000.0
        empire.add_resources("metals", 800.0)
        overflow = empire.add_resources("metals", 400.0)
        assert empire.resource_pool["metals"] == 1000.0
        assert overflow == 200.0

    def test_add_resources_no_max_storage_means_unlimited(self, empire):
        """No max_storage entry means unlimited capacity."""
        overflow = empire.add_resources("metals", 999999.0)
        assert empire.resource_pool["metals"] == 999999.0
        assert overflow == 0.0

    def test_add_resources_multiple_types(self, empire):
        """Different resource types are independent."""
        empire.add_resources("metals", 100.0)
        empire.add_resources("organics", 200.0)
        assert empire.resource_pool["metals"] == 100.0
        assert empire.resource_pool["organics"] == 200.0


class TestConsumeResources:
    """Test consume_resources() method."""

    def test_consume_resources_success(self, empire):
        """Successful consumption deducts and returns True."""
        empire._fleet_resource_pool["metals"] = 500.0
        result = empire.consume_resources("metals", 200.0)
        assert result is True
        assert empire.resource_pool.get("metals", 0.0) == 300.0

    def test_consume_resources_failure_insufficient(self, empire):
        """Insufficient resources returns False, no deduction."""
        empire._fleet_resource_pool["metals"] = 100.0
        result = empire.consume_resources("metals", 200.0)
        assert result is False
        assert empire.resource_pool.get("metals", 0.0) == 100.0

    def test_consume_resources_exact_amount(self, empire):
        """Consuming exactly available amount succeeds."""
        empire._fleet_resource_pool["metals"] = 500.0
        result = empire.consume_resources("metals", 500.0)
        assert result is True
        assert empire.resource_pool.get("metals", 0.0) == 0.0

    def test_consume_resources_missing_type(self, empire):
        """Consuming a type not in pool fails."""
        result = empire.consume_resources("metals", 100.0)
        assert result is False

    def test_consume_resources_partial_not_allowed(self, empire):
        """All-or-nothing: partial consumption not performed."""
        empire._fleet_resource_pool["metals"] = 50.0
        result = empire.consume_resources("metals", 100.0)
        assert result is False
        assert empire.resource_pool.get("metals", 0.0) == 50.0


class TestHasResources:
    """Test has_resources() method."""

    def test_has_resources_single_type_sufficient(self, empire):
        empire._fleet_resource_pool["metals"] = 500.0
        assert empire.has_resources({"metals": 300.0}) is True

    def test_has_resources_single_type_insufficient(self, empire):
        empire._fleet_resource_pool["metals"] = 100.0
        assert empire.has_resources({"metals": 300.0}) is False

    def test_has_resources_multiple_types_all_sufficient(self, empire):
        empire._fleet_resource_pool["metals"] = 500.0
        empire._fleet_resource_pool["organics"] = 300.0
        assert empire.has_resources({"metals": 200.0, "organics": 100.0}) is True

    def test_has_resources_multiple_types_one_insufficient(self, empire):
        """Returns False if ANY resource is insufficient."""
        empire._fleet_resource_pool["metals"] = 500.0
        empire._fleet_resource_pool["organics"] = 50.0
        assert empire.has_resources({"metals": 200.0, "organics": 100.0}) is False

    def test_has_resources_empty_costs(self, empire):
        """Empty costs dict always returns True."""
        assert empire.has_resources({}) is True

    def test_has_resources_missing_type(self, empire):
        """Missing resource type treated as 0."""
        assert empire.has_resources({"metals": 100.0}) is False


class TestGetResource:
    """Test get_resource() method."""

    def test_get_resource_existing(self, empire):
        empire._fleet_resource_pool["metals"] = 500.0
        assert empire.get_resource("metals") == 500.0

    def test_get_resource_missing_returns_zero(self, empire):
        assert empire.get_resource("metals") == 0.0


class TestEmpireResourceSerialization:
    """Test to_dict/from_dict for resource fields."""

    def test_to_dict_includes_resource_pool(self, empire):
        empire.resource_pool = {"metals": 500.0, "organics": 200.0}
        data = empire.to_dict()
        assert data["resource_pool"] == {"metals": 500.0, "organics": 200.0}

    def test_to_dict_includes_max_storage(self, empire):
        empire.max_storage = {"metals": 10000.0}
        data = empire.to_dict()
        assert data["max_storage"] == {"metals": 10000.0}

    def test_from_dict_restores_resource_pool(self, empire):
        empire.resource_pool = {"metals": 500.0, "radioactives": 100.0}
        empire.max_storage = {"metals": 10000.0}
        data = empire.to_dict()

        restored = Empire.from_dict(data)
        assert restored.resource_pool == {"metals": 500.0, "radioactives": 100.0}
        assert restored.max_storage == {"metals": 10000.0}

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

    def test_to_dict_empty_pools(self, empire):
        """Empty pools are still serialized."""
        data = empire.to_dict()
        assert data["resource_pool"] == {}
        assert data["max_storage"] == {}
