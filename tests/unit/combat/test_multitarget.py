import pytest
from unittest.mock import MagicMock, patch
import pygame
import math

from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import Component, load_components
from game.simulation.components.component_constants import LayerType
from game.core.registry import RegistryManager
from game.ai.controller import AIController
from game.ai.interfaces.controllable import ShipControllableAdapter
from game.engine.spatial import SpatialGrid
from game.simulation.entities.projectile import Projectile
from game.core.constants import AttackType


@pytest.fixture(autouse=True)
def setup_game_data():
    """Initialize pygame and game data before each test."""
    pygame.init()
    initialize_ship_data()
    load_components()


@pytest.fixture
def grid():
    """Create a spatial grid for tests."""
    return SpatialGrid(2000)


@pytest.fixture
def base_ship(grid, fresh_registries):
    """Create a fully equipped base ship for testing."""
    ship = Ship("TestShip", 1000, 1000, (255, 0, 0), team_id=0, ship_class="Cruiser", registries=fresh_registries)
    # Use ShipControllableAdapter to match production behavior (battle_engine.py)
    ai = AIController(ShipControllableAdapter(ship), grid, enemy_team_id=1)
    ship.ai_controller = ai

    # Add Infrastructure to avoid derelict status and allow components to work
    comps = RegistryManager.instance().components

    # 1. Bridge (required for non-derelict)
    if 'bridge' in comps:
        bridge = comps['bridge'].clone()
        ship.add_component(bridge, LayerType.CORE)

    # 2. Engine (required for non-derelict on Ships)
    if 'standard_engine' in comps:
        engine = comps['standard_engine'].clone()
        ship.add_component(engine, LayerType.INNER)

    # 3. Generator
    if 'generator' in comps:
        gen = comps['generator'].clone()
        ship.add_component(gen, LayerType.CORE)

    # 4. Battery (for energy storage - required for beam weapons)
    if 'battery' in comps:
        bat = comps['battery'].clone()
        ship.add_component(bat, LayerType.INNER)

    # 5. Crew Quarters (Need enough for Multi-tracker + weapons + bridge)
    if 'crew_quarters' in comps:
        cq1 = comps['crew_quarters'].clone()
        ship.add_component(cq1, LayerType.INNER)
        cq2 = comps['crew_quarters'].clone()
        ship.add_component(cq2, LayerType.INNER)
        cq3 = comps['crew_quarters'].clone()
        ship.add_component(cq3, LayerType.INNER)

    # 6. Life Support
    if 'life_support' in comps:
        ls = comps['life_support'].clone()
        ship.add_component(ls, LayerType.INNER)
        ls2 = comps['life_support'].clone()
        ship.add_component(ls2, LayerType.INNER)

    ship.recalculate_stats()
    return ship


class TestMultitarget:

    def test_multiplex_tracking_stats(self, base_ship):
        ship = base_ship
        # Add Multiplex Tracking
        comps = RegistryManager.instance().components
        if 'multiplex_tracking' not in comps:
            pytest.skip("multiplex_tracking component not defined")

        comp = comps['multiplex_tracking'].clone()
        ship.add_component(comp, LayerType.OUTER)
        ship.recalculate_stats()

        assert ship.max_targets == 10

    def test_secondary_target_acquisition(self, base_ship, grid, fresh_registries):
        ship = base_ship
        # Add Multiplex
        comps = RegistryManager.instance().components
        if 'multiplex_tracking' not in comps:
            pytest.skip("multiplex_tracking component not defined")

        comp = comps['multiplex_tracking'].clone()
        ship.add_component(comp, LayerType.OUTER)
        ship.recalculate_stats()

        # Create Enemies
        e1 = Ship("Enemy1", 1100, 1000, (255, 0, 0), team_id=1, registries=fresh_registries)  # Dist 100
        e2 = Ship("Enemy2", 1200, 1000, (255, 0, 0), team_id=1, registries=fresh_registries)  # Dist 200
        e3 = Ship("Enemy3", 1300, 1000, (255, 0, 0), team_id=1, registries=fresh_registries)  # Dist 300

        grid.insert(e1)
        grid.insert(e2)
        grid.insert(e3)

        # Update AI
        ship.ai_controller.update()

        # Depending on strategy (default 'nearest'), closest should be primary
        assert ship.current_target == e1
        assert e2 in ship.secondary_targets
        assert e3 in ship.secondary_targets

    def test_pdc_missile_logic(self, base_ship, grid):
        ship = base_ship
        comps = RegistryManager.instance().components
        if 'multiplex_tracking' not in comps:
            pytest.skip("multiplex_tracking component not defined")

        # Add Multiplex
        comp = comps['multiplex_tracking'].clone()
        res = ship.add_component(comp, LayerType.OUTER)
        if not res:
            pytest.fail("Multiplex add failed")

        # Add PDC: Facing 0 (Right), Arc 45
        pdc = comps['point_defence_cannon'].clone()
        pdc.facing_angle = 0
        limit_ab = pdc.get_ability('ProjectileWeaponAbility') or pdc.get_ability('WeaponAbility')
        if limit_ab:
            limit_ab.firing_arc = 45
            limit_ab.range = 800
        res = ship.add_component(pdc, LayerType.OUTER)
        if not res:
            pytest.fail("PDC add failed")

        ship.recalculate_stats()

        # Scenario 1: Missile in Front (In Arc)
        # 1200, 1000 is 200 units to RIGHT of 1000,1000. Angle 0.
        m1 = Projectile(None, pygame.math.Vector2(1200, 1000), pygame.math.Vector2(0,0), 10, 1000, 5, AttackType.MISSILE)
        m1.team_id = 1

        # Scenario 2: Missile Behind (Out of Arc)
        # 800, 1000 is 200 units to LEFT of 1000,1000. Angle 180.
        m2 = Projectile(None, pygame.math.Vector2(800, 1000), pygame.math.Vector2(0,0), 10, 1000, 5, AttackType.MISSILE)
        m2.team_id = 1

        # Add to grid so AI can find them
        grid.insert(m1)
        grid.insert(m2)

        # Inject Strategy into StrategyManager (new data-driven system)
        from game.ai.strategy_manager import StrategyManager
        manager = StrategyManager.instance()
        manager._loaded = True  # Prevent ensure_loaded() from overwriting test data

        # Add test targeting policy with missiles_in_pdc_arc rule
        manager.targeting_policies['test_pdc_target'] = {
            'name': 'Test PDC Targeting',
            'rules': [
                {'type': 'missiles_in_pdc_arc', 'weight': 2000, 'required': True},
                {'type': 'nearest', 'weight': 100}
            ]
        }

        # Add test strategy that uses this targeting policy
        manager.strategies['test_strat'] = {
            'name': 'Test Strategy',
            'targeting_policy': 'test_pdc_target',
            'movement_policy': 'kite_max'
        }

        ship.ai_strategy = 'test_strat'

        # Force AI update to use this strategy
        sec = ship.ai_controller.find_secondary_targets()

        # M1 should be prioritized because it is in PDC arc
        assert m1 in sec
        # M2 should NOT be in list (hard filter via required=True)
        assert m2 not in sec

        # Verify Firing
        # Manually set secondary targets as AI update would
        ship.secondary_targets = sec
        context = {'projectiles': [m1, m2]}

        # Ensure ship has resources to fire
        max_energy = ship.resources.get_max_value("energy")
        ship.resources.set_value("energy", max_energy)

        # Ensure PDC is not on cooldown
        pdc.cooldown_timer = 0

        fired = ship.fire_weapons(context)

        # Should fire 1 shot
        assert len(fired) > 0, "PDC should have fired at missile"

        # Check target of first shot
        shot = fired[0]
        # Handle dict or object return
        target = shot.target if hasattr(shot, 'target') else shot.get('target')
        assert target == m1


class TestMaxTargetsDefault:
    """Tests for CombatConstants.DEFAULT_MAX_TARGETS usage."""

    def test_ship_default_max_targets_equals_constant(self, fresh_registries):
        """Ship's default max_targets should equal CombatConstants.DEFAULT_MAX_TARGETS."""
        from game.core.constants import CombatConstants

        ship = Ship("TestShip", 0, 0, (255, 0, 0), team_id=0, ship_class="Escort", registries=fresh_registries)
        assert ship.max_targets == CombatConstants.DEFAULT_MAX_TARGETS

    def test_stats_reset_uses_default_constant(self, fresh_registries):
        """ShipStatsCalculator reset should use CombatConstants.DEFAULT_MAX_TARGETS."""
        from game.core.constants import CombatConstants
        from game.simulation.entities.ship_stats import ShipStatsCalculator
        from game.core.registry import get_default_registry_provider

        ship = Ship("TestShip", 0, 0, (255, 0, 0), team_id=0, ship_class="Escort", registries=fresh_registries)
        # Manually set max_targets to a different value
        ship.max_targets = 99

        calculator = ShipStatsCalculator(get_default_registry_provider().get_vehicle_classes())
        calculator.calculate(ship)

        # After recalculation, should be reset to default
        assert ship.max_targets == CombatConstants.DEFAULT_MAX_TARGETS
