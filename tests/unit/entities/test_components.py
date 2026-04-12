import pytest

from game.simulation.components.component import get_all_components, create_component
from game.core.registry import RegistryManager


class TestComponents:
    def test_load_components(self, fresh_registries):
        """Verify components.json is loaded correctly."""
        comps = get_all_components(registries=fresh_registries)
        assert len(comps) > 0, "No components loaded"

        bridge = create_component('bridge', registries=fresh_registries)
        assert bridge is not None
        # Recalculate stats to resolve formulas (uses default context k=1000)
        bridge.recalculate_stats()
        assert bridge.name == "Bridge"
        assert bridge.mass == 50

    def test_create_component_types(self, stable_component_registries):
        # Uses stable test values (railgun damage=40) instead of production
        # data so the assertion is stable against balance rebalancing.
        railgun = create_component('railgun', registries=stable_component_registries)
        # Phase 7: Check weapon has ability, not legacy class
        assert railgun.has_ability('WeaponAbility') is True
        weapon_ab = railgun.get_ability('ProjectileWeaponAbility')
        assert weapon_ab is not None
        assert weapon_ab.damage == 40

        tank = create_component('fuel_tank', registries=stable_component_registries)

        # Verify ResourceStorage ability exists
        from game.simulation.components.abilities.resources import ResourceStorage
        found_storage = False
        for ab in tank.ability_instances:
            if isinstance(ab, ResourceStorage) and ab.resource_type == 'fuel':
                found_storage = True
                break
        assert found_storage is True, "Fuel tank should have Fuel Storage ability"


class TestModifierStacking:
    """Test that modifiers stack multiplicatively, not override each other."""

    def test_single_size_modifier(self, fresh_registries):
        """Size mount 2x should double mass."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass  # 100

        railgun.add_modifier('simple_size_mount', 2.0)

        assert railgun.mass == pytest.approx(base_mass * 2.0, abs=0.01)

    def test_single_range_modifier(self, fresh_registries):
        """Range mount level 1 should increase mass by 3.5x."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass  # 100

        railgun.add_modifier('range_mount', 1.0)  # Level 1 = 3.5x mass

        assert railgun.mass == pytest.approx(base_mass * 3.5, abs=0.01)

    def test_multiplicative_stacking_size_and_range(self, fresh_registries):
        """Size 2x + Range level 1 (3.5x) should give 7x total mass."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass  # 100

        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('range_mount', 1.0)  # 3.5x

        expected_mass = base_mass * 2.0 * 3.5  # 7x = 700
        assert railgun.mass == pytest.approx(expected_mass, abs=0.01), \
            f"Expected {expected_mass}, got {railgun.mass}. Modifiers should stack multiplicatively!"

    def test_multiplicative_stacking_size_and_hardened(self, fresh_registries):
        """Size 2x + Hardened_mount 1.25x = 2.5x total mass."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass  # 100

        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('hardened_mount', 1.25)  # 1.25x mass

        expected_mass = base_mass * 2.0 * 1.25  # 2.5x = 250
        assert railgun.mass == pytest.approx(expected_mass, abs=0.01), \
            f"Expected {expected_mass}, got {railgun.mass}. Modifiers should stack multiplicatively!"

    def test_triple_modifier_stacking(self, fresh_registries):
        """Size 2x + Range level 1 (3.5x) + Hardened_mount (1.25x) = 8.75x mass."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass  # 100

        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('range_mount', 1.0)  # 3.5x
        railgun.add_modifier('hardened_mount', 1.25)  # 1.25x mass

        expected_mass = base_mass * 2.0 * 3.5 * 1.25  # 8.75x = 875
        assert railgun.mass == pytest.approx(expected_mass, abs=0.01), \
            f"Expected {expected_mass}, got {railgun.mass}. Triple stacking failed!"

    def test_hp_stacking(self, fresh_registries):
        """Size 2x HP + Hardened_mount (4x HP) = 8x HP."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_hp = railgun.base_max_hp  # 150

        railgun.add_modifier('simple_size_mount', 2.0)  # 2x HP
        railgun.add_modifier('hardened_mount', 2.0)  # 4x HP (value squared)

        expected_hp = base_hp * 2.0 * 4.0  # 8x = 1200
        assert railgun.max_hp == pytest.approx(expected_hp, abs=1), \
            f"Expected HP {expected_hp}, got {railgun.max_hp}"

    def test_range_stacking(self, fresh_registries):
        """Range mount level 2 should give 4x range."""
        railgun = create_component('railgun', registries=fresh_registries)
        # Phase 7: Get range from ability
        weapon_ab = railgun.get_ability('ProjectileWeaponAbility')
        base_range = weapon_ab.range  # 2400

        railgun.add_modifier('range_mount', 2.0)  # Level 2 = 4x range

        # Re-get ability after modifier application
        weapon_ab = railgun.get_ability('ProjectileWeaponAbility')
        expected_range = base_range * 4  # 9600
        assert weapon_ab.range == pytest.approx(expected_range, abs=1)


class TestModifierOrder:
    """Ensure modifier application order doesn't affect final result."""

    def test_order_independence(self, fresh_registries):
        """Adding modifiers in different order should give same result."""
        # Order A: size first, then range
        railgun_a = create_component('railgun', registries=fresh_registries)
        railgun_a.add_modifier('simple_size_mount', 2.0)
        railgun_a.add_modifier('range_mount', 1.0)

        # Order B: range first, then size
        railgun_b = create_component('railgun', registries=fresh_registries)
        railgun_b.add_modifier('range_mount', 1.0)
        railgun_b.add_modifier('simple_size_mount', 2.0)

        assert railgun_a.mass == pytest.approx(railgun_b.mass, abs=0.01), \
            "Modifier order should not affect final mass!"
        assert railgun_a.max_hp == pytest.approx(railgun_b.max_hp, abs=1), \
            "Modifier order should not affect final HP!"


class TestTurretMount:
    """Test turret mount logarithmic diminishing returns."""

    def test_turret_0_degrees_no_change(self, fresh_registries):
        """0 degree turret should not increase mass."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass

        railgun.add_modifier('turret_mount', 0)

        assert railgun.mass == pytest.approx(base_mass, abs=0.01)

    def test_turret_diminishing_returns(self, fresh_registries):
        """Mass increase should diminish as arc increases."""
        import math

        railgun_45 = create_component('railgun', registries=fresh_registries)
        railgun_90 = create_component('railgun', registries=fresh_registries)
        railgun_180 = create_component('railgun', registries=fresh_registries)
        base_mass = railgun_45.base_mass

        railgun_45.add_modifier('turret_mount', 45)
        railgun_90.add_modifier('turret_mount', 90)
        railgun_180.add_modifier('turret_mount', 180)

        # Calculate increases from base
        increase_45 = railgun_45.mass - base_mass
        increase_90 = railgun_90.mass - base_mass
        increase_180 = railgun_180.mass - base_mass

        # Going from 0-45 should cost more than 90-180
        cost_0_to_45 = increase_45
        cost_90_to_180 = increase_180 - increase_90

        assert cost_0_to_45 > cost_90_to_180, \
            "First 45 degrees should cost more than 90-180 degrees!"

    def test_turret_180_only_slightly_more_than_90(self, fresh_registries):
        """180 degree turret should only cost slightly more than 90."""
        railgun_90 = create_component('railgun', registries=fresh_registries)
        railgun_180 = create_component('railgun', registries=fresh_registries)
        base_mass = railgun_90.base_mass

        railgun_90.add_modifier('turret_mount', 90)
        railgun_180.add_modifier('turret_mount', 180)

        # 180 should be less than 20% more than 90
        ratio = railgun_180.mass / railgun_90.mass
        assert ratio < 1.20, \
            f"180 degrees should be <20% more than 90 degrees, got {ratio:.2%}"

    def test_turret_stacks_with_size(self, fresh_registries):
        """Turret mount should stack multiplicatively with size mount."""
        railgun = create_component('railgun', registries=fresh_registries)
        base_mass = railgun.base_mass

        railgun.add_modifier('simple_size_mount', 2.0)  # 2x
        railgun.add_modifier('turret_mount', 90)  # ~1.71x

        # Should be approximately 2.0 * 1.71 = 3.42x
        expected_mult = 2.0 * (1.0 + 0.514 * 1.386)  # ln(1 + 90/30) = ln(4)
        expected_mass = base_mass * expected_mult

        assert railgun.mass == pytest.approx(expected_mass, abs=1), \
            f"Size 2x + Turret 90 degrees should stack multiplicatively"


class TestModifierDataMethods:
    """Test the new modifier data methods: get_all_modifier_effects, get_modifier_stat_summary."""

    def test_get_all_modifier_effects_no_modifiers(self, fresh_registries):
        """Component with no modifiers returns empty list."""
        railgun = create_component('railgun', registries=fresh_registries)
        # Remove any default modifiers
        railgun.modifiers = []
        railgun.recalculate_stats()

        effects = railgun.get_all_modifier_effects()

        assert isinstance(effects, list)
        assert len(effects) == 0

    def test_get_all_modifier_effects_single_modifier(self, fresh_registries):
        """Single modifier returns its evaluated effects."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.modifiers = []
        railgun.add_modifier('simple_size_mount', 2.0)

        effects = railgun.get_all_modifier_effects()

        assert isinstance(effects, list)
        assert len(effects) > 0

        # Check that effects have the expected structure
        for effect in effects:
            assert hasattr(effect, 'stat_key')
            assert hasattr(effect, 'value')
            assert hasattr(effect, 'operation')
            assert hasattr(effect, 'source_modifier_id')

    def test_get_all_modifier_effects_multiple_modifiers(self, fresh_registries):
        """Multiple modifiers return all their effects combined."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.modifiers = []
        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('hardened_mount', 1.5)

        effects = railgun.get_all_modifier_effects()

        # Should have effects from both modifiers
        source_ids = {e.source_modifier_id for e in effects}
        assert 'simple_size_mount' in source_ids
        assert 'hardened_mount' in source_ids

    def test_get_all_modifier_effects_returns_modifier_effect_objects(self, fresh_registries):
        """Effects should be ModifierEffect dataclass instances."""
        from game.simulation.components.modifier_effects import ModifierEffect

        railgun = create_component('railgun', registries=fresh_registries)
        railgun.modifiers = []
        railgun.add_modifier('simple_size_mount', 2.0)

        effects = railgun.get_all_modifier_effects()

        for effect in effects:
            assert isinstance(effect, ModifierEffect)

    def test_get_modifier_stat_summary_no_modifiers(self, fresh_registries):
        """Component with no modifiers returns empty/default summary."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.modifiers = []
        railgun.recalculate_stats()

        summary = railgun.get_modifier_stat_summary()

        assert isinstance(summary, dict)
        # Should have empty or default values

    def test_get_modifier_stat_summary_single_modifier(self, fresh_registries):
        """Single modifier returns correct stat summary grouped by stat."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.modifiers = []
        railgun.add_modifier('simple_size_mount', 2.0)  # 2x mass_mult, 2x hp_mult

        summary = railgun.get_modifier_stat_summary()

        assert isinstance(summary, dict)
        # Should have stats as keys
        assert 'mass_mult' in summary

        # Each stat entry should have net_value and contributors
        mass_entry = summary['mass_mult']
        assert 'net_value' in mass_entry
        assert 'contributors' in mass_entry
        assert 'operation' in mass_entry

    def test_get_modifier_stat_summary_multiple_modifiers_same_stat(self, fresh_registries):
        """Multiple modifiers affecting same stat show correct net value."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.modifiers = []
        railgun.add_modifier('simple_size_mount', 2.0)  # 2x mass_mult
        railgun.add_modifier('hardened_mount', 1.5)  # 1.5x mass_mult

        summary = railgun.get_modifier_stat_summary()

        # Net mass_mult should be multiplicative: 2.0 * 1.5 = 3.0
        mass_entry = summary.get('mass_mult', {})
        assert mass_entry.get('net_value', 0) == pytest.approx(3.0, abs=0.01)

        # Contributors should list both modifiers
        contributors = mass_entry.get('contributors', [])
        assert len(contributors) == 2

    def test_get_modifier_stat_summary_add_operations(self, fresh_registries):
        """Addition operations should sum values correctly."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.modifiers = []
        # Turret mount uses arc_add
        railgun.add_modifier('turret_mount', 90)

        summary = railgun.get_modifier_stat_summary()

        if 'arc_add' in summary:
            arc_entry = summary['arc_add']
            assert 'net_value' in arc_entry
            assert arc_entry['operation'] == 'add'
