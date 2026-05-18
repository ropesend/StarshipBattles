"""
PROJ-436 Phase 0: tests for the `mass_per_unit` field added to
`ResourceDefinition` and the `ResourceCatalog.get_mass_per_unit()`
accessor.

The extension is additive: existing ResourceCatalog behaviour and
the eight canonical resources in data/resources.json are unchanged
except for one new field per entry.
"""
from __future__ import annotations

import pytest

from game.core.resources import ResourceCatalog, ResourceDefinition


class TestResourceDefinitionField:
    def test_mass_per_unit_default(self):
        defn = ResourceDefinition(
            id="custom",
            name="Custom",
            description="",
            display_group="",
            has_quality=False,
        )
        # Sensible default keeps backward compatibility with code that
        # constructs ResourceDefinition without the new field.
        assert defn.mass_per_unit == 1.0

    def test_mass_per_unit_explicit(self):
        defn = ResourceDefinition(
            id="metals",
            name="Metals",
            description="",
            display_group="",
            has_quality=True,
            mass_per_unit=0.01,
        )
        assert defn.mass_per_unit == 0.01

    def test_mass_per_unit_in_equality(self):
        a = ResourceDefinition("x", "X", "", "", False, mass_per_unit=0.5)
        b = ResourceDefinition("x", "X", "", "", False, mass_per_unit=0.5)
        c = ResourceDefinition("x", "X", "", "", False, mass_per_unit=0.7)
        assert a == b
        assert a != c

    def test_mass_per_unit_still_frozen(self):
        defn = ResourceDefinition("x", "X", "", "", False, mass_per_unit=0.5)
        with pytest.raises((AttributeError, TypeError)):
            defn.mass_per_unit = 99.0  # type: ignore[misc]


class TestCanonicalCatalogValues:
    """The 8 entries in data/resources.json land per the user directive."""

    def test_energy_one_ton(self):
        # Per user directive: 1 unit of energy = 1 ton.
        catalog = ResourceCatalog.from_json()
        assert catalog.get_mass_per_unit("energy") == pytest.approx(1.0)

    def test_metals(self):
        catalog = ResourceCatalog.from_json()
        assert catalog.get_mass_per_unit("metals") == pytest.approx(0.01)

    def test_organics(self):
        catalog = ResourceCatalog.from_json()
        assert catalog.get_mass_per_unit("organics") == pytest.approx(0.01)

    def test_vapors(self):
        catalog = ResourceCatalog.from_json()
        assert catalog.get_mass_per_unit("vapors") == pytest.approx(0.001)

    def test_radioactives(self):
        catalog = ResourceCatalog.from_json()
        assert catalog.get_mass_per_unit("radioactives") == pytest.approx(0.005)

    def test_exotics(self):
        catalog = ResourceCatalog.from_json()
        assert catalog.get_mass_per_unit("exotics") == pytest.approx(0.001)

    def test_fuel(self):
        catalog = ResourceCatalog.from_json()
        assert catalog.get_mass_per_unit("fuel") == pytest.approx(0.0001)

    def test_ammo(self):
        catalog = ResourceCatalog.from_json()
        assert catalog.get_mass_per_unit("ammo") == pytest.approx(0.001)


class TestGetMassPerUnitAccessor:
    def test_unknown_resource_raises(self):
        catalog = ResourceCatalog.from_json()
        with pytest.raises(KeyError):
            catalog.get_mass_per_unit("dilithium")

    def test_from_data_default(self):
        """from_data() entries without `mass_per_unit` default to 1.0."""
        data = [{"id": "minimal", "name": "Minimal"}]
        catalog = ResourceCatalog.from_data(data)
        assert catalog.get_mass_per_unit("minimal") == 1.0

    def test_from_data_explicit(self):
        data = [{"id": "fancy", "name": "Fancy", "mass_per_unit": 0.42}]
        catalog = ResourceCatalog.from_data(data)
        assert catalog.get_mass_per_unit("fancy") == pytest.approx(0.42)

    def test_definition_field_populated_from_data(self):
        data = [{"id": "fancy", "name": "Fancy", "mass_per_unit": 0.42}]
        catalog = ResourceCatalog.from_data(data)
        assert catalog.get("fancy").mass_per_unit == pytest.approx(0.42)


class TestCanonicalUnchangedFields:
    """The canonical catalog entries keep their other fields after extension."""

    def test_metals_name_and_quality(self):
        catalog = ResourceCatalog.from_json()
        metals = catalog.get("metals")
        assert metals.name == "Metals"
        assert metals.has_quality is True
        assert metals.display_group == "planetary"

    def test_energy_name_and_quality(self):
        catalog = ResourceCatalog.from_json()
        energy = catalog.get("energy")
        assert energy.name == "Energy"
        assert energy.has_quality is False
        assert energy.display_group == "operational"

    def test_full_resource_count(self):
        catalog = ResourceCatalog.from_json()
        assert len(catalog.all_ids()) == 8
