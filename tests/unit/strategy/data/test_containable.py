"""
PROJ-436 Phase 0: tests for `Containable` variants and how the
unified Container substrate resolves mass-per-unit through the
existing Core-layer `ResourceCatalog`, design metadata, and the
population species default.
"""
from __future__ import annotations

import pytest

from game.core.resources import ResourceCatalog
from game.strategy.data.container import (
    AddResult,
    Container,
    ContainerPolicy,
    set_resource_catalog,
)
from game.strategy.data.containable import (
    SPECIES_DEFAULT_MASS_PER_UNIT,
    ContainableKind,
    ItemContainable,
    ItemRef,
    PopulationContainable,
    ResourceContainable,
    species_mass_per_unit,
)


def _any_policy() -> ContainerPolicy:
    return ContainerPolicy(
        allowed_kinds=frozenset({
            ContainableKind.RESOURCE,
            ContainableKind.ITEM,
            ContainableKind.POPULATION,
        }),
        allowed_type_ids=None,
    )


@pytest.fixture(autouse=True)
def _reset_catalog():
    """Ensure each test starts with the canonical catalog."""
    set_resource_catalog(None)
    yield
    set_resource_catalog(None)


# ---------------------------------------------------------------------------
# Surface
# ---------------------------------------------------------------------------


class TestContainableSurface:
    def test_resource_kind_and_type_id(self):
        c = ResourceContainable("metals")
        assert c.kind is ContainableKind.RESOURCE
        assert c.type_id == "metals"

    def test_item_kind_and_type_id(self):
        ref = ItemRef("qs_fighter", "i-1", 100.0)
        c = ItemContainable(ref)
        assert c.kind is ContainableKind.ITEM
        assert c.type_id == "qs_fighter"

    def test_population_kind_and_type_id(self):
        c = PopulationContainable("human")
        assert c.kind is ContainableKind.POPULATION
        assert c.type_id == "human"

    def test_containables_frozen(self):
        c = ResourceContainable("metals")
        with pytest.raises((AttributeError, TypeError)):
            c.resource_id = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Mass-per-unit resolution
# ---------------------------------------------------------------------------


class TestResourceMassResolution:
    """Container reads ResourceContainable mass through the Core ResourceCatalog."""

    def test_resource_mass_uses_canonical_catalog(self):
        # No catalog override; default-loaded canonical data/resources.json.
        container = Container(capacity_mass=100.0, policy=_any_policy())
        result = container.add(ResourceContainable("metals"), 1000.0)
        assert result is AddResult.OK
        # 1000 units of metals at 0.01 = 10 tons.
        assert container.mass_used == pytest.approx(10.0)

    def test_resource_mass_via_injected_catalog(self):
        # Override the catalog with a deterministic in-memory one.
        catalog = ResourceCatalog.from_data([
            {"id": "test_metals", "name": "Test Metals", "mass_per_unit": 0.5},
        ])
        set_resource_catalog(catalog)

        container = Container(capacity_mass=100.0, policy=_any_policy())
        result = container.add(ResourceContainable("test_metals"), 10.0)
        assert result is AddResult.OK
        assert container.mass_used == pytest.approx(5.0)

    def test_unknown_resource_raises_when_added(self):
        # Catalog has no "dilithium".
        container = Container(capacity_mass=100.0, policy=_any_policy())
        with pytest.raises(KeyError):
            container.add(ResourceContainable("dilithium"), 1.0)


class TestItemMassResolution:
    def test_item_mass_comes_from_item_ref(self):
        container = Container(capacity_mass=200.0, policy=_any_policy())
        container.add(ItemContainable(ItemRef("qs_fighter", "i-1", 75.0)), 1)
        assert container.mass_used == pytest.approx(75.0)

    def test_item_mass_is_per_instance(self):
        # Two items with the same design but different recorded masses
        # both contribute their own mass to the total (this is how
        # damaged instances stay distinct from healthy ones).
        container = Container(capacity_mass=500.0, policy=_any_policy())
        container.add(ItemContainable(ItemRef("qs_fighter", "i-1", 80.0)), 1)
        container.add(ItemContainable(ItemRef("qs_fighter", "i-2", 100.0)), 1)
        assert container.mass_used == pytest.approx(180.0)


class TestPopulationMassResolution:
    def test_population_mass_uses_species_default(self):
        # 10 individuals per ton == 0.1 per individual per user directive.
        assert species_mass_per_unit("human") == pytest.approx(SPECIES_DEFAULT_MASS_PER_UNIT)
        assert species_mass_per_unit("vulcan") == pytest.approx(SPECIES_DEFAULT_MASS_PER_UNIT)

    def test_population_default_drives_container_mass(self):
        container = Container(capacity_mass=100.0, policy=_any_policy())
        container.add(PopulationContainable("human"), 500)
        # 500 * 0.1 = 50 tons.
        assert container.mass_used == pytest.approx(50.0)
