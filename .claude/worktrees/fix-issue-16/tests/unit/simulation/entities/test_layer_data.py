"""
Unit tests for LayerData dataclass.

PROJ-118 Phase 2: Foundation test coverage
Tests for game/simulation/entities/layer_data.py
"""
import pytest
from game.simulation.entities.layer_data import LayerData


class TestLayerDataConstruction:
    """Tests for LayerData default and explicit construction."""

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
            components=["comp1", "comp2"],
            radius_pct=0.75,
            restrictions=['ArmorOnly', 'NoWeapons'],
            max_mass_pct=2.0,
            mass=150.0,
            hp_pool=50,
            max_hp_pool=100
        )

        assert layer.components == ["comp1", "comp2"]
        assert layer.radius_pct == 0.75
        assert layer.restrictions == ['ArmorOnly', 'NoWeapons']
        assert layer.max_mass_pct == 2.0
        assert layer.mass == 150.0
        assert layer.hp_pool == 50
        assert layer.max_hp_pool == 100

    def test_construction_with_partial_explicit_values(self):
        """Construction with some explicit values uses defaults for others."""
        layer = LayerData(radius_pct=0.3, mass=100.0)

        assert layer.components == []
        assert layer.radius_pct == 0.3
        assert layer.restrictions == []
        assert layer.max_mass_pct == 1.0
        assert layer.mass == 100.0
        assert layer.hp_pool == 0
        assert layer.max_hp_pool == 0


class TestLayerDataCreateHull:
    """Tests for LayerData.create_hull() factory method."""

    def test_create_hull_returns_layerdata_instance(self):
        """create_hull() returns a LayerData instance."""
        hull = LayerData.create_hull()
        assert isinstance(hull, LayerData)

    def test_create_hull_returns_zero_radius(self):
        """create_hull() returns LayerData with radius_pct=0.0."""
        hull = LayerData.create_hull()
        assert hull.radius_pct == 0.0

    def test_create_hull_returns_hull_only_restriction(self):
        """create_hull() returns LayerData with ['HullOnly'] restriction."""
        hull = LayerData.create_hull()
        assert hull.restrictions == ['HullOnly']

    def test_create_hull_returns_high_max_mass_pct(self):
        """create_hull() returns LayerData with max_mass_pct=100.0."""
        hull = LayerData.create_hull()
        assert hull.max_mass_pct == 100.0

    def test_create_hull_returns_empty_components(self):
        """create_hull() returns LayerData with empty components list."""
        hull = LayerData.create_hull()
        assert hull.components == []

    def test_create_hull_returns_zeroed_runtime_stats(self):
        """create_hull() returns LayerData with zeroed mass and HP values."""
        hull = LayerData.create_hull()
        assert hull.mass == 0.0
        assert hull.hp_pool == 0
        assert hull.max_hp_pool == 0

    def test_multiple_create_hull_calls_return_independent_instances(self):
        """Each create_hull() call returns an independent instance."""
        hull1 = LayerData.create_hull()
        hull2 = LayerData.create_hull()

        hull1.components.append("test")
        hull1.mass = 500.0

        assert hull2.components == []
        assert hull2.mass == 0.0


class TestLayerDataFromDefinition:
    """Tests for LayerData.from_definition() factory method."""

    def test_from_definition_with_full_dict(self):
        """from_definition() with all fields uses provided values."""
        definition = {
            'radius_pct': 0.8,
            'restrictions': ['WeaponOnly'],
            'max_mass_pct': 1.5
        }

        layer = LayerData.from_definition(definition)

        assert layer.radius_pct == 0.8
        assert layer.restrictions == ['WeaponOnly']
        assert layer.max_mass_pct == 1.5

    def test_from_definition_initializes_runtime_state_to_defaults(self):
        """from_definition() always initializes runtime state to defaults."""
        definition = {
            'radius_pct': 0.8,
            'restrictions': ['WeaponOnly'],
            'max_mass_pct': 1.5
        }

        layer = LayerData.from_definition(definition)

        assert layer.components == []
        assert layer.mass == 0.0
        assert layer.hp_pool == 0
        assert layer.max_hp_pool == 0

    def test_from_definition_with_only_radius_pct(self):
        """from_definition() with only radius_pct uses defaults for others."""
        definition = {'radius_pct': 0.3}

        layer = LayerData.from_definition(definition)

        assert layer.radius_pct == 0.3
        assert layer.restrictions == []
        assert layer.max_mass_pct == 1.0

    def test_from_definition_with_only_restrictions(self):
        """from_definition() with only restrictions uses defaults for others."""
        definition = {'restrictions': ['ArmorOnly', 'NoEngines']}

        layer = LayerData.from_definition(definition)

        assert layer.radius_pct == 0.5
        assert layer.restrictions == ['ArmorOnly', 'NoEngines']
        assert layer.max_mass_pct == 1.0

    def test_from_definition_with_only_max_mass_pct(self):
        """from_definition() with only max_mass_pct uses defaults for others."""
        definition = {'max_mass_pct': 3.0}

        layer = LayerData.from_definition(definition)

        assert layer.radius_pct == 0.5
        assert layer.restrictions == []
        assert layer.max_mass_pct == 3.0

    def test_from_definition_with_empty_dict_uses_all_defaults(self):
        """from_definition() with empty dict uses all default values."""
        layer = LayerData.from_definition({})

        assert layer.radius_pct == 0.5
        assert layer.restrictions == []
        assert layer.max_mass_pct == 1.0
        assert layer.components == []
        assert layer.mass == 0.0
        assert layer.hp_pool == 0
        assert layer.max_hp_pool == 0

    def test_from_definition_ignores_unknown_keys(self):
        """from_definition() ignores keys not part of layer configuration."""
        definition = {
            'radius_pct': 0.6,
            'unknown_key': 'ignored',
            'another_unknown': 999
        }

        layer = LayerData.from_definition(definition)

        assert layer.radius_pct == 0.6
        assert not hasattr(layer, 'unknown_key')
        assert not hasattr(layer, 'another_unknown')

    def test_from_definition_with_empty_restrictions_list(self):
        """from_definition() accepts empty restrictions list."""
        definition = {'restrictions': []}

        layer = LayerData.from_definition(definition)

        assert layer.restrictions == []

    def test_from_definition_with_multiple_restrictions(self):
        """from_definition() correctly handles multiple restrictions."""
        definition = {'restrictions': ['NoWeapons', 'NoEngines', 'ArmorOnly']}

        layer = LayerData.from_definition(definition)

        assert layer.restrictions == ['NoWeapons', 'NoEngines', 'ArmorOnly']
        assert len(layer.restrictions) == 3


class TestLayerDataClear:
    """Tests for LayerData.clear() method."""

    def test_clear_resets_components_to_empty(self):
        """clear() resets components list to empty."""
        layer = LayerData()
        layer.components.extend(["comp1", "comp2", "comp3"])

        layer.clear()

        assert layer.components == []

    def test_clear_resets_mass_to_zero(self):
        """clear() resets mass to 0.0."""
        layer = LayerData(mass=500.0)

        layer.clear()

        assert layer.mass == 0.0

    def test_clear_resets_hp_pool_to_zero(self):
        """clear() resets hp_pool to 0."""
        layer = LayerData(hp_pool=75)

        layer.clear()

        assert layer.hp_pool == 0

    def test_clear_resets_max_hp_pool_to_zero(self):
        """clear() resets max_hp_pool to 0."""
        layer = LayerData(max_hp_pool=150)

        layer.clear()

        assert layer.max_hp_pool == 0

    def test_clear_resets_all_runtime_state_together(self):
        """clear() resets all runtime state in a single call."""
        layer = LayerData(
            components=["comp1"],
            mass=250.0,
            hp_pool=50,
            max_hp_pool=100
        )
        layer.components.append("comp2")

        layer.clear()

        assert layer.components == []
        assert layer.mass == 0.0
        assert layer.hp_pool == 0
        assert layer.max_hp_pool == 0

    def test_clear_preserves_radius_pct(self):
        """clear() does not modify radius_pct."""
        layer = LayerData(radius_pct=0.75, mass=500.0)

        layer.clear()

        assert layer.radius_pct == 0.75

    def test_clear_preserves_restrictions(self):
        """clear() does not modify restrictions."""
        layer = LayerData(restrictions=['ArmorOnly', 'NoWeapons'], mass=500.0)

        layer.clear()

        assert layer.restrictions == ['ArmorOnly', 'NoWeapons']

    def test_clear_preserves_max_mass_pct(self):
        """clear() does not modify max_mass_pct."""
        layer = LayerData(max_mass_pct=2.5, mass=500.0)

        layer.clear()

        assert layer.max_mass_pct == 2.5

    def test_clear_on_already_empty_layer_is_safe(self):
        """clear() on a layer with no runtime state is safe (no-op)."""
        layer = LayerData()

        layer.clear()

        assert layer.components == []
        assert layer.mass == 0.0
        assert layer.hp_pool == 0
        assert layer.max_hp_pool == 0

    def test_clear_can_be_called_multiple_times(self):
        """clear() can be called multiple times without issues."""
        layer = LayerData(mass=100.0)
        layer.components.append("test")

        layer.clear()
        layer.clear()
        layer.clear()

        assert layer.components == []
        assert layer.mass == 0.0


class TestLayerDataPropertyAccess:
    """Tests for LayerData property access and direct attribute modification."""

    def test_components_list_can_be_appended_to(self):
        """components list supports append operations."""
        layer = LayerData()
        layer.components.append("component1")
        layer.components.append("component2")

        assert len(layer.components) == 2
        assert layer.components[0] == "component1"
        assert layer.components[1] == "component2"

    def test_components_list_can_be_extended(self):
        """components list supports extend operations."""
        layer = LayerData()
        layer.components.extend(["a", "b", "c"])

        assert layer.components == ["a", "b", "c"]

    def test_components_list_can_be_cleared_directly(self):
        """components list supports direct clear()."""
        layer = LayerData()
        layer.components.extend(["a", "b", "c"])

        layer.components.clear()

        assert layer.components == []

    def test_restrictions_list_can_be_modified(self):
        """restrictions list supports modifications."""
        layer = LayerData()
        layer.restrictions.append("TestRestriction")
        layer.restrictions.append("AnotherRestriction")

        assert len(layer.restrictions) == 2

    def test_radius_pct_can_be_modified(self):
        """radius_pct can be modified after construction."""
        layer = LayerData()
        layer.radius_pct = 0.9

        assert layer.radius_pct == 0.9

    def test_max_mass_pct_can_be_modified(self):
        """max_mass_pct can be modified after construction."""
        layer = LayerData()
        layer.max_mass_pct = 5.0

        assert layer.max_mass_pct == 5.0

    def test_mass_can_be_modified(self):
        """mass can be modified after construction."""
        layer = LayerData()
        layer.mass = 123.45

        assert layer.mass == 123.45

    def test_hp_pool_can_be_modified(self):
        """hp_pool can be modified after construction."""
        layer = LayerData()
        layer.hp_pool = 75

        assert layer.hp_pool == 75

    def test_max_hp_pool_can_be_modified(self):
        """max_hp_pool can be modified after construction."""
        layer = LayerData()
        layer.max_hp_pool = 150

        assert layer.max_hp_pool == 150


class TestLayerDataInstanceIsolation:
    """Tests that each LayerData instance is independent."""

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

    def test_modifying_one_instance_does_not_affect_another(self):
        """Modifying attributes on one instance does not affect others."""
        layer1 = LayerData(radius_pct=0.3, mass=100.0)
        layer2 = LayerData(radius_pct=0.6, mass=200.0)

        layer1.radius_pct = 0.9
        layer1.mass = 999.0

        assert layer2.radius_pct == 0.6
        assert layer2.mass == 200.0


class TestLayerDataEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_radius_pct_can_be_zero(self):
        """radius_pct can be set to 0.0 (hull layer case)."""
        layer = LayerData(radius_pct=0.0)
        assert layer.radius_pct == 0.0

    def test_radius_pct_can_be_one(self):
        """radius_pct can be set to 1.0 (outermost layer)."""
        layer = LayerData(radius_pct=1.0)
        assert layer.radius_pct == 1.0

    def test_max_mass_pct_can_be_very_high(self):
        """max_mass_pct can be set to high values (hull layer case)."""
        layer = LayerData(max_mass_pct=100.0)
        assert layer.max_mass_pct == 100.0

    def test_max_mass_pct_can_be_fractional(self):
        """max_mass_pct can be fractional values."""
        layer = LayerData(max_mass_pct=0.25)
        assert layer.max_mass_pct == 0.25

    def test_mass_can_be_zero(self):
        """mass can be zero."""
        layer = LayerData(mass=0.0)
        assert layer.mass == 0.0

    def test_hp_values_can_be_zero(self):
        """HP values can be zero."""
        layer = LayerData(hp_pool=0, max_hp_pool=0)
        assert layer.hp_pool == 0
        assert layer.max_hp_pool == 0

    def test_hp_pool_can_exceed_max_hp_pool(self):
        """hp_pool can be set to exceed max_hp_pool (no validation enforced)."""
        # This tests that LayerData is just a data container without validation
        layer = LayerData(hp_pool=150, max_hp_pool=100)
        assert layer.hp_pool == 150
        assert layer.max_hp_pool == 100

    def test_empty_string_restriction_is_allowed(self):
        """Empty string in restrictions list is allowed."""
        layer = LayerData(restrictions=[''])
        assert layer.restrictions == ['']

    def test_duplicate_restrictions_are_allowed(self):
        """Duplicate restrictions are allowed (no deduplication)."""
        layer = LayerData(restrictions=['ArmorOnly', 'ArmorOnly'])
        assert layer.restrictions == ['ArmorOnly', 'ArmorOnly']
        assert len(layer.restrictions) == 2

    def test_negative_hp_pool_is_allowed(self):
        """Negative HP values are allowed (no validation enforced)."""
        layer = LayerData(hp_pool=-10, max_hp_pool=-5)
        assert layer.hp_pool == -10
        assert layer.max_hp_pool == -5

    def test_negative_mass_is_allowed(self):
        """Negative mass is allowed (no validation enforced)."""
        layer = LayerData(mass=-100.0)
        assert layer.mass == -100.0

    def test_float_precision_in_radius_pct(self):
        """radius_pct maintains float precision."""
        layer = LayerData(radius_pct=0.333333333333)
        assert abs(layer.radius_pct - 0.333333333333) < 1e-10

    def test_very_large_hp_pool(self):
        """Very large HP values are handled correctly."""
        layer = LayerData(hp_pool=10**15, max_hp_pool=10**15)
        assert layer.hp_pool == 10**15
        assert layer.max_hp_pool == 10**15


class TestLayerDataEquality:
    """Tests for LayerData equality comparison (dataclass default)."""

    def test_identical_layers_are_equal(self):
        """Two LayerData instances with identical values are equal."""
        layer1 = LayerData(
            components=[],
            radius_pct=0.5,
            restrictions=['ArmorOnly'],
            max_mass_pct=1.5,
            mass=100.0,
            hp_pool=50,
            max_hp_pool=100
        )
        layer2 = LayerData(
            components=[],
            radius_pct=0.5,
            restrictions=['ArmorOnly'],
            max_mass_pct=1.5,
            mass=100.0,
            hp_pool=50,
            max_hp_pool=100
        )
        assert layer1 == layer2

    def test_different_radius_pct_not_equal(self):
        """Layers with different radius_pct are not equal."""
        layer1 = LayerData(radius_pct=0.3)
        layer2 = LayerData(radius_pct=0.5)
        assert layer1 != layer2

    def test_different_restrictions_not_equal(self):
        """Layers with different restrictions are not equal."""
        layer1 = LayerData(restrictions=['ArmorOnly'])
        layer2 = LayerData(restrictions=['WeaponOnly'])
        assert layer1 != layer2

    def test_default_layers_are_equal(self):
        """Two default LayerData instances are equal."""
        layer1 = LayerData()
        layer2 = LayerData()
        assert layer1 == layer2

    def test_layer_not_equal_to_non_layerdata(self):
        """LayerData is not equal to non-LayerData objects."""
        layer = LayerData()
        assert layer != {"components": []}
        assert layer != None
        assert layer != "LayerData"


class TestLayerDataRepr:
    """Tests for LayerData string representation."""

    def test_repr_contains_class_name(self):
        """LayerData repr contains the class name."""
        layer = LayerData()
        repr_str = repr(layer)
        assert "LayerData" in repr_str

    def test_repr_contains_field_values(self):
        """LayerData repr contains field values."""
        layer = LayerData(radius_pct=0.75, mass=100.0)
        repr_str = repr(layer)
        assert "0.75" in repr_str
        assert "100.0" in repr_str


class TestLayerDataUsagePatterns:
    """Tests for common usage patterns with LayerData."""

    def test_typical_layer_initialization_workflow(self):
        """Test typical workflow: create from definition, add components, update stats."""
        # 1. Create from definition
        layer = LayerData.from_definition({
            'radius_pct': 0.6,
            'restrictions': ['WeaponOnly'],
            'max_mass_pct': 1.5
        })

        # 2. Add components (simulated)
        mock_comp1 = "weapon_1"
        mock_comp2 = "weapon_2"
        layer.components.append(mock_comp1)
        layer.components.append(mock_comp2)

        # 3. Update runtime stats
        layer.mass = 250.0
        layer.hp_pool = 75
        layer.max_hp_pool = 100

        # Verify final state
        assert len(layer.components) == 2
        assert layer.mass == 250.0
        assert layer.hp_pool == 75
        assert layer.max_hp_pool == 100
        assert layer.radius_pct == 0.6
        assert layer.restrictions == ['WeaponOnly']

    def test_reset_and_reuse_layer(self):
        """Test clearing and reusing a layer."""
        layer = LayerData(
            radius_pct=0.8,
            restrictions=['ArmorOnly'],
            max_mass_pct=2.0
        )

        # Simulate use
        layer.components.extend(["armor_1", "armor_2"])
        layer.mass = 500.0
        layer.hp_pool = 200
        layer.max_hp_pool = 250

        # Reset for reuse
        layer.clear()

        # Should be ready for new components while keeping config
        assert layer.components == []
        assert layer.mass == 0.0
        assert layer.hp_pool == 0
        assert layer.max_hp_pool == 0
        assert layer.radius_pct == 0.8  # Preserved
        assert layer.restrictions == ['ArmorOnly']  # Preserved
        assert layer.max_mass_pct == 2.0  # Preserved

    def test_hull_layer_special_case(self):
        """Test hull layer has special configuration."""
        hull = LayerData.create_hull()

        # Hull has structural role (radius 0)
        assert hull.radius_pct == 0.0

        # Hull only accepts hull components
        assert 'HullOnly' in hull.restrictions

        # Hull can hold 100% of ship mass
        assert hull.max_mass_pct == 100.0
