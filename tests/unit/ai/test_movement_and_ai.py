import pytest
from unittest.mock import MagicMock
import pygame

from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import initialize_ship_data
from game.ui.screens.battle_screen import BattleScreen
from game.ai.controller import AIController
from game.ai.policy_manager import get_default_policy_manager
from game.ai.interfaces.controllable import ShipControllableAdapter
from game.simulation.components.component import load_components, load_modifiers, create_component
from game.core.constants import LayerType
from game.core.registry import get_default_registry_provider
from tests.fixtures.paths import get_data_dir, get_unit_test_data_dir


@pytest.fixture
def movement_ai_setup(fresh_registries):
    pygame.init()
    # Initialize vehicle class definitions FIRST (required for layer configs)
    initialize_ship_data()

    data_dir = get_data_dir()
    unit_test_data_dir = get_unit_test_data_dir()

    # Load components and modifiers
    comp_path = data_dir / "components.json"
    mod_path = data_dir / "modifiers.json"

    provider = get_default_registry_provider()
    mod_path_str = None
    if comp_path.exists():
        load_components(str(comp_path), registry_provider=provider)
    if mod_path.exists():
        mod_path_str = str(mod_path)
        load_modifiers(str(mod_path), registry_provider=provider)

    manager = get_default_policy_manager()
    manager.load_data(
        str(unit_test_data_dir),
        targeting_file="test_targeting_policies.json",
        movement_file="test_movement_policies.json",
    )
    manager._loaded = True
    ship = Ship("TestShip", 0, 0, (255, 255, 255), 0, ship_class="Cruiser", registries=fresh_registries)

    yield {
        'ship': ship,
        'mod_path': mod_path_str,
        'registries': fresh_registries
    }

    pygame.quit()
    get_default_policy_manager().clear()


class TestMovementAndAI:

    def test_ai_target_acquisition_long_range(self, movement_ai_setup):
        """
        Regression Test: Ensure AI can target enemies at very long range.
        """
        attacker = movement_ai_setup['ship']
        registries = movement_ai_setup['registries']
        attacker.movement_policy = "kite_max"
        attacker.position = pygame.math.Vector2(0, 0)

        target = Ship("Target", 50000, 0, (255, 0, 0), 1, registries=registries)
        target.ship_class = "Escort"
        target.mass = 1000

        mock_grid = MagicMock()
        mock_grid.query_radius.return_value = [target]
        mock_grid.query_radius_exact.return_value = [target]

        # Use ShipControllableAdapter to match production behavior
        ai = AIController(ShipControllableAdapter(attacker), mock_grid, 1)

        found_target = ai.find_target()

        assert found_target is not None, "AI failed to acquire long-range target"
        assert found_target == target

    def test_ai_thrust_command_generation(self, movement_ai_setup):
        """
        Verify AI issues thrust commands when it has a valid target ahead.
        """
        attacker = movement_ai_setup['ship']
        registries = movement_ai_setup['registries']
        # Build a valid ship with all required components
        # Bridge (CORE) - CommandAndControl
        bridge = create_component("bridge", registries=registries)
        attacker.add_component(bridge, LayerType.CORE)

        # Generator (CORE)
        gen = create_component("generator", registries=registries)
        attacker.add_component(gen, LayerType.CORE)

        # Engine (OUTER) - CombatPropulsion
        engine = create_component("standard_engine", registries=registries)
        attacker.add_component(engine, LayerType.OUTER)

        # Fuel (INNER) - FuelStorage
        fuel = create_component("fuel_tank", registries=registries)
        attacker.add_component(fuel, LayerType.INNER)

        # Life Support + Crew for operational ship (need multiple for Cruiser crew requirements)
        for _ in range(4):
            ls = create_component("life_support", registries=registries)
            attacker.add_component(ls, LayerType.INNER)
            cq = create_component("crew_quarters", registries=registries)
            attacker.add_component(cq, LayerType.INNER)

        attacker.recalculate_stats()

        attacker.position = pygame.math.Vector2(0, 0)
        attacker.update(1 / 60.0)

        # Attacker is already configured as Cruiser in setUp

        target = Ship("Test", 500, 0, (255, 0, 0), team_id=1, ship_class="Cruiser", registries=registries)
        target.mass = 100

        mock_grid = MagicMock()
        mock_grid.query_radius.return_value = [target]
        mock_grid.query_radius_exact.return_value = [target]

        # Use ShipControllableAdapter to match production behavior
        ai = AIController(ShipControllableAdapter(attacker), mock_grid, 1)

        # 1. Find target
        attacker.current_target = ai.find_target()
        assert attacker.current_target == target

        # 2. Update AI
        attacker.is_thrusting = False
        ai.update()

        assert attacker.is_thrusting is True, "AI did not set is_thrusting despite valid target ahead"
