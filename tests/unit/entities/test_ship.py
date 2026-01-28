"""
Tests for Ship entity behavior.

PROJ-38: Migrated key fixtures to use fresh_registries for cleaner test setup.
"""
import pytest
import pygame

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import Component, load_components, create_component
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_project_root, get_data_dir


class TestShip:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, fresh_registries):
        """Set up registry data for tests.

        PROJ-38: Uses fresh_registries fixture for data, then hydrates singleton.
        """
        # Hydrate registry singleton from fresh_registries fixture data
        mgr = RegistryManager.instance()
        mgr.hydrate(
            fresh_registries.components,
            fresh_registries.modifiers,
            fresh_registries.vehicle_classes
        )

        yield

        # Note: reset_singletons fixture in conftest.py handles cleanup
        if pygame.get_init():
            pygame.quit()

    def test_add_component_constraints(self):
        ship = Ship("TestShip", 0, 0, (255, 255, 255))

        # Bridge is allowed in CORE
        bridge = create_component('bridge')
        ship.add_component(bridge, LayerType.CORE)
        assert bridge in ship.layers[LayerType.CORE]['components']

        # Railgun allowed in OUTER. Try adding to CORE (should fail or be allowed if logic checks?)
        # Ship.add_component definition:
        # if not layer_type in component.allowed_layers: return False
        railgun = create_component('railgun') # allowed: OUTER
        result = ship.add_component(railgun, LayerType.CORE)
        assert result is False, "Should not allow Railgun in CORE"

        result_ok = ship.add_component(railgun, LayerType.OUTER)
        assert result_ok is True

    def test_mass_calculation(self):
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        # Initial mass: Ships now auto-equip Hull component (50 mass for Escort)
        # Hull is added in __init__ but current_mass not updated until recalculate_stats
        ship.recalculate_stats()  # Trigger calculation
        assert ship.current_mass == 50  # Hull mass

        bridge = create_component('bridge') # 50
        ship.add_component(bridge, LayerType.CORE)
        assert ship.current_mass == 100  # Hull (50) + Bridge (50)

    def test_damage_armor_absorption(self):
        # Inject TestShip definition strictly
        RegistryManager.instance().vehicle_classes["TestShip"] = {
            "default_hull_id": "hull_escort", "max_mass": 1000,
            "layers": [
                {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 0.5},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.5}
            ]
        }

        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        # ship._initialize_layers() # Ship init calls this, and it sees the new class def logic

        # Add Armor Plate (250 HP) to ARMOR layer
        armor = create_component('armor_plate')
        ship.add_component(armor, LayerType.ARMOR)

        # Add Bridge (200 HP) to CORE - requires crew to be active
        bridge = create_component('bridge')
        ship.add_component(bridge, LayerType.CORE)

        # Add crew support so bridge is active and can receive damage
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)

        ship.recalculate_stats()
        assert bridge.is_active is True, "Bridge should be active with crew support"

        # Apply 100 damage (Should be absorbed by Armor)
        ship.take_damage(100)

        assert armor.current_hp == 150
        assert bridge.current_hp == 200  # Bridge untouched

        # Apply 200 damage (overflows armor by 50)
        # Armor has 150 left. 200 - 150 = 50 overflow to next layers.
        # Next is OUTER (empty), INNER (empty), CORE (Bridge + crew_quarters + life_support).
        # Damage is dealt to a random component - if that component has less HP than
        # the damage, the remaining damage continues to next random component.
        # Note: With current damage mechanics, one component takes as much as it can absorb.
        ship.take_damage(200)

        assert armor.current_hp == 0
        assert armor.is_active is False
        # 50 damage should be distributed to CORE components
        # Due to random selection and HP caps, verify total damage absorbed is correct
        core_hp_lost = sum(c.max_hp - c.current_hp for c in ship.layers[LayerType.CORE]['components'])
        assert core_hp_lost >= 40, f"At least 40 HP should be lost in CORE (got {core_hp_lost})"
        assert core_hp_lost <= 50, f"At most 50 HP should be lost in CORE (got {core_hp_lost})"

    def test_serialization(self):
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        # Add components (Hull is auto-equipped already)
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('railgun'), LayerType.OUTER)

        data = ship.to_dict()

        assert data['name'] == "TestShip"
        assert "layers" in data
        assert "CORE" in data["layers"]
        assert len(data["layers"]["CORE"]) > 0

        # Reconstruct
        new_ship = Ship.from_dict(data)

        assert new_ship.name == "TestShip"
        # HULL: Hull (auto-equipped) = 1 component
        # CORE: Bridge (from data) = 1 component
        assert len(new_ship.layers[LayerType.HULL]['components']) == 1
        assert len(new_ship.layers[LayerType.CORE]['components']) == 1
        assert len(new_ship.layers[LayerType.OUTER]['components']) == 1
        # Check Bridge is present
        bridge_found = any(c.type_str == 'Bridge' for c in new_ship.layers[LayerType.CORE]['components'])
        assert bridge_found is True, "Bridge component should be in CORE layer"


class TestShipClassMutation:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, fresh_registries):
        """Set up registry data for class mutation tests.

        PROJ-38: Uses fresh_registries fixture for data, then hydrates singleton.
        """
        if not pygame.get_init():
            pygame.init()

        # Hydrate registry singleton from fresh_registries fixture data
        mgr = RegistryManager.instance()
        mgr.hydrate(
            fresh_registries.components,
            fresh_registries.modifiers,
            fresh_registries.vehicle_classes
        )

        self.ship = Ship("Mutation Test", 0, 0, (255, 255, 255), ship_class="Frigate")
        yield

        # Note: reset_singletons fixture in conftest.py handles cleanup
        if pygame.get_init():
            pygame.quit()

    def test_change_class_migration(self):
        """Verify components migrate or are removed during class change."""
        # Add components to Frigate
        bridge = create_component('bridge')
        self.ship.add_component(bridge, LayerType.CORE)

        railgun = create_component('railgun')
        self.ship.add_component(railgun, LayerType.OUTER)

        # Change to "Destroyer" with migration
        self.ship.change_class("Destroyer", migrate_components=True)

        # Verify components remained
        assert self.ship.ship_class == "Destroyer"

        # Helper to find component in layer
        def has_comp(layer_type, comp):
            return comp in self.ship.layers[layer_type]['components']

        assert has_comp(LayerType.CORE, bridge) is True
        assert has_comp(LayerType.OUTER, railgun) is True

    def test_derelict_status_logic(self):
        """
        Verify is_derelict update logic when key components are destroyed.

        The new data-driven system:
        - Ships with hulls have RequiresCommandAndControl ability
        - Ships only become derelict if they have components requiring command
        - CommandAndControl is provided by bridges or similar components
        - Destroying all command components makes the ship derelict
        """
        # Frigate ships automatically get a hull with RequiresCommandAndControl ability
        # Verify the ship requires command and control
        requires_command = self.ship.get_total_ability_value('RequiresCommandAndControl')
        assert requires_command > 0, "Frigate hull should require CommandAndControl"

        # Add bridge to provide CommandAndControl
        bridge = create_component('bridge')
        self.ship.add_component(bridge, LayerType.CORE)

        # Add crew support to keep bridge operational
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)

        # Recalculate and verify ship is operational
        self.ship.recalculate_stats()
        self.ship.update_derelict_status()
        assert self.ship.is_derelict is False, "Ship should be operational with active bridge"

        # Verify bridge provides CommandAndControl
        has_command = self.ship.get_total_ability_value('CommandAndControl', operational_only=True)
        assert has_command > 0, "Bridge should provide CommandAndControl"

        # Destroy the bridge
        bridge.current_hp = 0
        bridge.is_active = False

        # Update status and verify ship becomes derelict
        self.ship.recalculate_stats()
        self.ship.update_derelict_status()

        # Verify no operational command remaining
        has_command_after = self.ship.get_total_ability_value('CommandAndControl', operational_only=True)
        assert has_command_after == 0, "No CommandAndControl should remain after bridge destruction"

        # Ship should now be derelict
        assert self.ship.is_derelict is True, "Ship should be derelict after losing all CommandAndControl"


# --- Pytest-style Tests (merged from test_ship_core.py) ---

@pytest.fixture
def registry_with_hull():
    """
    Populate RegistryManager with Escort class and its hull_escort component.
    Uses use_custom_data marker to skip production hydration.
    """
    mgr = RegistryManager.instance()
    mgr.clear()  # Ensure clean state before populating

    # Vehicle class with default_hull_id
    mgr.vehicle_classes.update({
        "Escort": {
            "type": "Ship",
            "max_mass": 1000,
            "default_hull_id": "hull_escort",
            "layers": [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []},
                {"type": "OUTER", "radius_pct": 0.5, "restrictions": []},
            ]
        }
    })

    # Hull component - must be a Component instance with clone() method
    hull_data = {
        "id": "hull_escort",
        "name": "Escort Hull",
        "type": "Hull",
        "mass": 50,
        "hp": 100,
        "abilities": {
            "HullComponent": True,
            "RequiresCommandAndControl": True
        }
    }
    hull_component = Component(hull_data)
    mgr.components["hull_escort"] = hull_component

    yield mgr
    mgr.clear()  # Clean up after test


@pytest.fixture
def ship_with_components(registry_with_hull):
    """Create a Ship with known components for mass/HP verification."""
    mgr = registry_with_hull

    # Add a simple Armor component
    armor_data = {
        "id": "test_armor",
        "name": "Test Armor",
        "type": "Armor",
        "mass": 25,
        "hp": 50,
        "abilities": {}
    }
    armor_component = Component(armor_data)
    mgr.components["test_armor"] = armor_component

    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="Escort")

    # Add armor component to OUTER layer
    armor = create_component("test_armor")
    if armor:
        ship.add_component(armor, LayerType.OUTER)

    ship.recalculate_stats()
    return ship


class TestHullAutoEquip:
    """TC-3.2.1: Hull Auto-Equip Verification"""

    def test_hull_auto_equip(self, registry_with_hull):
        """Verify Ship auto-equips default_hull_id from vehicle class."""
        ship = Ship(name="Test", x=0, y=0, color=(255, 255, 255), ship_class="Escort")

        hull_comps = ship.layers[LayerType.HULL]['components']
        assert len(hull_comps) >= 1, "Expected at least 1 component in HULL layer"

        # Find the hull component
        hull_comp = next((c for c in hull_comps if c.id == "hull_escort"), None)
        assert hull_comp is not None, "hull_escort should be auto-equipped to HULL layer"

        # Attribute Shadowing: base_mass should be 0 when hull is equipped
        assert ship.base_mass == 0.0, "base_mass should be 0 when Hull component is equipped"


class TestMassAggregation:
    """TC-3.2.3: Mass Aggregation"""

    def test_mass_from_components(self, ship_with_components):
        """Verify Ship.mass equals sum of all component masses + base_mass."""
        ship = ship_with_components

        # Calculate expected mass using helper method
        component_mass = sum(c.mass for c in ship.get_all_components())
        expected_mass = ship.base_mass + component_mass

        # Ship.mass should match
        assert ship.mass == expected_mass, f"Ship.mass ({ship.mass}) != expected ({expected_mass})"


class TestHPAggregation:
    """TC-3.2.4: HP Aggregation"""

    def test_hp_from_components(self, ship_with_components):
        """Verify Ship.max_hp equals sum of component max_hp values."""
        ship = ship_with_components

        # Use helper method for iteration
        expected_hp = sum(c.max_hp for c in ship.get_all_components())

        assert ship.max_hp == expected_hp, f"Ship.max_hp ({ship.max_hp}) != expected ({expected_hp})"


class TestChangeClassInvalidInput:
    """Test Ship.change_class() with invalid inputs.

    Regression test for PROJ-12 Phase 7 Fix 7.3:
    Local import at line 435 shadowed module-level import, causing
    UnboundLocalError when log_error was called at line 417.
    """

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, fresh_registries):
        """Set up registry data for invalid input tests.

        PROJ-38: Uses fresh_registries fixture for data, then hydrates singleton.
        """
        if not pygame.get_init():
            pygame.init()

        # Hydrate registry singleton from fresh_registries fixture data
        mgr = RegistryManager.instance()
        mgr.hydrate(
            fresh_registries.components,
            fresh_registries.modifiers,
            fresh_registries.vehicle_classes
        )

        yield

        # Note: reset_singletons fixture in conftest.py handles cleanup
        if pygame.get_init():
            pygame.quit()

    def test_change_class_invalid_class_name_does_not_raise(self):
        """Verify change_class() with invalid class name handles error gracefully.

        Prior to fix, this would raise UnboundLocalError due to local import shadowing.
        """
        ship = Ship("Test", 0, 0, (255, 255, 255), ship_class="Frigate")
        original_class = ship.ship_class

        # This should NOT raise UnboundLocalError - just log error and return
        ship.change_class("NonExistentClassXYZ")

        # Ship class should remain unchanged since the new class doesn't exist
        assert ship.ship_class == original_class
