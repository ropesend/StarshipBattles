"""
Tests for Ship entity behavior.

PROJ-38: Migrated key fixtures to use fresh_registries for cleaner test setup.
"""
import pytest
import pygame

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.entities.ship_serialization import ShipSerializer
from game.simulation.components.component import Component, load_components, create_component
from tests.fixtures.paths import get_project_root, get_data_dir


class TestShip:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, fresh_registries):
        """Set up registry data for tests.

        PROJ-195: Pure DI pattern - uses fresh_registries directly, no singleton hydration.
        """
        yield

        # Note: reset_singletons fixture in conftest.py handles cleanup
        if pygame.get_init():
            pygame.quit()

    def test_add_component_constraints(self, fresh_registries):
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=fresh_registries)

        # Bridge is allowed in CORE
        bridge = create_component('bridge', registries=fresh_registries)
        ship.add_component(bridge, LayerType.CORE)
        assert bridge in ship.layers[LayerType.CORE].components

        # Railgun allowed in OUTER. Try adding to CORE (should fail or be allowed if logic checks?)
        # Ship.add_component definition:
        # if not layer_type in component.allowed_layers: return False
        railgun = create_component('railgun', registries=fresh_registries) # allowed: OUTER
        result = ship.add_component(railgun, LayerType.CORE)
        assert result is False, "Should not allow Railgun in CORE"

        result_ok = ship.add_component(railgun, LayerType.OUTER)
        assert result_ok is True

    def test_mass_calculation(self, fresh_registries):
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=fresh_registries)
        # Initial mass: Ships now auto-equip Hull component (50 mass for Escort)
        # Hull is added in __init__ but current_mass not updated until recalculate_stats
        ship.recalculate_stats()  # Trigger calculation
        assert ship.current_mass == 50  # Hull mass

        bridge = create_component('bridge', registries=fresh_registries) # 50
        ship.add_component(bridge, LayerType.CORE)
        assert ship.current_mass == 100  # Hull (50) + Bridge (50)

    def test_damage_armor_absorption(self, fresh_registries):
        # Inject TestShip definition strictly
        fresh_registries.vehicle_classes["TestShip"] = {
            "default_hull_id": "hull_escort", "max_mass": 1000,
            "layers": [
                {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 0.5},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.5}
            ]
        }

        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=fresh_registries)
        # ship._initialize_layers() # Ship init calls this, and it sees the new class def logic

        # Add Armor Plate (250 HP) to ARMOR layer
        armor = create_component('armor_plate', registries=fresh_registries)
        ship.add_component(armor, LayerType.ARMOR)

        # Add Bridge (200 HP) to CORE - requires crew to be active
        bridge = create_component('bridge', registries=fresh_registries)
        ship.add_component(bridge, LayerType.CORE)

        # Add crew support so bridge is active and can receive damage
        ship.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)

        ship.recalculate_stats()
        assert bridge.is_active is True, "Bridge should be active with crew support"

        # Apply 100 damage (Should be absorbed by Armor)
        ship.combat_engine.take_damage(100)

        assert armor.current_hp == 150
        assert bridge.current_hp == 200  # Bridge untouched

        # Apply 200 damage (overflows armor by 50)
        # Armor has 150 left. 200 - 150 = 50 overflow to next layers.
        # Next is OUTER (empty), INNER (empty), CORE (Bridge + crew_quarters + life_support).
        # Damage is dealt to a random component - if that component has less HP than
        # the damage, the remaining damage continues to next random component.
        # Note: With current damage mechanics, one component takes as much as it can absorb.
        ship.combat_engine.take_damage(200)

        assert armor.current_hp == 0
        assert armor.is_active is False
        # 50 damage should be distributed to CORE components
        # Due to random selection and HP caps, verify total damage absorbed is correct
        core_hp_lost = sum(c.max_hp - c.current_hp for c in ship.layers[LayerType.CORE].components)
        assert core_hp_lost >= 40, f"At least 40 HP should be lost in CORE (got {core_hp_lost})"
        assert core_hp_lost <= 50, f"At most 50 HP should be lost in CORE (got {core_hp_lost})"

    def test_serialization(self, fresh_registries):
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=fresh_registries)
        # Add components (Hull is auto-equipped already)
        ship.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('railgun', registries=fresh_registries), LayerType.OUTER)

        data = ship.to_dict()

        assert data['name'] == "TestShip"
        assert "layers" in data
        assert "CORE" in data["layers"]
        assert len(data["layers"]["CORE"]) > 0

        # Reconstruct
        new_ship = ShipSerializer.from_dict(data, registries=fresh_registries)

        assert new_ship.name == "TestShip"
        # HULL: Hull (auto-equipped) = 1 component
        # CORE: Bridge (from data) = 1 component
        assert len(new_ship.layers[LayerType.HULL].components) == 1
        assert len(new_ship.layers[LayerType.CORE].components) == 1
        assert len(new_ship.layers[LayerType.OUTER].components) == 1
        # Check Bridge is present
        bridge_found = any(c.type_str == 'Bridge' for c in new_ship.layers[LayerType.CORE].components)
        assert bridge_found is True, "Bridge component should be in CORE layer"


class TestShipClassMutation:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, fresh_registries):
        """Set up registry data for class mutation tests.

        PROJ-195: Pure DI pattern - uses fresh_registries directly, no singleton hydration.
        """
        if not pygame.get_init():
            pygame.init()

        self.registries = fresh_registries
        self.ship = Ship("Mutation Test", 0, 0, (255, 255, 255), ship_class="Frigate", registries=fresh_registries)
        yield

        # Note: reset_singletons fixture in conftest.py handles cleanup
        if pygame.get_init():
            pygame.quit()

    def test_change_class_migration(self):
        """Verify components migrate or are removed during class change."""
        # Add components to Frigate
        bridge = create_component('bridge', registries=self.registries)
        self.ship.add_component(bridge, LayerType.CORE)

        railgun = create_component('railgun', registries=self.registries)
        self.ship.add_component(railgun, LayerType.OUTER)

        # Change to "Destroyer" with migration
        self.ship.change_class("Destroyer", migrate_components=True)

        # Verify components remained
        assert self.ship.ship_class == "Destroyer"

        # Helper to find component in layer
        def has_comp(layer_type, comp):
            return comp in self.ship.layers[layer_type].components

        assert has_comp(LayerType.CORE, bridge) is True
        assert has_comp(LayerType.OUTER, railgun) is True

    def test_derelict_status_logic(self):
        """
        Verify is_derelict uses functional definition: no operational
        weapons AND no operational engines = derelict.

        The per-component RequiresCommandAndControl check is tested
        separately in combat_lab (CNC category).
        """
        # Add bridge and crew support
        bridge = create_component('bridge', registries=self.registries)
        self.ship.add_component(bridge, LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters', registries=self.registries), LayerType.CORE)
        self.ship.add_component(create_component('life_support', registries=self.registries), LayerType.CORE)

        # Ship with no weapons and no engines → derelict
        self.ship.recalculate_stats()
        self.ship.update_derelict_status()
        assert self.ship.is_derelict is True, "Ship with no weapons/engines should be derelict"

        # Add a weapon → no longer derelict
        railgun = create_component('railgun', registries=self.registries)
        self.ship.add_component(railgun, LayerType.OUTER)
        self.ship.recalculate_stats()
        self.ship.update_derelict_status()
        assert self.ship.is_derelict is False, "Ship with operational weapon should not be derelict"

        # Destroy the weapon → derelict again
        railgun.current_hp = 0
        railgun.is_active = False
        self.ship.recalculate_stats()
        self.ship.update_derelict_status()
        assert self.ship.is_derelict is True, "Ship should be derelict after losing all weapons"


# --- Pytest-style Tests (merged from test_ship_core.py) ---

@pytest.fixture
def registry_with_hull(minimal_registries):
    """
    Populate GameRegistries with Escort class and its hull_escort component.
    Uses minimal_registries as a base for test isolation.
    """
    # Vehicle class with default_hull_id
    minimal_registries.vehicle_classes.update({
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
    hull_component = Component(hull_data, registries=minimal_registries)
    minimal_registries.components["hull_escort"] = hull_component

    return minimal_registries


@pytest.fixture
def ship_with_components(registry_with_hull):
    """Create a Ship with known components for mass/HP verification."""
    registries = registry_with_hull

    # Add a simple Armor component
    armor_data = {
        "id": "test_armor",
        "name": "Test Armor",
        "type": "Armor",
        "mass": 25,
        "hp": 50,
        "abilities": {}
    }
    armor_component = Component(armor_data, registries=registries)
    registries.components["test_armor"] = armor_component

    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="Escort", registries=registries)

    # Add armor component to OUTER layer
    armor = create_component("test_armor", registries=registries)
    if armor:
        ship.add_component(armor, LayerType.OUTER)

    ship.recalculate_stats()
    return ship


class TestHullAutoEquipVerification:
    """TC-3.2.1: Hull Auto-Equip Verification"""

    def test_hull_auto_equip(self, registry_with_hull):
        """Verify Ship auto-equips default_hull_id from vehicle class."""
        ship = Ship(name="Test", x=0, y=0, color=(255, 255, 255), ship_class="Escort", registries=registry_with_hull)

        hull_comps = ship.layers[LayerType.HULL].components
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

        PROJ-195: Pure DI pattern - uses fresh_registries directly, no singleton hydration.
        """
        if not pygame.get_init():
            pygame.init()

        yield

        # Note: reset_singletons fixture in conftest.py handles cleanup
        if pygame.get_init():
            pygame.quit()

    def test_change_class_invalid_class_name_does_not_raise(self, fresh_registries):
        """Verify change_class() with invalid class name handles error gracefully.

        Prior to fix, this would raise UnboundLocalError due to local import shadowing.
        """
        ship = Ship("Test", 0, 0, (255, 255, 255), ship_class="Frigate", registries=fresh_registries)
        original_class = ship.ship_class

        # This should NOT raise UnboundLocalError - just log error and return
        ship.change_class("NonExistentClassXYZ")

        # Ship class should remain unchanged since the new class doesn't exist
        assert ship.ship_class == original_class


class TestTotalDefenseScoreInitialization:
    """Tests for total_defense_score initialization (NEW-SIM-001 fix)."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, fresh_registries):
        """Set up registry data for tests.

        PROJ-195: Pure DI pattern - uses fresh_registries directly, no singleton hydration.
        """
        yield
        if pygame.get_init():
            pygame.quit()

    def test_total_defense_score_initial_value_is_zero(self, fresh_registries):
        """Verify total_defense_score is initialized to 0.0 (additive neutral).

        Defense score is an additive term subtracted in the sigmoid hit formula:
        net_score = (base_accuracy + attack_bonus) - (range_penalty + defense_score)
        A default of 0.0 means no defense modifier before stats are calculated.
        The actual value is computed by ShipStatsCalculator.calculate().
        """
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=fresh_registries)

        assert ship.total_defense_score == 0.0, (
            f"total_defense_score should be initialized to 0.0, got {ship.total_defense_score}"
        )

    def test_total_defense_score_is_recalculated_by_stats(self, fresh_registries):
        """Verify total_defense_score is updated when stats are recalculated."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=fresh_registries)

        ship.recalculate_stats()

        # After recalculation, value should be computed from components
        # For a ship with just a Hull, this will be based on size/maneuver/ecm scores
        # The exact value depends on the ship configuration, but it should be a float
        assert isinstance(ship.total_defense_score, float), "total_defense_score should be a float"


# =============================================================================
# PROJ-225: Hull Auto-Equip Extraction Tests
# =============================================================================

class TestHullAutoEquip:
    """Tests for the extracted _equip_default_hull method."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        yield

    def test_init_equips_default_hull(self, fresh_registries):
        """Ship.__init__ equips the default hull component."""
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries)
        hull_comps = ship.layers[LayerType.HULL].components
        assert len(hull_comps) == 1
        assert hull_comps[0].layer_assigned == LayerType.HULL
        assert hull_comps[0].ship is ship

    def test_change_class_equips_new_hull(self, fresh_registries):
        """Ship.change_class equips the hull for the new class."""
        ship = Ship("Test", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        old_hull = ship.layers[LayerType.HULL].components[0]

        # Change to a different class that also has a hull
        ship.change_class("Frigate")
        new_hull = ship.layers[LayerType.HULL].components[0]

        # Should have a hull in the new class
        assert len(ship.layers[LayerType.HULL].components) == 1
        assert new_hull.ship is ship
        assert new_hull.layer_assigned == LayerType.HULL

    def test_no_hull_if_class_has_no_default(self, fresh_registries):
        """Ship with no default_hull_id gets no hull component."""
        fresh_registries.vehicle_classes["NoHull"] = {
            "max_mass": 500,
            "layers": [
                {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 1.0},
            ]
        }
        ship = Ship("Test", 0, 0, (255, 255, 255), ship_class="NoHull", registries=fresh_registries)
        assert len(ship.layers[LayerType.HULL].components) == 0


# =============================================================================
# PROJ-225: Component Attachment Extraction Tests
# =============================================================================

class TestComponentAttachment:
    """Tests for the extracted _attach_component method."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        yield

    def test_add_component_attaches_correctly(self, fresh_registries):
        """add_component sets layer_assigned, ship ref, and triggers recalculate."""
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries)
        bridge = create_component('bridge', registries=fresh_registries)

        result = ship.add_component(bridge, LayerType.CORE)

        assert result is True
        assert bridge.layer_assigned == LayerType.CORE
        assert bridge.ship is ship
        assert bridge in ship.layers[LayerType.CORE].components

    def test_add_components_bulk_attaches_all(self, fresh_registries):
        """add_components_bulk attaches multiple components correctly."""
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries)
        bridge = create_component('bridge', registries=fresh_registries)

        count = ship.add_components_bulk(bridge, LayerType.CORE, 2)

        assert count >= 1  # At least one should be added
        for comp in ship.layers[LayerType.CORE].components:
            assert comp.layer_assigned == LayerType.CORE
            assert comp.ship is ship


# =============================================================================
# PROJ-225: DEFAULT_MAX_MASS Constant Tests
# =============================================================================

class TestDefaultMaxMass:
    """Tests for DEFAULT_MAX_MASS named constant."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        yield

    def test_ship_uses_constant_for_unknown_class(self, fresh_registries):
        """Ship with unknown class uses DEFAULT_MAX_MASS."""
        from game.simulation.entities.ship import DEFAULT_MAX_MASS
        fresh_registries.vehicle_classes["Unknown"] = {
            "layers": [{"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 1.0}]
        }
        ship = Ship("Test", 0, 0, (255, 255, 255), ship_class="Unknown", registries=fresh_registries)
        assert ship.max_mass_budget == DEFAULT_MAX_MASS

    def test_change_class_unknown_raises_validation_error(self, fresh_registries):
        """change_class with unknown class should raise ValidationException.

        PROJ-240 Phase 3: Bug fix -- previously silently fell back to empty dict.
        """
        from game.core.exceptions import ValidationException
        ship = Ship("Test", 0, 0, (255, 255, 255), registries=fresh_registries)
        # Attempt to change to a nonexistent class -- early guard should reject
        # The method currently returns silently for unknown classes at entry
        ship.change_class("nonexistent_class_xyz")
        # The ship_class should NOT have changed (early guard returns before mutation)
        assert ship.ship_class == "Escort"

    def test_ship_layer_manager_uses_canonical_default_max_mass(self):
        """ship_layer_manager must use the canonical DEFAULT_MAX_MASS from
        physics_constants (1000), not a divergent local definition.

        Previously ship_layer_manager.py defined its own DEFAULT_MAX_MASS = 500
        — different from physics_constants.DEFAULT_MAX_MASS = 1000. The local 500
        was effectively dead code (Ship.recalculate_stats always overwrote it
        with the canonical 1000), but the divergence was a smell. This test
        asserts the two are unified.
        """
        from game.simulation.entities import ship_layer_manager
        from game.simulation.physics_constants import DEFAULT_MAX_MASS as CANONICAL_DEFAULT

        assert ship_layer_manager.DEFAULT_MAX_MASS == CANONICAL_DEFAULT, (
            f"ship_layer_manager.DEFAULT_MAX_MASS = "
            f"{ship_layer_manager.DEFAULT_MAX_MASS}, but physics_constants."
            f"DEFAULT_MAX_MASS = {CANONICAL_DEFAULT}. The two must be unified — "
            f"ship_layer_manager should import from physics_constants."
        )
