import pytest
from unittest.mock import MagicMock, patch
from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component
from game.simulation.components.component_constants import LayerType
from game.core.registry import RegistryManager
# Assuming registry is populated or we mock it.
# Better to mock components or use a minimal test case without full registry dependency if possible.


class TestShipCaching:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Create a basic ship
        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255))

        yield

        RegistryManager.instance().clear()
        patch.stopall()

    def test_cached_summary_empty_initially(self):
        assert self.ship.cached_summary == {}

    def test_cached_summary_populated_after_calc(self):
        # Create a mock weapon component
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {
                "WeaponAbility": {"damage": 10, "reload": 1.0, "range": 1000}
            }
        }
        weapon = Component(weapon_data)

        # Add to ship - use CORE layer (not HULL, which only accepts hull components)
        self.ship.add_component(weapon, LayerType.CORE)

        summary = self.ship.cached_summary
        assert summary
        assert 'dps' in summary
        assert 'mass' in summary

        # Verify values
        assert summary['dps'] == 10.0  # 10 / 1.0
        assert summary['range'] == 1000
        # Mass: Hull component (50 for Escort) + weapon component (10) = 60
        assert summary['mass'] == 60.0

    def test_cached_summary_updates(self):
        # Add weapon
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {
                "WeaponAbility": {"damage": 10, "reload": 2.0, "range": 500}
            }
        }
        weapon = Component(weapon_data)
        self.ship.add_component(weapon, LayerType.CORE)

        summary = self.ship.cached_summary
        assert summary['dps'] == 5.0

        # Add another identical weapon
        weapon2 = Component(weapon_data)
        self.ship.add_component(weapon2, LayerType.CORE)

        summary = self.ship.cached_summary
        assert summary['dps'] == 10.0
        # Mass: Hull component (50) + 2 weapons (10 + 10) = 70
        assert summary['mass'] == 70.0


class TestComponentCacheInvalidation:
    """PROJ-49 Phase 3: Tests for component list caching."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255))
        yield
        RegistryManager.instance().clear()
        patch.stopall()

    def test_cache_starts_dirty(self):
        """New ships should have dirty cache."""
        assert self.ship._components_dirty is True
        assert self.ship._components_cache is None

    def test_get_all_components_populates_cache(self):
        """Calling get_all_components should populate cache."""
        components = self.ship.get_all_components()

        # Cache should now be populated
        assert self.ship._components_dirty is False
        assert self.ship._components_cache is not None
        assert self.ship._components_cache is components

    def test_cache_reused_on_second_call(self):
        """Second call should return same cached list."""
        first_call = self.ship.get_all_components()
        second_call = self.ship.get_all_components()

        # Should be exact same object (not just equal)
        assert first_call is second_call

    def test_add_component_updates_cache(self):
        """Adding component should update cache with new component."""
        # Populate cache
        initial_components = self.ship.get_all_components()
        initial_count = len(initial_components)
        assert self.ship._components_dirty is False

        # Add component
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {"WeaponAbility": {"damage": 10, "reload": 1.0, "range": 500}}
        }
        weapon = Component(weapon_data)
        self.ship.add_component(weapon, LayerType.CORE)

        # Cache should be refreshed (not dirty) and include new component
        new_components = self.ship.get_all_components()
        assert len(new_components) == initial_count + 1
        # Verify the new component is in the cache
        assert weapon in new_components

    def test_remove_component_updates_cache(self):
        """Removing component should update cache without the component."""
        # Add component first
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {"WeaponAbility": {"damage": 10, "reload": 1.0, "range": 500}}
        }
        weapon = Component(weapon_data)
        self.ship.add_component(weapon, LayerType.CORE)

        # Populate cache and record count
        components_after_add = self.ship.get_all_components()
        count_after_add = len(components_after_add)

        # Remove component
        self.ship.remove_component(LayerType.CORE, 0)

        # Cache should be refreshed and reflect removal
        components_after_remove = self.ship.get_all_components()
        assert len(components_after_remove) == count_after_add - 1
        # Verify the weapon is no longer in the cache
        assert weapon not in components_after_remove

    def test_cache_reflects_current_components(self):
        """Cache should return correct components after invalidation."""
        # Get initial components (just hull)
        initial = self.ship.get_all_components()
        initial_count = len(initial)

        # Add weapon
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {"WeaponAbility": {"damage": 10, "reload": 1.0, "range": 500}}
        }
        weapon = Component(weapon_data)
        self.ship.add_component(weapon, LayerType.CORE)

        # Get new components - should have one more
        after_add = self.ship.get_all_components()
        assert len(after_add) == initial_count + 1

    def test_invalidate_components_cache_method(self):
        """_invalidate_components_cache should mark cache dirty."""
        # Populate cache
        self.ship.get_all_components()
        assert self.ship._components_dirty is False
        assert self.ship._components_cache is not None

        # Manually invalidate
        self.ship._invalidate_components_cache()

        # Cache should be invalidated
        assert self.ship._components_dirty is True
        assert self.ship._components_cache is None


class TestWeaponCachePerTick:
    """PROJ-49 Phase 3: Tests for per-tick weapon component caching."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255))
        yield
        RegistryManager.instance().clear()
        patch.stopall()

    def test_weapon_cache_starts_empty(self):
        """New ships should have no weapon cache."""
        assert self.ship._weapons_cache is None
        assert self.ship._weapons_cache_tick == -1

    def test_get_weapon_components_cached_populates_cache(self):
        """Calling get_weapon_components_cached populates cache."""
        # Add weapon
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {"WeaponAbility": {"damage": 10, "reload": 1.0, "range": 500}}
        }
        weapon = Component(weapon_data)
        self.ship.add_component(weapon, LayerType.CORE)

        # Call with tick 0
        weapons = self.ship.get_weapon_components_cached(0)

        assert len(weapons) == 1
        assert self.ship._weapons_cache is weapons
        assert self.ship._weapons_cache_tick == 0

    def test_weapon_cache_reused_same_tick(self):
        """Same tick should reuse cache."""
        # Add weapon
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {"WeaponAbility": {"damage": 10, "reload": 1.0, "range": 500}}
        }
        weapon = Component(weapon_data)
        self.ship.add_component(weapon, LayerType.CORE)

        first_call = self.ship.get_weapon_components_cached(5)
        second_call = self.ship.get_weapon_components_cached(5)

        # Should be exact same object
        assert first_call is second_call

    def test_weapon_cache_invalidated_new_tick(self):
        """New tick should refresh cache."""
        # Add weapon
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {"WeaponAbility": {"damage": 10, "reload": 1.0, "range": 500}}
        }
        weapon = Component(weapon_data)
        self.ship.add_component(weapon, LayerType.CORE)

        tick_5_weapons = self.ship.get_weapon_components_cached(5)
        tick_6_weapons = self.ship.get_weapon_components_cached(6)

        # Should be different list objects (refreshed)
        assert tick_5_weapons is not tick_6_weapons
        assert self.ship._weapons_cache_tick == 6

    def test_weapon_cache_only_operational(self):
        """Weapon cache should only include operational weapons."""
        # Add two weapons
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {"WeaponAbility": {"damage": 10, "reload": 1.0, "range": 500}}
        }
        weapon1 = Component(weapon_data)
        weapon2 = Component(weapon_data)
        self.ship.add_component(weapon1, LayerType.CORE)
        self.ship.add_component(weapon2, LayerType.CORE)

        # Disable one weapon (is_active controls operational status)
        weapon1.is_active = False

        weapons = self.ship.get_weapon_components_cached(0)

        # Only operational weapon should be in cache
        assert len(weapons) == 1
        assert weapon2 in weapons
        assert weapon1 not in weapons
