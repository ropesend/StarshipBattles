"""
Tests for AbilityStatBinding dataclass - Phase 1 Task 1.2

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest


class TestAbilityStatBinding:
    """Tests for the AbilityStatBinding dataclass."""

    def test_binding_creation(self):
        """AbilityStatBinding should store stat_key, attribute_name, operation."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage',
            operation='multiply'
        )

        assert binding.stat_key == StatKey.DAMAGE_MULT
        assert binding.attribute_name == 'damage'
        assert binding.operation == 'multiply'

    def test_binding_default_operation(self):
        """operation should default to 'multiply'."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage'
        )

        assert binding.operation == 'multiply'

    def test_binding_default_base_attribute(self):
        """base_attribute should default to '_base_{attribute_name}'."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        binding = AbilityStatBinding(
            stat_key=StatKey.DAMAGE_MULT,
            attribute_name='damage'
        )

        assert binding.base_attribute is None
        assert binding.get_base_attribute_name() == '_base_damage'

    def test_binding_custom_base_attribute(self):
        """Should use custom base_attribute when provided."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        binding = AbilityStatBinding(
            stat_key=StatKey.ARC_ADD,
            attribute_name='firing_arc',
            operation='add',
            base_attribute='_base_firing_arc'
        )

        assert binding.base_attribute == '_base_firing_arc'
        assert binding.get_base_attribute_name() == '_base_firing_arc'

    def test_binding_operations(self):
        """Should support 'multiply', 'add', 'set' operations."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        # All valid operations should work
        multiply = AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply')
        add = AbilityStatBinding(StatKey.ACCURACY_ADD, 'accuracy', 'add')
        set_op = AbilityStatBinding(StatKey.ARC_SET, 'arc', 'set')

        assert multiply.operation == 'multiply'
        assert add.operation == 'add'
        assert set_op.operation == 'set'

    def test_binding_invalid_operation_raises(self):
        """Invalid operation should raise ValueError."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        with pytest.raises(ValueError, match="Invalid operation"):
            AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'invalid')

    def test_binding_describe(self):
        """describe() should return human-readable description."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        binding = AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply')
        desc = binding.describe()

        assert 'damage' in desc
        assert 'damage_mult' in desc

    def test_binding_apply_multiply(self):
        """apply() should multiply attribute value."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        # Create a mock ability object
        class MockAbility:
            def __init__(self):
                self._base_damage = 100.0
                self.damage = 100.0

        ability = MockAbility()
        stats = {'damage_mult': 1.5}

        binding = AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply')
        result = binding.apply(ability, stats)

        assert result is True
        assert ability.damage == 150.0

    def test_binding_apply_add(self):
        """apply() should add to attribute value."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        class MockAbility:
            def __init__(self):
                self._base_accuracy = 2.0
                self.accuracy = 2.0

        ability = MockAbility()
        stats = {'accuracy_add': 0.5}

        binding = AbilityStatBinding(StatKey.ACCURACY_ADD, 'accuracy', 'add')
        result = binding.apply(ability, stats)

        assert result is True
        assert ability.accuracy == 2.5

    def test_binding_apply_set(self):
        """apply() should set attribute value."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        class MockAbility:
            def __init__(self):
                self._base_arc = 30.0
                self.arc = 30.0

        ability = MockAbility()
        stats = {'arc_set': 90.0}

        binding = AbilityStatBinding(StatKey.ARC_SET, 'arc', 'set')
        result = binding.apply(ability, stats)

        assert result is True
        assert ability.arc == 90.0

    def test_binding_apply_missing_stat(self):
        """apply() should return False if stat not in dict."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        class MockAbility:
            def __init__(self):
                self._base_damage = 100.0
                self.damage = 100.0

        ability = MockAbility()
        stats = {}  # No damage_mult

        binding = AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply')
        result = binding.apply(ability, stats)

        assert result is False
        assert ability.damage == 100.0  # Unchanged

    def test_binding_apply_missing_base_attr(self):
        """apply() should return False if base attribute missing."""
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        class MockAbility:
            def __init__(self):
                self.damage = 100.0  # No _base_damage

        ability = MockAbility()
        stats = {'damage_mult': 1.5}

        binding = AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply')
        result = binding.apply(ability, stats)

        assert result is False
        assert ability.damage == 100.0  # Unchanged
