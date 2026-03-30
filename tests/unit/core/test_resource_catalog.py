"""
Tests for ResourceCatalog and ResourceDefinition.

Phase 1 of the Resource System Unification: Verify that the unified
ResourceCatalog loads all resource definitions from the expanded
data/resources.json and provides query methods for accessing them.
"""
import json
import pytest
from unittest.mock import patch

from game.core.resources import ResourceCatalog, ResourceDefinition


class TestResourceDefinition:
    """Tests for the ResourceDefinition frozen dataclass."""

    def test_creation(self):
        """Can create a ResourceDefinition with all fields."""
        defn = ResourceDefinition(
            id="metals",
            name="Metals",
            description="Refined metallic ores.",
            display_group="planetary",
            has_quality=True,
        )
        assert defn.id == "metals"
        assert defn.name == "Metals"
        assert defn.description == "Refined metallic ores."
        assert defn.display_group == "planetary"
        assert defn.has_quality is True

    def test_frozen(self):
        """ResourceDefinition is immutable."""
        defn = ResourceDefinition(
            id="fuel",
            name="Fuel",
            description="Powers engines.",
            display_group="operational",
            has_quality=False,
        )
        with pytest.raises(AttributeError):
            defn.id = "changed"

    def test_equality(self):
        """Two definitions with same fields are equal."""
        a = ResourceDefinition("fuel", "Fuel", "Desc", "operational", False)
        b = ResourceDefinition("fuel", "Fuel", "Desc", "operational", False)
        assert a == b

    def test_inequality(self):
        """Definitions with different fields are not equal."""
        a = ResourceDefinition("fuel", "Fuel", "Desc", "operational", False)
        b = ResourceDefinition("ammo", "Ammo", "Desc", "operational", False)
        assert a != b


class TestResourceCatalogFromJson:
    """Tests for loading ResourceCatalog from the actual data/resources.json."""

    def test_loads_all_eight_resources(self):
        """The expanded resources.json should contain all 8 resource definitions."""
        catalog = ResourceCatalog.from_json()
        ids = catalog.all_ids()
        assert len(ids) == 8
        for expected_id in ["metals", "organics", "vapors", "radioactives", "exotics",
                            "fuel", "energy", "ammo"]:
            assert expected_id in ids, f"Expected '{expected_id}' in catalog"

    def test_get_existing_resource(self):
        """get() returns the correct ResourceDefinition."""
        catalog = ResourceCatalog.from_json()
        metals = catalog.get("metals")
        assert metals is not None
        assert metals.id == "metals"
        assert metals.name == "Metals"
        assert metals.has_quality is True

    def test_get_nonexistent_resource(self):
        """get() returns None for unknown resource IDs."""
        catalog = ResourceCatalog.from_json()
        assert catalog.get("nonexistent") is None

    def test_has_existing(self):
        """has() returns True for existing resources."""
        catalog = ResourceCatalog.from_json()
        assert catalog.has("fuel") is True
        assert catalog.has("metals") is True

    def test_has_nonexistent(self):
        """has() returns False for unknown resources."""
        catalog = ResourceCatalog.from_json()
        assert catalog.has("dilithium") is False

    def test_planetary_display_group(self):
        """by_display_group('planetary') returns the 5 planet resources."""
        catalog = ResourceCatalog.from_json()
        planetary = catalog.by_display_group("planetary")
        planetary_ids = [r.id for r in planetary]
        assert set(planetary_ids) == {"metals", "organics", "vapors", "radioactives", "exotics"}

    def test_operational_display_group(self):
        """by_display_group('operational') returns the 3 ship resources."""
        catalog = ResourceCatalog.from_json()
        operational = catalog.by_display_group("operational")
        operational_ids = [r.id for r in operational]
        assert set(operational_ids) == {"fuel", "energy", "ammo"}

    def test_empty_display_group(self):
        """by_display_group() returns empty list for unknown groups."""
        catalog = ResourceCatalog.from_json()
        assert catalog.by_display_group("nonexistent") == []

    def test_all_definitions_returns_list(self):
        """all_definitions() returns a list of ResourceDefinition objects."""
        catalog = ResourceCatalog.from_json()
        defs = catalog.all_definitions()
        assert isinstance(defs, list)
        assert len(defs) == 8
        assert all(isinstance(d, ResourceDefinition) for d in defs)

    def test_has_quality_flag_correct(self):
        """Planetary resources have has_quality=True, operational have False."""
        catalog = ResourceCatalog.from_json()
        for res_id in ["metals", "organics", "vapors", "radioactives", "exotics"]:
            assert catalog.get(res_id).has_quality is True, f"{res_id} should have quality"
        for res_id in ["fuel", "energy", "ammo"]:
            assert catalog.get(res_id).has_quality is False, f"{res_id} should not have quality"

    def test_definitions_are_frozen(self):
        """Returned definitions cannot be mutated."""
        catalog = ResourceCatalog.from_json()
        defn = catalog.get("metals")
        with pytest.raises(AttributeError):
            defn.name = "Changed"

    def test_all_ids_returns_list_of_strings(self):
        """all_ids() returns a list of string IDs."""
        catalog = ResourceCatalog.from_json()
        ids = catalog.all_ids()
        assert isinstance(ids, list)
        assert all(isinstance(i, str) for i in ids)


class TestResourceCatalogFromData:
    """Tests for building ResourceCatalog from in-memory data (for testing/modding)."""

    def test_from_data_list(self):
        """Can create catalog from a list of resource dicts."""
        data = [
            {"id": "dilithium", "name": "Dilithium", "description": "Rare crystal.",
             "display_group": "exotic", "has_quality": True},
            {"id": "plasma", "name": "Plasma", "description": "Ionized gas.",
             "display_group": "exotic", "has_quality": False},
        ]
        catalog = ResourceCatalog.from_data(data)
        assert catalog.has("dilithium")
        assert catalog.has("plasma")
        assert len(catalog.all_ids()) == 2

    def test_from_data_preserves_fields(self):
        """from_data() correctly maps all fields."""
        data = [
            {"id": "test_res", "name": "Test", "description": "A test resource.",
             "display_group": "test_group", "has_quality": True},
        ]
        catalog = ResourceCatalog.from_data(data)
        defn = catalog.get("test_res")
        assert defn.name == "Test"
        assert defn.description == "A test resource."
        assert defn.display_group == "test_group"
        assert defn.has_quality is True

    def test_from_data_defaults(self):
        """from_data() applies sensible defaults for missing optional fields."""
        data = [{"id": "minimal", "name": "Minimal"}]
        catalog = ResourceCatalog.from_data(data)
        defn = catalog.get("minimal")
        assert defn.description == ""
        assert defn.display_group == ""
        assert defn.has_quality is False

    def test_custom_resource_with_json_file(self, tmp_path):
        """Can load a custom resources.json with modded resources."""
        custom_data = {
            "resources": [
                {"id": "dilithium", "name": "Dilithium", "description": "Rare crystal.",
                 "display_group": "exotic", "has_quality": True},
                {"id": "fuel", "name": "Fuel", "description": "Powers engines.",
                 "display_group": "operational", "has_quality": False},
            ]
        }
        json_file = tmp_path / "resources.json"
        json_file.write_text(json.dumps(custom_data))

        catalog = ResourceCatalog.from_json(str(json_file))
        assert catalog.has("dilithium")
        assert catalog.has("fuel")
        assert len(catalog.all_ids()) == 2


class TestResourceCatalogEdgeCases:
    """Edge case tests for ResourceCatalog."""

    def test_empty_catalog(self):
        """Can create an empty catalog."""
        catalog = ResourceCatalog.from_data([])
        assert catalog.all_ids() == []
        assert catalog.all_definitions() == []
        assert catalog.get("anything") is None
        assert catalog.has("anything") is False

    def test_duplicate_ids_last_wins(self):
        """Duplicate IDs: last definition wins."""
        data = [
            {"id": "dupe", "name": "First"},
            {"id": "dupe", "name": "Second"},
        ]
        catalog = ResourceCatalog.from_data(data)
        assert catalog.get("dupe").name == "Second"
        assert len(catalog.all_ids()) == 1

    def test_resource_without_id_skipped(self):
        """Resources without id field are skipped."""
        data = [
            {"name": "No ID"},
            {"id": "valid", "name": "Valid"},
        ]
        catalog = ResourceCatalog.from_data(data)
        assert len(catalog.all_ids()) == 1
        assert catalog.has("valid")

    def test_resource_with_empty_id_skipped(self):
        """Resources with empty string id are skipped."""
        data = [
            {"id": "", "name": "Empty"},
            {"id": "valid", "name": "Valid"},
        ]
        catalog = ResourceCatalog.from_data(data)
        assert len(catalog.all_ids()) == 1

    def test_resource_with_none_id_skipped(self):
        """Resources with None id are skipped."""
        data = [
            {"id": None, "name": "Null"},
            {"id": "valid", "name": "Valid"},
        ]
        catalog = ResourceCatalog.from_data(data)
        assert len(catalog.all_ids()) == 1

    def test_catalog_is_not_mutated_by_all_ids(self):
        """Mutating the list from all_ids() doesn't affect the catalog."""
        data = [{"id": "test", "name": "Test"}]
        catalog = ResourceCatalog.from_data(data)
        ids = catalog.all_ids()
        ids.append("injected")
        assert "injected" not in catalog.all_ids()

    def test_catalog_is_not_mutated_by_all_definitions(self):
        """Mutating the list from all_definitions() doesn't affect the catalog."""
        data = [{"id": "test", "name": "Test"}]
        catalog = ResourceCatalog.from_data(data)
        defs = catalog.all_definitions()
        defs.clear()
        assert len(catalog.all_definitions()) == 1
