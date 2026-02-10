"""
Unit tests for LayerData dataclass.

PROJ-84 Phase 1: Ship Layer Data Typed Structures
"""
import pytest
from game.simulation.entities.layer_data import LayerData
from game.simulation.components.component import Component


class TestLayerDataConstruction:
    """Tests for LayerData construction."""

    def test_default_construction_has_correct_defaults(self):
        """Default construction creates LayerData with expected default values."""
        layer = LayerData()

        assert layer.components == []
        assert layer.radius_pct == 0.5
        assert layer.restrictions == []
        assert layer.max_mass_pct == 1.0
        assert layer.mass == 0.0
        assert layer.hp_pool == 0
        assert layer.max_hp_pool == 0

    def test_construction_with_explicit_values(self):
        """Construction with explicit values sets all fields correctly."""
        layer = LayerData(
            components=[],
            radius_pct=0.75,
            restrictions=['ArmorOnly'],
            max_mass_pct=2.0,
            mass=150.0,
            hp_pool=50,
            max_hp_pool=100
        )

        assert layer.radius_pct == 0.75
        assert layer.restrictions == ['ArmorOnly']
        assert layer.max_mass_pct == 2.0
        assert layer.mass == 150.0
        assert layer.hp_pool == 50
        assert layer.max_hp_pool == 100


class TestLayerDataCreateHull:
    """Tests for LayerData.create_hull() factory method."""

    def test_create_hull_returns_correct_radius(self):
        """create_hull() returns LayerData with radius_pct=0.0."""
        hull = LayerData.create_hull()
        assert hull.radius_pct == 0.0

    def test_create_hull_returns_hull_only_restriction(self):
        """create_hull() returns LayerData with ['HullOnly'] restriction."""
        hull = LayerData.create_hull()
        assert hull.restrictions == ['HullOnly']

    def test_create_hull_returns_correct_max_mass_pct(self):
        """create_hull() returns LayerData with max_mass_pct=100.0."""
        hull = LayerData.create_hull()
        assert hull.max_mass_pct == 100.0

    def test_create_hull_returns_empty_components(self):
        """create_hull() returns LayerData with empty components list."""
        hull = LayerData.create_hull()
        assert hull.components == []

    def test_create_hull_returns_zeroed_stats(self):
        """create_hull() returns LayerData with zeroed stats."""
        hull = LayerData.create_hull()
        assert hull.mass == 0.0
        assert hull.hp_pool == 0
        assert hull.max_hp_pool == 0


class TestLayerDataFromDefinition:
    """Tests for LayerData.from_definition() factory method."""

    def test_from_definition_with_full_dict(self):
        """from_definition() with all fields set uses provided values."""
        definition = {
            'radius_pct': 0.8,
            'restrictions': ['WeaponOnly'],
            'max_mass_pct': 1.5
        }

        layer = LayerData.from_definition(definition)

        assert layer.radius_pct == 0.8
        assert layer.restrictions == ['WeaponOnly']
        assert layer.max_mass_pct == 1.5
        assert layer.components == []
        assert layer.mass == 0.0
        assert layer.hp_pool == 0
        assert layer.max_hp_pool == 0

    def test_from_definition_with_partial_dict_uses_defaults(self):
        """from_definition() with missing keys uses default values."""
        definition = {'radius_pct': 0.3}

        layer = LayerData.from_definition(definition)

        assert layer.radius_pct == 0.3
        assert layer.restrictions == []  # default
        assert layer.max_mass_pct == 1.0  # default

    def test_from_definition_with_empty_dict_uses_all_defaults(self):
        """from_definition() with empty dict uses all default values."""
        layer = LayerData.from_definition({})

        assert layer.radius_pct == 0.5
        assert layer.restrictions == []
        assert layer.max_mass_pct == 1.0


class TestLayerDataClear:
    """Tests for LayerData.clear() method."""

    def test_clear_resets_components_to_empty(self):
        """clear() resets components list to empty."""
        layer = LayerData()
        # Simulate having components
        layer.components.append("fake_component")

        layer.clear()

        assert layer.components == []

    def test_clear_resets_mass_to_zero(self):
        """clear() resets mass to 0.0."""
        layer = LayerData(mass=500.0)

        layer.clear()

        assert layer.mass == 0.0

    def test_clear_resets_hp_pool_to_zero(self):
        """clear() resets hp_pool and max_hp_pool to 0."""
        layer = LayerData(hp_pool=50, max_hp_pool=100)

        layer.clear()

        assert layer.hp_pool == 0
        assert layer.max_hp_pool == 0

    def test_clear_preserves_radius_pct(self):
        """clear() does not modify radius_pct."""
        layer = LayerData(radius_pct=0.75, mass=500.0)

        layer.clear()

        assert layer.radius_pct == 0.75

    def test_clear_preserves_restrictions(self):
        """clear() does not modify restrictions."""
        layer = LayerData(restrictions=['ArmorOnly'], mass=500.0)

        layer.clear()

        assert layer.restrictions == ['ArmorOnly']

    def test_clear_preserves_max_mass_pct(self):
        """clear() does not modify max_mass_pct."""
        layer = LayerData(max_mass_pct=2.0, mass=500.0)

        layer.clear()

        assert layer.max_mass_pct == 2.0


class TestLayerDataAttributeAccess:
    """Tests for LayerData attribute access and mutability."""

    def test_components_is_mutable_list(self):
        """components attribute is a mutable list."""
        layer = LayerData()
        layer.components.append("test")

        assert len(layer.components) == 1
        assert layer.components[0] == "test"

    def test_restrictions_is_mutable_list(self):
        """restrictions attribute is a mutable list."""
        layer = LayerData()
        layer.restrictions.append("TestRestriction")

        assert len(layer.restrictions) == 1

    def test_radius_pct_is_mutable(self):
        """radius_pct can be modified after construction."""
        layer = LayerData()
        layer.radius_pct = 0.9

        assert layer.radius_pct == 0.9

    def test_mass_is_mutable(self):
        """mass can be modified after construction."""
        layer = LayerData()
        layer.mass = 123.45

        assert layer.mass == 123.45

    def test_hp_pool_is_mutable(self):
        """hp_pool can be modified after construction."""
        layer = LayerData()
        layer.hp_pool = 75

        assert layer.hp_pool == 75

    def test_max_hp_pool_is_mutable(self):
        """max_hp_pool can be modified after construction."""
        layer = LayerData()
        layer.max_hp_pool = 150

        assert layer.max_hp_pool == 150


class TestLayerDataDefaultFactoryIsolation:
    """Tests that default_factory creates independent lists."""

    def test_each_instance_has_independent_components_list(self):
        """Each LayerData instance gets its own components list."""
        layer1 = LayerData()
        layer2 = LayerData()

        layer1.components.append("comp1")

        assert len(layer1.components) == 1
        assert len(layer2.components) == 0

    def test_each_instance_has_independent_restrictions_list(self):
        """Each LayerData instance gets its own restrictions list."""
        layer1 = LayerData()
        layer2 = LayerData()

        layer1.restrictions.append("restriction1")

        assert len(layer1.restrictions) == 1
        assert len(layer2.restrictions) == 0
