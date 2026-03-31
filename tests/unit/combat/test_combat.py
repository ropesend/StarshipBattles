"""Tests for ship combat damage mechanics."""
import pytest
import pygame
import random

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import create_component  # Phase 7: Removed Bridge import
from unittest.mock import MagicMock


class TestDamageLayerLogic:
    """Test damage distribution through ship layers."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        # Save random state and set deterministic seed for reproducible tests
        # State is restored after test to prevent pollution of other tests
        saved_random_state = random.getstate()
        random.seed(42)

        self.registries = fresh_registries
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=fresh_registries)
        self.ship.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('armor_plate', registries=fresh_registries), LayerType.ARMOR)

        # Ensure TestShip class exists in registries with correct layers
        # Note: Post-Phase 5, hull_mass is removed; Hull component provides mass
        self.registries.vehicle_classes["TestShip"] = {
            "max_mass": 1000,
            "layers": [
                {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 0.5},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.5}
            ]
        }
        self.ship._initialize_layers()
        # Re-add components because _initialize_layers clears them
        self.ship.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('armor_plate', registries=fresh_registries), LayerType.ARMOR)

        self.ship.recalculate_stats()

        yield

        # Restore random state to prevent pollution of other tests
        random.setstate(saved_random_state)

    def test_armor_absorbs_damage_first(self):
        """Damage should be absorbed by armor layer first."""
        armor = self.ship.layers[LayerType.ARMOR].components[0]
        initial_armor_hp = armor.current_hp

        # Deal damage less than armor HP
        self.ship.combat_engine.take_damage(50)

        assert armor.current_hp < initial_armor_hp
        # Core components should be untouched
        core_damage = sum(c.max_hp - c.current_hp for c in self.ship.layers[LayerType.CORE].components)
        assert core_damage == 0

    def test_damage_overflows_to_next_layer(self):
        """Excess damage should overflow to inner layers."""
        armor = self.ship.layers[LayerType.ARMOR].components[0]
        armor_hp = armor.current_hp

        # Deal more damage than armor can absorb
        overflow_damage = 50
        self.ship.combat_engine.take_damage(armor_hp + overflow_damage)

        # Armor should be destroyed
        assert armor.current_hp == 0

        # CORE (skipping empty OUTER/INNER) should have taken overflow
        core_damage = sum(c.max_hp - c.current_hp for c in self.ship.layers[LayerType.CORE].components)
        assert core_damage > 0

    def test_shield_absorbs_before_armor(self):
        """Shield should absorb damage before armor."""
        # Add shield (correct component ID is 'shield_generator')
        self.ship.add_component(create_component('shield_generator', registries=self.registries), LayerType.CORE)
        self.ship.recalculate_stats()

        initial_shields = self.ship.current_shields
        armor = self.ship.layers[LayerType.ARMOR].components[0]
        initial_armor_hp = armor.current_hp

        # Deal damage less than shields
        damage = min(initial_shields - 10, 50)
        if damage > 0:
            self.ship.combat_engine.take_damage(damage)

            assert self.ship.current_shields < initial_shields
            assert armor.current_hp == initial_armor_hp

    def test_bridge_destruction_kills_ship(self):
        """Destroying the bridge SHOULD make the ship derelict (ability-based detection).

        Post-Phase 5: Derelict status is determined by CommandAndControl ability.
        If no operational component has CommandAndControl, ship becomes derelict.
        The ship needs a hull component with RequiresCommandAndControl for this to work.
        """
        self.registries.vehicle_classes["TestShip"] = {
            "max_mass": 1000,
            "layers": [
                {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 0.5},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.5}
            ]
        }
        self.ship.ship_class = "TestShip"

        # Add a hull component to require command and control
        # Without this, the ship has no requirements and won't become derelict
        hull = create_component('hull_escort', registries=self.registries)
        self.ship.add_component(hull, LayerType.CORE)

        # Remove armor first to make bridge accessible
        self.ship.layers[LayerType.ARMOR].components = []
        self.ship.recalculate_stats()

        bridge = None
        for c in self.ship.layers[LayerType.CORE].components:
            if c.type_str == 'Bridge':
                bridge = c
                break

        assert bridge is not None
        assert self.ship.is_alive

        # Update derelict status - should NOT be derelict initially (has bridge)
        self.ship.update_derelict_status()
        assert not self.ship.is_derelict, "Ship should not be derelict with operational bridge"

        # Directly destroy the bridge instead of using take_damage
        # take_damage might hit other components first due to random distribution
        bridge.current_hp = 0
        bridge.is_active = False

        # Bridge should be destroyed
        assert not bridge.is_active

        # Update derelict status - should BE derelict now (no CommandAndControl)
        self.ship.update_derelict_status()
        assert self.ship.is_derelict, "Ship should be derelict after bridge destruction"
        assert self.ship.bridge_destroyed, "bridge_destroyed flag should be set"

class TestEnergyRegeneration:
    """Test energy and shield regeneration mechanics."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser", registries=fresh_registries)
        self.ship.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('battery', registries=fresh_registries), LayerType.INNER)
        self.ship.add_component(create_component('generator', registries=fresh_registries), LayerType.INNER)
        self.ship.recalculate_stats()

    def test_energy_regenerates_per_tick(self):
        """Energy should regenerate each combat tick."""
        # Drain energy first, then check if it regenerates
        self.ship.resources.get_resource("energy").current_value = self.ship.resources.get_max_value("energy") / 2
        initial_energy = self.ship.resources.get_value("energy")

        # Energy regeneration happens in Ship.update() via ResourceRegistry (tick-based)
        self.ship.update()

        assert self.ship.resources.get_value("energy") > initial_energy

    def test_energy_capped_at_max(self):
        """Energy should not exceed max_energy."""
        self.ship.resources.get_resource("energy").current_value = self.ship.resources.get_max_value("energy") - 1

        # Regen creates overflow
        # Manually boost regen rate to ensure overflow (tick is 0.01s, need >1.0 change)
        self.ship.resources.get_resource("energy").regen_rate = 200
        self.ship.update()

        assert self.ship.resources.get_value("energy") == self.ship.resources.get_max_value("energy")

    def test_dead_ship_no_regen(self):
        """Dead ship should not regenerate energy."""
        self.ship.is_alive = False
        self.ship.resources.get_resource("energy").current_value = 0

        self.ship.update()

        assert self.ship.resources.get_value("energy") == 0


class TestWeaponCooldowns:
    """Test weapon cooldown mechanics."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), registries=fresh_registries)
        self.ship.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
        self.ship.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
        # Use laser_cannon which is a BeamWeapon that can go in OUTER
        self.ship.add_component(create_component('laser_cannon', registries=fresh_registries), LayerType.OUTER)
        self.ship.recalculate_stats()

    def test_weapon_cooldown_decreases(self):
        """Weapon cooldown should decrease each tick."""
        # Phase 7: Use ability-based weapon detection

        weapon = None
        for c in self.ship.layers[LayerType.OUTER].components:
            if c.has_ability('WeaponAbility') and c.is_active:
                weapon = c
                break

        assert weapon is not None, "No active weapon found in OUTER layer"

        # Phase 7: Use ability-based access for weapon methods
        weapon_ab = weapon.get_ability('WeaponAbility') or weapon.get_ability('ProjectileWeaponAbility')
        assert weapon_ab is not None

        # Fire to start cooldown
        weapon_ab.fire(target=None)
        initial_cooldown = weapon_ab.cooldown_timer
        assert initial_cooldown > 0, "Weapon should have cooldown after firing"

        # Weapon cooldowns are updated in Ship.update() via Component.update() (tick-based)
        self.ship.update()

        assert weapon_ab.cooldown_timer < initial_cooldown



class TestCombatFlow:
    """Refactored Tests for Combat Flow (Firing and Damage)."""

    def test_firing_solution_lead(self):
        """Test lead calculation for moving targets."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        mock_ship = MagicMock()
        mock_ship.position = pygame.math.Vector2(0, 0)
        mock_ship.velocity = pygame.math.Vector2(0, 0)

        engine = ShipCombatEngine(mock_ship)

        # Target moving right at 10 u/s at (100, 0)
        target_pos = pygame.math.Vector2(100, 0)
        target_vel = pygame.math.Vector2(10, 0)
        proj_speed = 20.0

        # Expected collision:
        # P = Vp * t = 20t
        # T = P0 + Vt * t = 100 + 10t
        # Intercept when distance covered matches
        # (20t)^2 = (100 + 10t)^2
        # ... t = 10.0 (See calculation logic)

        t = engine.solve_lead(mock_ship.position, mock_ship.velocity, target_pos, target_vel, proj_speed)
        assert abs(t - 10.0) < 0.1

    def test_fire_weapons_creates_projectiles(self, fresh_registries):
        """Test that fire_weapons returns correct projectile objects."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import Component
        from game.core.constants import AttackType

        ship = Ship("Shooter", 0,0, (255,255,255), registries=fresh_registries)

        # Add a weapon component manually to ensure it has no cost issues
        # Component needs to be 'active'
        weapon = Component({
            "id": "test_gun",
            "name": "Gun",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {
                "WeaponAbility": {"range": 1000, "fire_rate": 1, "cooldown": 0},
                "ProjectileWeaponAbility": {"projectile_speed": 100, "damage": 10, "range": 1000}
            }
        }, registries=fresh_registries)
        ship.add_component(weapon, LayerType.OUTER)
        ship.recalculate_stats() # Activate component

        # Setup Target
        target = MagicMock()
        target.position = pygame.math.Vector2(100, 0)
        target.velocity = pygame.math.Vector2(0,0)
        target.is_alive = True
        target.team_id = 1
        target.type = 'ship'

        ship.team_id = 0
        ship.current_target = target

        # Fire
        attacks = ship.combat_engine.fire_weapons()

        assert len(attacks) == 1
        assert attacks[0].damage == 10
        assert attacks[0].type == AttackType.PROJECTILE  # proj_type -> type
        assert attacks[0].owner == ship

    def test_special_armor_interactions(self, fresh_registries):
        """Test Emissive and Crystalline Armor logic."""
        from game.simulation.entities.ship import Ship
        ship = Ship("Tank", 0,0, (255,255,255), registries=fresh_registries)

        # 1. Emissive Armor (Flat Reduction)
        ship.emissive_armor = 5
        ship.is_alive = True

        # Add a dummy component to take damage
        c = create_component('bridge', registries=fresh_registries)
        ship.add_component(c, LayerType.CORE)
        ship.recalculate_stats()
        ship.emissive_armor = 5

        # Find the bridge component (Hull is auto-equipped first now)
        bridge = None
        for comp in ship.layers[LayerType.CORE].components:
            if comp.type_str == 'Bridge':
                bridge = comp
                break
        assert bridge is not None, "Bridge component should be in CORE layer"
        c = bridge

        c.is_active = True
        c.current_hp = 100
        initial_hp = c.current_hp

        # Clear other components except the bridge for this test
        ship.layers[LayerType.CORE].components = [c]

        # Take 10 damage -> Reduced by 5 -> 5 damage
        ship.combat_engine.take_damage(10)
        assert c.current_hp == initial_hp - 5

        ship.emissive_armor = 5

        # Take 4 damage -> Reduced by 5 -> 0 damage
        prev_hp = c.current_hp
        ship.combat_engine.take_damage(4)
        assert c.current_hp == prev_hp

        # 2. Crystalline Armor (Absorb + Shield Recharge)
        # This test sets shield values directly without ShieldProjection components.
        # Disable recalculate_stats so damage_calculator doesn't zero out shields.
        ship.recalculate_stats = lambda: None
        ship.emissive_armor = 0
        ship.crystalline_armor = 10
        ship.max_shields = 100
        ship.current_shields = 50

        # Take 20 damage
        # Absorb min(10, 20) = 10
        # Shields += 10 -> 60
        # Remaining Damage = 10
        # Shield Absorption: min(60, 10) = 10 absorbed
        # Shields -= 10 -> 50
        # Remaining Damage = 0
        # Component HP untouched

        prev_hp = c.current_hp
        ship.combat_engine.take_damage(20)

        assert ship.current_shields == 50
        assert c.current_hp == prev_hp
