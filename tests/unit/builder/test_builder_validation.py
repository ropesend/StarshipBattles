import pytest
from unittest.mock import MagicMock

from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component
from game.core.constants import LayerType  # Phase 7: Removed Bridge, Armor, Weapon imports
from tests.fixtures.paths import get_project_root


class TestBuilderValidation:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, fresh_registries):
        # Ensure data is loaded
        from game.simulation.entities.ship_loader import initialize_ship_data
        initialize_ship_data(str(get_project_root()))

        # Store registries for use in tests
        self.registries = fresh_registries

        # Create a standard ship for testing
        # Use Cruiser because it uses Capital_Standard which has INNER layer (Frigate/Escort no longer does)
        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255), ship_class="Cruiser", registries=fresh_registries)

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

        yield

    def create_component(self, **kwargs):
        data = self.base_component_data.copy()
        data.update(kwargs)
        # Handle allowed_layers if passed as list of strings, Component expects strings in data
        return Component(data, registries=self.registries)

    def test_layer_restrictions(self):
        """Step 2: Verify layer restrictions are enforced."""

        # 1. Test Restriction: Block specific classification
        comp_data = self.base_component_data.copy()
        comp_data["major_classification"] = "Weapons"
        comp = Component(comp_data, registries=self.registries)

        # Inject restriction into INNER layer for this test
        self.ship.layers[LayerType.INNER].restrictions.append("block_classification:Weapons")

        # Try adding to INNER (Should fail)
        result = self.ship.add_component(comp, LayerType.INNER)
        assert not result, "Should not allow Weapons in restricted INNER layer"

        # Try adding to OUTER (Should succeed, no restriction)
        result = self.ship.add_component(comp, LayerType.OUTER)
        assert result, "Should allow Weapons in unrestricted OUTER layer"

        # 2. Test Allow only restriction (Armor layer)
        armor_comp_data = self.base_component_data.copy()
        armor_comp_data["major_classification"] = "Armor"
        armor_comp = Component(armor_comp_data, registries=self.registries)

        generic_comp = Component(self.base_component_data, registries=self.registries) # Classification is None or default?
        generic_comp.data['major_classification'] = "Generic"

        # Verify ARMOR layer usually has restriction (from ship init)
        # But our ship uses "Frigate" -> "Capital_Escort" which SHOULD have [allow_classification:Armor] now

        # Add Armor to ARMOR (Succeed)
        result = self.ship.add_component(armor_comp, LayerType.ARMOR)
        assert result, "Should allow Armor in ARMOR layer"

        # Add Generic to ARMOR (Fail)
        result = self.ship.add_component(generic_comp, LayerType.ARMOR)
        assert not result, "Should not allow Non-Armor in ARMOR layer"

    def test_unique_flag(self):
        """Step 3a: Test is_unique flag validation."""
        # Create a unique component
        unique_data = self.base_component_data.copy()
        unique_data["id"] = "unique_bridge"
        unique_data["is_unique"] = True # Hypothetical flag

        comp1 = Component(unique_data, registries=self.registries)
        comp2 = Component(unique_data, registries=self.registries) # Same ID/Definition

        # Add first one
        self.ship.add_component(comp1, LayerType.CORE)

        # Try to add second one
        # Note: This is expected to fail currently as the logic is likely missing.
        # If add_component returns True, it means the validation is checking this.
        # We assert False to flag if it succeeds (meaning check is missing/failing).
        result = self.ship.add_component(comp2, LayerType.CORE)

        assert not result, "Should not allow duplicate of unique component"

    def test_exclusive_group(self):
        """Step 3b: Test exclusive_group validation."""
        # Define two components in same exclusive group
        group_a_1 = self.base_component_data.copy()
        group_a_1["id"] = "group_a_1"
        group_a_1["exclusive_group"] = "GroupA"

        group_a_2 = self.base_component_data.copy()
        group_a_2["id"] = "group_a_2"
        group_a_2["exclusive_group"] = "GroupA"

        comp1 = Component(group_a_1, registries=self.registries)
        comp2 = Component(group_a_2, registries=self.registries)

        self.ship.add_component(comp1, LayerType.INNER)

        # Try adding second component from same group
        # Should be rejected OR replace the first.
        # For now, let's assume rejection for simplicity of test, or check if it replaced.
        result = self.ship.add_component(comp2, LayerType.INNER)

        # If accepted, check if comp1 is still there.
        # If comp1 is there and comp2 is there -> Fail.

        # PROJ-323 Task 5.12: pre-compute id-set once instead of two `any(...)` scans.
        inner_component_ids = {c.id for c in self.ship.layers[LayerType.INNER].components}
        assert not {"group_a_1", "group_a_2"}.issubset(inner_component_ids), (
            "Should not allow multiple components from same exclusive group"
        )

    def test_component_dependencies(self):
        """Step 4: Test logic that requires specific mounts."""
        # Define a mount and a component requiring it
        mount_data = self.base_component_data.copy()
        mount_data["id"] = "heavy_mount"
        mount_data["mount_type"] = "Heavy"
        mount = Component(mount_data, registries=self.registries)

        weapon_data = self.base_component_data.copy()
        weapon_data["id"] = "heavy_weapon"
        weapon_data["required_mount"] = "Heavy"
        weapon = Component(weapon_data, registries=self.registries)

        # Try adding weapon without mount
        result = self.ship.add_component(weapon, LayerType.OUTER)

        assert not result, "Should fail to add component without required mount"

        # Add mount then weapon (Logic might require them to be in specific slot or just present?
        # Usually dependencies are slot-based or presence-based. Assuming presence for now if generic.)
        self.ship.add_component(mount, LayerType.OUTER)
        result_with_mount = self.ship.add_component(weapon, LayerType.OUTER)
        # Note: Even if we add mount, if logic is missing, above assert failed already.
        # If logic exists, this should pass.

    def test_mass_validation(self):
        """Step 5a: Test complex mass addition boundary condition."""
        # Save original vehicle_classes and modify in-place
        original_classes = dict(self.registries.vehicle_classes)
        self.registries.vehicle_classes.clear()
        self.registries.vehicle_classes.update({"Cruiser": {"max_mass": 100, "layers": []}})
        try:
            # Re-init ship to pick up new class limit
            self.ship = Ship("Test Ship", 0, 0, (255, 255, 255), ship_class="Cruiser", registries=self.registries)
            # Force explicit override just in case update overwrites it with 100
            self.ship.max_mass_budget = 100

            # Add component of mass 60
            comp1 = self.create_component(mass=60)
            assert self.ship.add_component(comp1, LayerType.INNER)

            # Add component of mass 40 (Total 100 == Limit)
            comp2 = self.create_component(mass=40)
            assert self.ship.add_component(comp2, LayerType.INNER), "Should allow exact match of mass budget"

            # Add component of mass 1 (Total 101 > Limit) — placement allowed, mass warning shown
            comp3 = self.create_component(mass=1)
            assert self.ship.add_component(comp3, LayerType.INNER), "Should allow placement even over mass budget"
            assert not self.ship.mass_limits_ok, "Should flag mass_limits_ok as False"
        finally:
            # Restore original vehicle_classes
            self.registries.vehicle_classes.clear()
            self.registries.vehicle_classes.update(original_classes)

    def test_ability_restrictions(self):
        """Step 6: Test ability-based restrictions (allow_ability/deny_ability)."""
        # Create a component with 'WeaponAbility'
        weapon_data = self.base_component_data.copy()
        weapon_data["abilities"] = {"WeaponAbility": {"damage": 10}}
        weapon = Component(weapon_data, registries=self.registries)

        # Create a component with 'ShieldProjection'
        shield_data = self.base_component_data.copy()
        shield_data["abilities"] = {"ShieldProjection": {"capacity": 100}}
        shield = Component(shield_data, registries=self.registries)

        # 1. Test allow_ability
        # Inject restriction: Only allow components with WeaponAbility in OUTER
        self.ship.layers[LayerType.OUTER].restrictions = ["allow_ability:WeaponAbility"]

        # Add Weapon (Should pass)
        assert self.ship.add_component(weapon, LayerType.OUTER), "Should allow component with allowed ability"

        # Add Shield (Should fail)
        assert not self.ship.add_component(shield, LayerType.OUTER), "Should deny component without allowed ability"

        # 2. Test deny_ability
        # Inject restriction: Deny ShieldProjection in INNER
        self.ship.layers[LayerType.INNER].restrictions = ["deny_ability:ShieldProjection"]

        # Add Weapon (Should pass - not denied)
        assert self.ship.add_component(weapon, LayerType.INNER), "Should allow component without denied ability"

        # Add Shield (Should fail - denied)
        assert not self.ship.add_component(shield, LayerType.INNER), "Should deny component with denied ability"

    def test_block_id_restriction(self):
        """Step 7: Verify block_id restriction."""
        # Inject restriction: Block 'test_comp'
        self.ship.layers[LayerType.INNER].restrictions.append("block_id:test_comp")

        comp = self.create_component(id="test_comp")
        other_comp = self.create_component(id="other_comp")

        # Test Blocked
        assert not self.ship.add_component(comp, LayerType.INNER), "Should block specific ID"

        # Test Allowed
        assert self.ship.add_component(other_comp, LayerType.INNER), "Should allow other IDs"


class TestComplexRules:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, fresh_registries):
        # Initialize ship logic
        from game.simulation.entities.ship import Ship
        from game.simulation.entities.ship_loader import initialize_ship_data
        initialize_ship_data(str(get_project_root()))

        # Store registries for use in tests
        self.registries = fresh_registries

        self.ship = Ship("Complex Test Ship", 0, 0, (255, 255, 255), ship_class="Cruiser", registries=fresh_registries)

        from game.simulation.validation.ship_validator import ShipDesignValidator
        self.validator = ShipDesignValidator(registries=fresh_registries)

        yield

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
        return Component(data, registries=self.registries)

    def test_class_requirements(self):
        """Verify ClassRequirementsRule validates the maintenance + crew-needs-LS rules.

        QA Observation 5 maintenance abstraction: the old crew-housing-vs-required
        check is replaced by (a) a hard crew-needs-life-support rule and (b) a
        maintenance rule comparing RequiresMaintenance vs ProvidesMaintenance.
        """

        # Case 1: Insufficient Maintenance
        bridge = self.create_component_with_abilities(
            {"RequiresMaintenance": 10},
            name="Bridge"
        )
        # Quarters provides only 5 maintenance (and 5 crew, with no LS).
        quarters = self.create_component_with_abilities(
            {"CrewCapacity": 5, "ProvidesMaintenance": 5},
            name="Quarters"
        )
        self.ship.add_component(bridge, LayerType.INNER)
        self.ship.add_component(quarters, LayerType.INNER)

        result = self.validator.validate_design(self.ship)

        # Crew-needs-LS rule: 5 crew capacity but 0 life support → error.
        found_crew_ls_error = any(
            "life support" in e.lower() and "crew" in e.lower()
            for e in result.errors
        )
        assert found_crew_ls_error, (
            f"Should report crew-without-life-support. Errors: {result.errors}"
        )

        # Maintenance rule: 10 required, 5 provided → error.
        found_maint_error = any("maintenance" in e.lower() for e in result.errors)
        assert found_maint_error, (
            f"Should report maintenance shortage. Errors: {result.errors}"
        )

        # Case 2: Add enough life support and enough maintenance providers.
        life_support = self.create_component_with_abilities(
            {"LifeSupportCapacity": 20},
            name="LifeSupport"
        )
        extra_maint = self.create_component_with_abilities(
            {"ProvidesMaintenance": 10},
            name="ExtraMaint"
        )
        self.ship.add_component(life_support, LayerType.INNER)
        self.ship.add_component(extra_maint, LayerType.INNER)

        result = self.validator.validate_design(self.ship)
        joined = " ".join(result.errors).lower()
        assert "maintenance" not in joined, (
            f"Maintenance should now be satisfied. Errors: {result.errors}"
        )
        assert "life support" not in joined, (
            f"Crew-needs-LS should now pass. Errors: {result.errors}"
        )

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
        assert found_ammo_warn, f"Should warn about missing ammo storage. Warnings: {result.warnings}"

        # Case 2: Add Ammo Storage
        magazine = self.create_component_with_abilities(
            {"ResourceStorage": [{"resource": "ammo", "amount": 100}]},
            name="Magazine"
        )
        self.ship.add_component(magazine, LayerType.INNER)

        result = self.validator.validate_design(self.ship)
        found_ammo_warn = any("Needs Ammo Storage" in w for w in result.warnings)
        assert not found_ammo_warn, "Should NOT warn when ammo storage is present"


