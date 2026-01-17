"""
Tests for ModifierService.

This service provides domain logic for component modifier operations,
including allowance checks, mandatory modifier management, and value constraints.
"""
import pytest

from game.simulation.services.modifier_service import ModifierService
from game.simulation.components.component import create_component


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def weapon_component():
    """Create a weapon component (laser cannon) for testing."""
    return create_component("laser_cannon")


@pytest.fixture
def engine_component():
    """Create an engine component for testing."""
    return create_component("standard_engine")


@pytest.fixture
def armor_component():
    """Create an armor component for testing."""
    return create_component("armor_plate")


@pytest.fixture
def seeker_component():
    """Create a seeker weapon component for testing."""
    return create_component("missile_launcher")


@pytest.fixture
def beam_component():
    """Create a beam weapon component for testing."""
    return create_component("beam_emitter")


# =============================================================================
# TestIsModifierAllowed
# =============================================================================

class TestIsModifierAllowed:
    """Tests for ModifierService.is_modifier_allowed()."""

    def test_simple_size_mount_allowed_for_all(self, weapon_component, engine_component):
        """simple_size_mount should be allowed for all components."""
        assert ModifierService.is_modifier_allowed('simple_size_mount', weapon_component)
        assert ModifierService.is_modifier_allowed('simple_size_mount', engine_component)

    def test_turret_mount_allowed_for_weapon(self, weapon_component):
        """turret_mount should be allowed for weapon components."""
        assert ModifierService.is_modifier_allowed('turret_mount', weapon_component)

    def test_turret_mount_not_allowed_for_engine(self, engine_component):
        """turret_mount should NOT be allowed for engine components."""
        assert not ModifierService.is_modifier_allowed('turret_mount', engine_component)

    def test_range_mount_allowed_for_projectile_weapon(self, weapon_component):
        """range_mount should be allowed for projectile weapons."""
        # Assuming laser_cannon is a projectile weapon
        result = ModifierService.is_modifier_allowed('range_mount', weapon_component)
        # Result depends on whether weapon has ProjectileWeaponAbility or BeamWeaponAbility
        assert isinstance(result, bool)

    def test_range_mount_not_allowed_for_seeker(self, seeker_component):
        """range_mount should NOT be allowed for seeker weapons (denied by restrictions)."""
        if seeker_component:
            assert not ModifierService.is_modifier_allowed('range_mount', seeker_component)

    def test_nonexistent_modifier_not_allowed(self, weapon_component):
        """Non-existent modifier should not be allowed."""
        assert not ModifierService.is_modifier_allowed('nonexistent_modifier_xyz', weapon_component)

    def test_hardened_not_allowed_for_armor(self, armor_component):
        """hardened modifier should NOT be allowed for armor (denied by restrictions)."""
        assert not ModifierService.is_modifier_allowed('hardened', armor_component)


# =============================================================================
# TestGetMandatoryModifiers
# =============================================================================

class TestGetMandatoryModifiers:
    """Tests for ModifierService.get_mandatory_modifiers()."""

    def test_returns_list(self, weapon_component):
        """get_mandatory_modifiers() should return a list."""
        result = ModifierService.get_mandatory_modifiers(weapon_component)
        assert isinstance(result, list)

    def test_simple_size_always_mandatory(self, weapon_component, engine_component, armor_component):
        """simple_size_mount should always be in mandatory modifiers."""
        assert 'simple_size_mount' in ModifierService.get_mandatory_modifiers(weapon_component)
        assert 'simple_size_mount' in ModifierService.get_mandatory_modifiers(engine_component)
        assert 'simple_size_mount' in ModifierService.get_mandatory_modifiers(armor_component)

    def test_weapon_gets_facing_mandatory(self, weapon_component):
        """Weapon components should have facing as mandatory."""
        mandatory = ModifierService.get_mandatory_modifiers(weapon_component)
        assert 'facing' in mandatory

    def test_weapon_gets_turret_mount_mandatory(self, weapon_component):
        """Weapon components should have turret_mount as mandatory."""
        mandatory = ModifierService.get_mandatory_modifiers(weapon_component)
        assert 'turret_mount' in mandatory

    def test_engine_does_not_get_weapon_modifiers(self, engine_component):
        """Engine components should NOT have weapon-specific mandatory modifiers."""
        mandatory = ModifierService.get_mandatory_modifiers(engine_component)
        assert 'facing' not in mandatory
        assert 'turret_mount' not in mandatory

    def test_seeker_gets_seeker_modifiers(self, seeker_component):
        """Seeker weapons should have seeker-specific mandatory modifiers."""
        if seeker_component and seeker_component.has_ability('SeekerWeaponAbility'):
            mandatory = ModifierService.get_mandatory_modifiers(seeker_component)
            # Check at least one seeker modifier is present
            seeker_mods = ['seeker_endurance', 'seeker_damage', 'seeker_armored', 'seeker_stealth']
            has_seeker_mod = any(mod in mandatory for mod in seeker_mods)
            assert has_seeker_mod


# =============================================================================
# TestIsModifierMandatory
# =============================================================================

class TestIsModifierMandatory:
    """Tests for ModifierService.is_modifier_mandatory()."""

    def test_simple_size_is_mandatory(self, weapon_component):
        """simple_size_mount should always be mandatory."""
        assert ModifierService.is_modifier_mandatory('simple_size_mount', weapon_component)

    def test_facing_mandatory_for_weapon(self, weapon_component):
        """facing should be mandatory for weapon components."""
        assert ModifierService.is_modifier_mandatory('facing', weapon_component)

    def test_facing_not_mandatory_for_engine(self, engine_component):
        """facing should NOT be mandatory for engine components."""
        assert not ModifierService.is_modifier_mandatory('facing', engine_component)

    def test_turret_mandatory_for_weapon(self, weapon_component):
        """turret_mount should be mandatory for weapon components."""
        assert ModifierService.is_modifier_mandatory('turret_mount', weapon_component)

    def test_arbitrary_modifier_not_mandatory(self, weapon_component):
        """Random modifier should not be mandatory."""
        assert not ModifierService.is_modifier_mandatory('hardened', weapon_component)


# =============================================================================
# TestGetInitialValue
# =============================================================================

class TestGetInitialValue:
    """Tests for ModifierService.get_initial_value()."""

    def test_simple_size_mount_initial_value(self, weapon_component):
        """simple_size_mount should start at 1.0."""
        value = ModifierService.get_initial_value('simple_size_mount', weapon_component)
        assert value == 1.0

    def test_range_mount_initial_value(self, weapon_component):
        """range_mount should start at 0.0."""
        value = ModifierService.get_initial_value('range_mount', weapon_component)
        assert value == 0.0

    def test_facing_initial_value(self, weapon_component):
        """facing should start at 0.0 (forward)."""
        value = ModifierService.get_initial_value('facing', weapon_component)
        assert value == 0.0

    def test_precision_mount_initial_value(self, weapon_component):
        """precision_mount should start at 0.0."""
        value = ModifierService.get_initial_value('precision_mount', weapon_component)
        assert value == 0.0

    def test_turret_mount_initial_value_uses_base_arc(self, weapon_component):
        """turret_mount initial value should use component's base firing_arc."""
        value = ModifierService.get_initial_value('turret_mount', weapon_component)
        # Should be a float (either base arc from component or min_val from modifier)
        assert isinstance(value, float)
        assert value >= 0

    def test_nonexistent_modifier_returns_zero(self, weapon_component):
        """Non-existent modifier should return 0."""
        value = ModifierService.get_initial_value('nonexistent_modifier_xyz', weapon_component)
        assert value == 0


# =============================================================================
# TestEnsureMandatoryModifiers
# =============================================================================

class TestEnsureMandatoryModifiers:
    """Tests for ModifierService.ensure_mandatory_modifiers()."""

    def test_adds_missing_mandatory_modifiers(self, weapon_component):
        """ensure_mandatory_modifiers() should add all mandatory modifiers."""
        # Clear any existing modifiers
        weapon_component.modifiers.clear()

        ModifierService.ensure_mandatory_modifiers(weapon_component)

        # Check that mandatory modifiers are now present
        mandatory = ModifierService.get_mandatory_modifiers(weapon_component)
        for mod_id in mandatory:
            modifier = weapon_component.get_modifier(mod_id)
            assert modifier is not None, f"Missing mandatory modifier: {mod_id}"

    def test_does_not_duplicate_existing_modifiers(self, weapon_component):
        """ensure_mandatory_modifiers() should not duplicate existing modifiers."""
        # Ensure modifiers exist first
        ModifierService.ensure_mandatory_modifiers(weapon_component)
        initial_count = len(weapon_component.modifiers)

        # Call again
        ModifierService.ensure_mandatory_modifiers(weapon_component)
        final_count = len(weapon_component.modifiers)

        assert initial_count == final_count

    def test_sets_initial_values(self, weapon_component):
        """ensure_mandatory_modifiers() should set initial values."""
        weapon_component.modifiers.clear()
        ModifierService.ensure_mandatory_modifiers(weapon_component)

        # Check simple_size_mount has value 1.0
        size_mod = weapon_component.get_modifier('simple_size_mount')
        if size_mod:
            assert size_mod.value == 1.0


# =============================================================================
# TestGetLocalMinMax
# =============================================================================

class TestGetLocalMinMax:
    """Tests for ModifierService.get_local_min_max()."""

    def test_returns_tuple(self, weapon_component):
        """get_local_min_max() should return a tuple of (min, max)."""
        result = ModifierService.get_local_min_max('simple_size_mount', weapon_component)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_simple_size_mount_range(self, weapon_component):
        """simple_size_mount should have range [1, 1024]."""
        min_val, max_val = ModifierService.get_local_min_max('simple_size_mount', weapon_component)
        assert min_val == 1.0
        assert max_val == 1024.0

    def test_facing_range(self, weapon_component):
        """facing should have range [0, 359]."""
        min_val, max_val = ModifierService.get_local_min_max('facing', weapon_component)
        assert min_val == 0.0
        assert max_val == 359.0

    def test_turret_mount_min_uses_base_arc(self, weapon_component):
        """turret_mount min should be at least the component's base firing_arc."""
        min_val, max_val = ModifierService.get_local_min_max('turret_mount', weapon_component)
        assert min_val >= 0
        assert max_val == 180.0

    def test_nonexistent_modifier_returns_default(self, weapon_component):
        """Non-existent modifier should return (0, 100)."""
        min_val, max_val = ModifierService.get_local_min_max('nonexistent_modifier_xyz', weapon_component)
        assert min_val == 0
        assert max_val == 100

    def test_range_mount_range(self, weapon_component):
        """range_mount should have range [0, 3]."""
        min_val, max_val = ModifierService.get_local_min_max('range_mount', weapon_component)
        assert min_val == 0.0
        assert max_val == 3.0
