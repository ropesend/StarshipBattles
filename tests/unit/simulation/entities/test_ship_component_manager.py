"""
Tests for ShipComponentManager -- component lifecycle delegate extracted from Ship.

PROJ-240 Phase 1: Tests written BEFORE implementation (TDD).
These tests verify the ShipComponentManager class manages component
lifecycle, caching, and queries correctly as a delegate of Ship.

Since ShipComponentManager is an internal delegate and Ship preserves
its facade API, these tests exercise the manager through Ship's public
methods to prove the delegation works correctly.
"""
import pytest

from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, create_component
from game.core.constants import LayerType


class TestShipComponentManagerAddRemove:
    """Tests for add_component, add_components_bulk, remove_component."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        """Create a standard test ship with fresh registries."""
        self.registries = fresh_registries
        self.ship = Ship(
            "TestShip", 0, 0, (255, 255, 255),
            registries=fresh_registries
        )

    def test_add_component_attaches_correctly(self):
        """add_component validates and attaches to the specified layer."""
        bridge = create_component('bridge', registries=self.registries)
        result = self.ship.add_component(bridge, LayerType.CORE)
        assert result is True
        assert bridge in self.ship.layers[LayerType.CORE].components
        assert bridge.ship is self.ship
        assert bridge.layer_assigned == LayerType.CORE

    def test_add_component_returns_false_for_none(self):
        """add_component returns False when given None."""
        result = self.ship.add_component(None, LayerType.CORE)
        assert result is False

    def test_add_components_bulk_defers_recalculation(self):
        """add_components_bulk adds multiple copies, returns count."""
        armor = create_component('armor_plate', registries=self.registries)
        count = self.ship.add_components_bulk(armor, LayerType.ARMOR, 3)
        assert count == 3
        # Verify all 3 are present
        armor_comps = self.ship.layers[LayerType.ARMOR].components
        assert len(armor_comps) == 3

    def test_add_components_bulk_stops_on_validation_failure(self):
        """add_components_bulk stops adding when validation fails.

        Tests that bulk add correctly stops when a None component is cloned
        (which returns None), or when some other validation prevents addition.
        For mass budget validation, we accept that the current validator may
        allow exceeding budget -- the important behavior is that add_components_bulk
        returns the count of successfully added items and stops on first failure.
        """
        # Test the zero-count case: try to add to a layer that blocks the classification
        # CORE blocks classification:Weapons for Escort
        railgun = create_component('railgun', registries=self.registries)
        count = self.ship.add_components_bulk(railgun, LayerType.CORE, 5)
        assert count == 0  # All should fail validation

    def test_remove_component_valid_index(self):
        """remove_component returns removed component for valid index."""
        bridge = create_component('bridge', registries=self.registries)
        self.ship.add_component(bridge, LayerType.CORE)
        removed = self.ship.remove_component(LayerType.CORE, 0)
        assert removed is bridge
        assert bridge not in self.ship.layers[LayerType.CORE].components

    def test_remove_component_invalid_index(self):
        """remove_component returns None for out-of-range index."""
        result = self.ship.remove_component(LayerType.CORE, 999)
        assert result is None


class TestShipComponentManagerGetAll:
    """Tests for get_all_components caching and defensive copy."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "TestShip", 0, 0, (255, 255, 255),
            registries=fresh_registries
        )

    def test_get_all_components_returns_correct_list(self):
        """get_all_components returns components from all layers."""
        bridge = create_component('bridge', registries=self.registries)
        self.ship.add_component(bridge, LayerType.CORE)

        armor = create_component('armor_plate', registries=self.registries)
        self.ship.add_component(armor, LayerType.ARMOR)

        all_comps = self.ship.get_all_components()
        # Should contain hull (auto-equipped) + bridge + armor
        assert bridge in all_comps
        assert armor in all_comps
        assert len(all_comps) >= 3  # hull + bridge + armor

    def test_get_all_components_returns_defensive_copy(self):
        """Mutating the returned list does NOT affect the internal cache.

        PROJ-240 BUG FIX: Previously returned the internal cache directly.
        """
        comps1 = self.ship.get_all_components()
        original_len = len(comps1)
        # Mutate the returned list
        comps1.append("GARBAGE")
        # Get again -- should not contain the garbage
        comps2 = self.ship.get_all_components()
        assert len(comps2) == original_len
        assert "GARBAGE" not in comps2

    def test_get_all_components_cache_invalidation_on_add(self):
        """Cache updates when a component is added."""
        comps_before = self.ship.get_all_components()
        count_before = len(comps_before)

        bridge = create_component('bridge', registries=self.registries)
        self.ship.add_component(bridge, LayerType.CORE)

        comps_after = self.ship.get_all_components()
        assert len(comps_after) == count_before + 1
        assert bridge in comps_after

    def test_get_all_components_cache_invalidation_on_remove(self):
        """Cache updates when a component is removed."""
        bridge = create_component('bridge', registries=self.registries)
        self.ship.add_component(bridge, LayerType.CORE)
        comps_before = self.ship.get_all_components()
        count_before = len(comps_before)

        self.ship.remove_component(LayerType.CORE, 0)
        comps_after = self.ship.get_all_components()
        assert len(comps_after) == count_before - 1


class TestShipComponentManagerIteration:
    """Tests for iter_components."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "TestShip", 0, 0, (255, 255, 255),
            registries=fresh_registries
        )

    def test_iter_components_yields_layer_component_tuples(self):
        """iter_components yields (LayerType, Component) tuples."""
        bridge = create_component('bridge', registries=self.registries)
        self.ship.add_component(bridge, LayerType.CORE)

        results = list(self.ship.iter_components())
        # Should have at least hull + bridge
        assert len(results) >= 2
        for layer_type, comp in results:
            assert isinstance(layer_type, LayerType)
            assert isinstance(comp, Component)

        # Bridge should be in the results with CORE layer
        bridge_entries = [(lt, c) for lt, c in results if c is bridge]
        assert len(bridge_entries) == 1
        assert bridge_entries[0][0] == LayerType.CORE


class TestShipComponentManagerAbilityQuery:
    """Tests for get_components_by_ability."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "TestShip", 0, 0, (255, 255, 255),
            registries=fresh_registries
        )

    def test_get_components_by_ability_operational_only(self):
        """With operational_only=True, skips non-operational components."""
        # Add a weapon
        railgun = create_component('railgun', registries=self.registries)
        self.ship.add_component(railgun, LayerType.OUTER)

        weapons = self.ship.get_components_by_ability(
            'WeaponAbility', operational_only=True
        )
        # Railgun may or may not be operational depending on requirements
        # But the filtering logic should work without error
        for comp in weapons:
            assert comp.is_operational

    def test_get_components_by_ability_all(self):
        """With operational_only=False, returns all matching components."""
        railgun = create_component('railgun', registries=self.registries)
        self.ship.add_component(railgun, LayerType.OUTER)

        all_weapons = self.ship.get_components_by_ability(
            'WeaponAbility', operational_only=False
        )
        # Should include the railgun regardless of operational status
        assert railgun in all_weapons


class TestShipComponentManagerWeaponCache:
    """Tests for get_weapon_components_cached with dirty-flag invalidation."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        # Create a ship that can have operational weapons
        fresh_registries.vehicle_classes["WeaponTestShip"] = {
            "default_hull_id": "hull_escort",
            "max_mass": 5000,
            "layers": [
                {"type": "CORE", "radius_pct": 0.3, "max_mass_pct": 0.3},
                {"type": "OUTER", "radius_pct": 0.7, "max_mass_pct": 0.4},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.3},
            ]
        }
        self.ship = Ship(
            "WeaponTestShip", 0, 0, (255, 255, 255),
            ship_class="WeaponTestShip",
            registries=fresh_registries
        )
        # Add crew support for operational components
        self.ship.add_component(
            create_component('crew_quarters', registries=fresh_registries),
            LayerType.CORE
        )
        self.ship.add_component(
            create_component('life_support', registries=fresh_registries),
            LayerType.CORE
        )
        self.ship.add_component(
            create_component('bridge', registries=fresh_registries),
            LayerType.CORE
        )

    def test_weapon_cache_returns_equal_list_on_second_call(self):
        """Second call returns equal cached list (cache hit)."""
        railgun = create_component('railgun', registries=self.registries)
        self.ship.add_component(railgun, LayerType.OUTER)

        weapons1 = self.ship.get_weapon_components_cached()
        weapons2 = self.ship.get_weapon_components_cached()
        assert weapons1 == weapons2  # Equal contents = cache hit

    def test_weapon_cache_mutation_does_not_corrupt(self):
        """Mutating the returned list must not corrupt the internal cache."""
        railgun = create_component('railgun', registries=self.registries)
        self.ship.add_component(railgun, LayerType.OUTER)

        weapons = self.ship.get_weapon_components_cached()
        weapons.clear()  # Mutate the returned list
        weapons2 = self.ship.get_weapon_components_cached()
        assert len(weapons2) > 0  # Cache unaffected

    def test_weapon_cache_invalidates_on_add(self):
        """Adding a component invalidates the weapons cache.

        PROJ-240 BUG FIX: Previously used tick-based invalidation.
        """
        weapons_before = self.ship.get_weapon_components_cached()

        railgun = create_component('railgun', registries=self.registries)
        self.ship.add_component(railgun, LayerType.OUTER)

        weapons_after = self.ship.get_weapon_components_cached()
        # Should be a different list (cache was invalidated)
        assert weapons_before is not weapons_after

    def test_weapon_cache_invalidates_on_remove(self):
        """Removing a component invalidates the weapons cache."""
        railgun = create_component('railgun', registries=self.registries)
        self.ship.add_component(railgun, LayerType.OUTER)

        weapons_before = self.ship.get_weapon_components_cached()
        self.ship.remove_component(LayerType.OUTER, 0)

        weapons_after = self.ship.get_weapon_components_cached()
        assert weapons_before is not weapons_after


class TestShipComponentManagerLayerQuery:
    """Tests for get_components_by_layer."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "TestShip", 0, 0, (255, 255, 255),
            registries=fresh_registries
        )

    def test_get_components_by_layer_returns_fresh_list(self):
        """Returns a new list each call, not an internal reference."""
        bridge = create_component('bridge', registries=self.registries)
        self.ship.add_component(bridge, LayerType.CORE)

        list1 = self.ship.get_components_by_layer(LayerType.CORE)
        list2 = self.ship.get_components_by_layer(LayerType.CORE)
        assert list1 is not list2
        assert list1 == list2

    def test_get_components_by_layer_empty_for_missing_layer(self):
        """Returns empty list for a layer that doesn't exist on this ship."""
        # The default Escort class may not have all layer types
        # Use a layer type that is guaranteed to be absent
        # Actually, all standard ships have HULL/CORE/INNER/OUTER/ARMOR
        # So we test a layer with no components instead
        result = self.ship.get_components_by_layer(LayerType.INNER)
        assert result == []


class TestShipComponentManagerHasComponents:
    """Tests for has_components."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries

    def test_has_components_true(self):
        """Returns True when ship has components (hull auto-equipped)."""
        ship = Ship(
            "TestShip", 0, 0, (255, 255, 255),
            registries=self.registries
        )
        # Escort auto-equips hull
        assert ship.has_components() is True

    def test_has_components_false(self):
        """Returns False when ship has no components at all."""
        # Use minimal registries with a class that has no default hull
        self.registries.vehicle_classes["EmptyShip"] = {
            "max_mass": 1000,
            "layers": [
                {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 0.5},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.5},
            ]
        }
        ship = Ship(
            "EmptyShip", 0, 0, (255, 255, 255),
            ship_class="EmptyShip",
            registries=self.registries
        )
        assert ship.has_components() is False


class TestShipComponentManagerFindComponent:
    """Tests for find_component_with_index."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "TestShip", 0, 0, (255, 255, 255),
            registries=fresh_registries
        )

    def test_find_component_with_index_match(self):
        """Returns (LayerType, index, Component) for matching component."""
        bridge = create_component('bridge', registries=self.registries)
        self.ship.add_component(bridge, LayerType.CORE)

        result = self.ship.find_component_with_index(
            lambda c: c.id == 'bridge'
        )
        assert result is not None
        layer_type, idx, comp = result
        assert layer_type == LayerType.CORE
        assert isinstance(idx, int)
        assert comp is bridge

    def test_find_component_with_index_no_match(self):
        """Returns None when no component matches predicate."""
        result = self.ship.find_component_with_index(
            lambda c: c.id == 'nonexistent_component_xyz'
        )
        assert result is None


class TestShipComponentManagerClearNonHull:
    """Tests for clear_non_hull_components."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "TestShip", 0, 0, (255, 255, 255),
            registries=fresh_registries
        )

    def test_clear_non_hull_preserves_hull(self):
        """clear_non_hull_components removes all except hull components."""
        # Add some non-hull components
        bridge = create_component('bridge', registries=self.registries)
        self.ship.add_component(bridge, LayerType.CORE)

        armor = create_component('armor_plate', registries=self.registries)
        self.ship.add_component(armor, LayerType.ARMOR)

        # Remember hull count
        hull_count = len(self.ship.layers[LayerType.HULL].components)
        assert hull_count > 0, "Escort should have auto-equipped hull"

        self.ship.clear_non_hull_components()

        # Hull should be preserved
        assert len(self.ship.layers[LayerType.HULL].components) == hull_count
        # Other layers should be empty
        assert len(self.ship.layers[LayerType.CORE].components) == 0
        assert len(self.ship.layers[LayerType.ARMOR].components) == 0


class TestShipComponentManagerCacheInvalidation:
    """Tests for _invalidate_components_cache clearing both caches."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.registries = fresh_registries
        self.ship = Ship(
            "TestShip", 0, 0, (255, 255, 255),
            registries=fresh_registries
        )

    def test_adding_and_removing_components_surfaces_in_cached_views(self):
        """``Ship.add_component`` / ``Ship.remove_component`` must surface in
        the cached ``get_all_components`` view on the very next read.

        PROJ-491 Task 1.9: replaces the prior direct
        ``_invalidate_components_cache`` call + ``_components_dirty`` /
        ``_weapons_cache_dirty`` private-flag reads with a behavioral
        assertion on the public Ship API. The cache invalidation is the
        implementation detail; the observable contract is "mutate
        composition via public API, then a subsequent cached read returns
        the updated component set".

        The companion weapon-cache invalidation contract is already
        covered behaviorally by ``test_weapon_cache_invalidates_on_add``
        and ``test_weapon_cache_invalidates_on_remove`` in
        ``TestShipComponentManagerWeaponCache`` above.
        """
        # Populate the all-components cache at its initial (empty) state.
        baseline_all = self.ship.get_all_components()

        # Mutate composition through the public Ship API: add.
        bridge = create_component('bridge', registries=self.registries)
        added = self.ship.add_component(bridge, LayerType.CORE)
        assert added is True

        armor = create_component('armor_plate', registries=self.registries)
        added = self.ship.add_component(armor, LayerType.ARMOR)
        assert added is True

        after_add = self.ship.get_all_components()
        assert bridge in after_add
        assert armor in after_add
        assert len(after_add) == len(baseline_all) + 2, (
            "All-components cached view must reflect freshly-added components."
        )

        # Remove via public API and confirm the cache reflects the removal.
        removed = self.ship.remove_component(LayerType.ARMOR, 0)
        assert removed is armor

        after_remove = self.ship.get_all_components()
        assert armor not in after_remove
        assert bridge in after_remove
        assert len(after_remove) == len(baseline_all) + 1
