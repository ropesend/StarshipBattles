
import unittest
from unittest.mock import MagicMock, patch
import pygame
import sys
import os

# Add project root to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType
from components import Component, LayerType  # Phase 7: Removed Bridge, Armor, Weapon imports

class TestBuilderValidation(unittest.TestCase):
    def setUp(self):
        # Initialize pygame for Vector2
        if not pygame.get_init():
            pygame.init()
            
        # Ensure data is loaded
        from ship import initialize_ship_data
        # Resolve path to project root
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        initialize_ship_data(root_dir)
            
        # Create a standard ship for testing
        # Use Cruiser because it uses Capital_Standard which has INNER layer (Frigate/Escort no longer does)
        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255), ship_class="Cruiser")
        
        # Helper to create component data
        self.base_component_data = {
            "id": "test_comp",
            "name": "Test Component",
            "type": "Component",
            "mass": 10,
            "hp": 100,
            "allowed_layers": ["INNER", "OUTER", "CORE", "ARMOR"],
            "allowed_vehicle_types": ["Ship"],
            "abilities": {}
        }

    def create_component(self, **kwargs):
        data = self.base_component_data.copy()
        data.update(kwargs)
        # Handle allowed_layers if passed as list of strings, Component expects strings in data
        return Component(data)

    def test_layer_restrictions(self):
        """Step 2: Verify layer restrictions are enforced."""
        
        # 1. Test Restriction: Block specific classification
        comp_data = self.base_component_data.copy()
        comp_data["major_classification"] = "Weapons"
        comp = Component(comp_data)
        
        # Inject restriction into INNER layer for this test
        self.ship.layers[LayerType.INNER]['restrictions'].append("block_classification:Weapons")
        
        # Try adding to INNER (Should fail)
        result = self.ship.add_component(comp, LayerType.INNER)
        self.assertFalse(result, "Should not allow Weapons in restricted INNER layer")
        
        # Try adding to OUTER (Should succeed, no restriction)
        result = self.ship.add_component(comp, LayerType.OUTER)
        self.assertTrue(result, "Should allow Weapons in unrestricted OUTER layer")
        
        # 2. Test Allow only restriction (Armor layer)
        armor_comp_data = self.base_component_data.copy()
        armor_comp_data["major_classification"] = "Armor"
        armor_comp = Component(armor_comp_data)
        
        generic_comp = Component(self.base_component_data) # Classification is None or default?
        generic_comp.data['major_classification'] = "Generic"
        
        # Verify ARMOR layer usually has restriction (from ship init)
        # But our ship uses "Frigate" -> "Capital_Escort" which SHOULD have [allow_classification:Armor] now
        
        # Add Armor to ARMOR (Succeed)
        result = self.ship.add_component(armor_comp, LayerType.ARMOR)
        self.assertTrue(result, "Should allow Armor in ARMOR layer")
        
        # Add Generic to ARMOR (Fail)
        result = self.ship.add_component(generic_comp, LayerType.ARMOR)
        self.assertFalse(result, "Should not allow Non-Armor in ARMOR layer")

    def test_unique_flag(self):
        """Step 3a: Test is_unique flag validation."""
        # Create a unique component
        unique_data = self.base_component_data.copy()
        unique_data["id"] = "unique_bridge"
        unique_data["is_unique"] = True # Hypothetical flag
        
        comp1 = Component(unique_data)
        comp2 = Component(unique_data) # Same ID/Definition
        
        # Add first one
        self.ship.add_component(comp1, LayerType.CORE)
        
        # Try to add second one
        # Note: This is expected to fail currently as the logic is likely missing.
        # If add_component returns True, it means the validation is checking this.
        # We assert False to flag if it succeeds (meaning check is missing/failing).
        result = self.ship.add_component(comp2, LayerType.CORE)
        
        if result:
            print("FAIL: is_unique validation missing (duplicate added)")
        
        self.assertFalse(result, "Should not allow duplicate of unique component")

    def test_exclusive_group(self):
        """Step 3b: Test exclusive_group validation."""
        # Define two components in same exclusive group
        group_a_1 = self.base_component_data.copy()
        group_a_1["id"] = "group_a_1"
        group_a_1["exclusive_group"] = "GroupA"
        
        group_a_2 = self.base_component_data.copy()
        group_a_2["id"] = "group_a_2"
        group_a_2["exclusive_group"] = "GroupA"
        
        comp1 = Component(group_a_1)
        comp2 = Component(group_a_2)
        
        self.ship.add_component(comp1, LayerType.INNER)
        
        # Try adding second component from same group
        # Should be rejected OR replace the first. 
        # For now, let's assume rejection for simplicity of test, or check if it replaced.
        result = self.ship.add_component(comp2, LayerType.INNER)
        
        # If accepted, check if comp1 is still there. 
        # If comp1 is there and comp2 is there -> Fail.
        
        has_comp1 = any(c.id == "group_a_1" for c in self.ship.layers[LayerType.INNER]['components'])
        has_comp2 = any(c.id == "group_a_2" for c in self.ship.layers[LayerType.INNER]['components'])
        
        if has_comp1 and has_comp2:
             print("FAIL: exclusive_group validation missing (both assumed)")
             self.fail("Should not allow multiple components from same exclusive group")
             
    def test_component_dependencies(self):
        """Step 4: Test logic that requires specific mounts."""
        # Define a mount and a component requiring it
        mount_data = self.base_component_data.copy()
        mount_data["id"] = "heavy_mount"
        mount_data["mount_type"] = "Heavy"
        mount = Component(mount_data)
        
        weapon_data = self.base_component_data.copy()
        weapon_data["id"] = "heavy_weapon"
        weapon_data["required_mount"] = "Heavy"
        weapon = Component(weapon_data)
        
        # Try adding weapon without mount
        result = self.ship.add_component(weapon, LayerType.OUTER)
        
        if result:
             print("FAIL: Dependency validation missing (weapon added without mount)")
        
        self.assertFalse(result, "Should fail to add component without required mount")
        
        # Add mount then weapon (Logic might require them to be in specific slot or just present?
        # Usually dependencies are slot-based or presence-based. Assuming presence for now if generic.)
        self.ship.add_component(mount, LayerType.OUTER)
        result_with_mount = self.ship.add_component(weapon, LayerType.OUTER)
        # Note: Even if we add mount, if logic is missing, above assert failed already.
        # If logic exists, this should pass.
        
    def test_mass_validation(self):
        """Step 5a: Test complex mass addition boundary condition."""
        # Patch VEHICLE_CLASSES to enforce a small limit for the 'Cruiser' class
        with patch('ship.VEHICLE_CLASSES', {"Cruiser": {"max_mass": 100, "hull_mass": 0, "layers": []}}):
            # Re-init ship to pick up new class limit
            self.ship = Ship("Test Ship", 0, 0, (255, 255, 255), ship_class="Cruiser")
            # Force explicit override just in case update overwrites it with 100
            self.ship.max_mass_budget = 100
             
            # Add component of mass 60
            comp1 = self.create_component(mass=60)
            self.assertTrue(self.ship.add_component(comp1, LayerType.INNER))
            
            # Add component of mass 40 (Total 100 == Limit)
            comp2 = self.create_component(mass=40)
            self.assertTrue(self.ship.add_component(comp2, LayerType.INNER), "Should allow exact match of mass budget")
            
            # Add component of mass 1 (Total 101 > Limit)
            comp3 = self.create_component(mass=1)
            self.assertFalse(self.ship.add_component(comp3, LayerType.INNER), "Should reject mass exceeding budget")
        
    def test_ability_restrictions(self):
        """Step 6: Test ability-based restrictions (allow_ability/deny_ability)."""
        # Create a component with 'WeaponAbility'
        weapon_data = self.base_component_data.copy()
        weapon_data["abilities"] = {"WeaponAbility": {"damage": 10}}
        weapon = Component(weapon_data)
        
        # Create a component with 'ShieldProjection'
        shield_data = self.base_component_data.copy()
        shield_data["abilities"] = {"ShieldProjection": {"capacity": 100}}
        shield = Component(shield_data)
        
        # 1. Test allow_ability
        # Inject restriction: Only allow components with WeaponAbility in OUTER
        self.ship.layers[LayerType.OUTER]['restrictions'] = ["allow_ability:WeaponAbility"]
        
        # Add Weapon (Should pass)
        self.assertTrue(self.ship.add_component(weapon, LayerType.OUTER), "Should allow component with allowed ability")
        
        # Add Shield (Should fail)
        self.assertFalse(self.ship.add_component(shield, LayerType.OUTER), "Should deny component without allowed ability")
        
        # 2. Test deny_ability
        # Inject restriction: Deny ShieldProjection in INNER
        self.ship.layers[LayerType.INNER]['restrictions'] = ["deny_ability:ShieldProjection"]
        
        # Add Weapon (Should pass - not denied)
        self.assertTrue(self.ship.add_component(weapon, LayerType.INNER), "Should allow component without denied ability")
        
        # Add Shield (Should fail - denied)
        self.assertFalse(self.ship.add_component(shield, LayerType.INNER), "Should deny component with denied ability")
        
    def test_symmetry_enforcement(self):
        """Step 5b: Test symmetry enforcement (if enabled)."""
        # Symmetry is usually a Builder UI feature, not strict Ship validation?
        # But if valid_ship() checks symmetry, we test it here.
        # Checking ship.py, there is no symmetry check in check_validity().
        # So this test checks for a feature likely essentially missing in backend validation.
        
        # We'll just define the test structure.
        pass

    def test_block_id_restriction(self):
        """Step 7: Verify block_id restriction."""
        # Inject restriction: Block 'test_comp'
        self.ship.layers[LayerType.INNER]['restrictions'].append("block_id:test_comp")
        
        comp = self.create_component(id="test_comp")
        other_comp = self.create_component(id="other_comp")
        
        # Test Blocked
        self.assertFalse(self.ship.add_component(comp, LayerType.INNER), "Should block specific ID")
        
        # Test Allowed
        self.assertTrue(self.ship.add_component(other_comp, LayerType.INNER), "Should allow other IDs")


class TestComplexRules(unittest.TestCase):
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        # Initialize ship logic
        from ship import initialize_ship_data, Ship
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        initialize_ship_data(root_dir)
        
        self.ship = Ship("Complex Test Ship", 0, 0, (255, 255, 255), ship_class="Cruiser")
        
        from ship_validator import ShipDesignValidator
        self.validator = ShipDesignValidator()

    def create_component_with_abilities(self, abilities: dict, name="Test Comp"):
        data = {
            "id": name.lower().replace(" ", "_"),
            "name": name,
            "type": "Component",
            "mass": 10,
            "hp": 100,
            "allowed_layers": ["INNER", "OUTER"],
            "allowed_vehicle_types": ["Ship"],
            "abilities": abilities
        }
        return Component(data)

    def test_class_requirements(self):
        """Verify ClassRequirementsRule (Crew/LifeSupport)."""
        # Patch VEHICLE_CLASSES locally to force requirements
        mock_classes = {
            "Cruiser": {
                "max_mass": 1000, 
                "requirements": {
                    "req_crew": {"ability": "CrewRequired", "min_value": 0} # Just tracking
                }
            }
        }
        
        # We need to test the logic in ClassRequirementsRule.validate
        # It calculates totals from components.
        
        # Case 1: Insufficient Crew Housing
        # Component needing 10 Crew
        bridge = self.create_component_with_abilities(
            {"CrewRequired": 10}, 
            name="Bridge"
        )
        
        # Quarters providing 5 Crew
        quarters = self.create_component_with_abilities(
            {"CrewCapacity": 5}, 
            name="Quarters"
        )
        
        self.ship.add_component(bridge, LayerType.INNER)
        self.ship.add_component(quarters, LayerType.INNER)
        
        # Run validation
        result = self.validator.validate_design(self.ship)
        
        # Should have error about crew housing (Need 5 more)
        # Note: ClassRequirementsRule logic: if crew_capacity < crew_required
        
        # To make this deterministic, we need to ensure our mocked vehicle classes are used.
        # But ShipDesignValidator imports VEHICLE_CLASSES from ship.
        # So we patch it there.
        with patch('ship.VEHICLE_CLASSES', mock_classes):
             result = self.validator.validate_design(self.ship)
             
        # Check errors
        found_crew_error = any("more crew housing" in e for e in result.errors)
        self.assertTrue(found_crew_error, f"Should report crew housing shortage. Errors: {result.errors}")
        
        # Case 2: Insufficient Life Support
        # Logic: life_support < crew_required
        # We have 5 capacity, 10 required.
        # Add Life Support for 8 people.
        life_support = self.create_component_with_abilities(
            {"LifeSupportCapacity": 8}, 
            name="LifeSupport"
        )
        self.ship.add_component(life_support, LayerType.INNER)
        
        with patch('ship.VEHICLE_CLASSES', mock_classes):
             result = self.validator.validate_design(self.ship)
             
        # Crew Housing: 5 cap < 10 req -> Error
        # Life Support: 8 cap < 10 req -> Error
        found_ls_error = any("more life support" in e for e in result.errors)
        self.assertTrue(found_ls_error, f"Should report life support shortage. Errors: {result.errors}")

    def test_resource_dependency(self):
        """Verify ResourceDependencyRule (Ammo/Fuel)."""
        
        # Case 1: Ammo Consumer without Storage
        weapon = self.create_component_with_abilities(
            {"ResourceConsumption": [{"resource": "ammo", "amount": 1}]},
            name="Cannon"
        )
        self.ship.add_component(weapon, LayerType.OUTER)
        
        result = self.validator.validate_design(self.ship)
        
        found_ammo_warn = any("Needs Ammo Storage" in w for w in result.warnings)
        self.assertTrue(found_ammo_warn, f"Should warn about missing ammo storage. Warnings: {result.warnings}")
        
        # Case 2: Add Ammo Storage
        magazine = self.create_component_with_abilities(
            {"ResourceStorage": [{"resource": "ammo", "amount": 100}]},
            name="Magazine"
        )
        self.ship.add_component(magazine, LayerType.INNER)
        
        result = self.validator.validate_design(self.ship)
        found_ammo_warn = any("Needs Ammo Storage" in w for w in result.warnings)
        self.assertFalse(found_ammo_warn, "Should NOT warn when ammo storage is present")

if __name__ == '__main__':
    unittest.main()
