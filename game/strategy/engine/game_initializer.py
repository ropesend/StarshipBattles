"""
GameInitializer - Handles galaxy and empire initialization.

Extracted from GameSession (PROJ-87 Phase 6) to isolate initialization
logic from session management.

Provides a single entry point for creating new game galaxies with empires.
"""
import logging
import random
from typing import List, Optional, Tuple

from game.strategy.data.empire import Empire

logger = logging.getLogger(__name__)
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.planet import SpeciesPopulation
from game.strategy.engine.game_config import GameConfig
from game.strategy.generation.placement_strategies import (
    RandomPlacementStrategy,
    DensityBasedPlacementStrategy,
)
from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.loaders.galaxy_layouts_loader import GalaxyLayoutsLoader


class GameInitializer:
    """
    Handles initialization of new game galaxies and empires.

    Provides a single static entry point for creating game content.
    """

    @staticmethod
    def initialize(config: GameConfig) -> Tuple[Galaxy, List[Empire]]:
        """
        Initialize a new game galaxy and empires from configuration.

        Args:
            config: Game configuration with player, galaxy, and seed settings.

        Returns:
            Tuple of (Galaxy, list[Empire]) ready for gameplay.
        """
        # Create empires from config
        empires = GameInitializer._create_empires(config)

        # Create and populate galaxy
        galaxy = Galaxy(radius=config.galaxy_radius)
        systems = GameInitializer._initialize_galaxy(galaxy, config)

        # Set up initial scenario (homeworlds, colonies)
        GameInitializer._setup_initial_scenario(systems, empires, config)

        # PROJ-219: Set galaxy back-references for auto fleet registration
        for empire in empires:
            empire.set_galaxy(galaxy)

        return galaxy, empires

    @staticmethod
    def _create_empires(config: GameConfig) -> List[Empire]:
        """Create Empire objects from player configuration.

        If a player has no race_config, a default RaceConfig is created
        using the player's name and theme (BUG-88).
        """
        from game.strategy.data.race_config import RaceConfig

        empires = []
        for i, player_cfg in enumerate(config.players):
            theme_path = config.get_player_theme_path(i)
            logger.info(f"GameInitializer: Creating empire {i} with theme={player_cfg.theme}")

            # Ensure every empire has a race_config (BUG-88)
            race_config = player_cfg.race_config
            if race_config is None:
                race_config = RaceConfig(
                    race_id=f"empire_{i}",
                    name=player_cfg.name,
                    faction_name=player_cfg.name,
                    race_name=player_cfg.name,
                    theme_id=player_cfg.theme,
                    flag_id=player_cfg.flag_id,
                    portrait_id=player_cfg.portrait_id,
                )

            empire = Empire(
                empire_id=i,
                name=player_cfg.name,
                color=player_cfg.color,
                theme_path=theme_path,
                empire_theme_id=player_cfg.theme,
                flag_id=player_cfg.flag_id,
                portrait_id=player_cfg.portrait_id,
                race_config=race_config
            )
            empires.append(empire)
        return empires

    @staticmethod
    def _initialize_galaxy(galaxy: Galaxy, config: GameConfig) -> list:
        """
        Initialize the galaxy with systems and warp lanes.

        Uses the galaxy_type and galaxy_seed from config to determine
        placement strategy. If galaxy_type is "random", uses uniform random
        placement. Otherwise, loads the density-based layout from
        galaxy_layouts.json.

        Args:
            galaxy: Galaxy to populate.
            config: Game configuration.

        Returns:
            List of generated StarSystem objects.
        """
        galaxy_type = config.galaxy_type
        galaxy_seed = config.galaxy_seed

        logger.info(f"GameInitializer: Generating Galaxy (type={galaxy_type}, seed={galaxy_seed})...")

        # Set up RNG for deterministic generation
        rng: Optional[random.Random] = None
        if galaxy_seed is not None:
            rng = random.Random(galaxy_seed)
            # Also seed global random for star/planet generation
            random.seed(galaxy_seed)

        # Create placement strategy based on galaxy type
        if galaxy_type == "random":
            strategy = RandomPlacementStrategy()
        else:
            # Load layout configuration
            loader = GalaxyLayoutsLoader()
            layout_config = loader.load_and_scale(galaxy_type, galaxy.radius)

            # Create density map from config
            density_map = DensityMap.from_config(layout_config, galaxy.radius)
            strategy = DensityBasedPlacementStrategy(density_map)

        # Generate systems using the strategy
        systems = galaxy.generate_systems(
            count=config.system_count,
            min_dist=400,
            placement_strategy=strategy,
            rng=rng
        )
        galaxy.generate_warp_lanes()

        logger.info(f"GameInitializer: Generated {len(systems)} systems.")
        return systems

    @staticmethod
    def _setup_initial_scenario(systems: list, empires: List[Empire], config: GameConfig) -> None:
        """Set up starting colonies and homeworlds for all empires."""
        if not systems:
            return

        num_empires = len(empires)
        num_systems = len(systems)

        # Distribute starting colonies across the galaxy
        # Use evenly spaced system indices to spread empires apart
        if num_empires == 1:
            # Single player gets first system
            home_indices = [0]
        elif num_empires == 2:
            # Two players get first and last systems (opposite ends)
            home_indices = [0, num_systems - 1]
        elif num_empires == 3:
            # Three players: first, middle, last
            mid = num_systems // 2
            home_indices = [0, mid, num_systems - 1]
        else:  # 4+ players
            # Distribute evenly
            step = max(1, num_systems // num_empires)
            home_indices = [min(i * step, num_systems - 1) for i in range(num_empires)]

        # Assign home systems to empires
        for i, empire in enumerate(empires):
            if i < len(home_indices) and home_indices[i] < num_systems:
                home_sys = systems[home_indices[i]]
                if home_sys.planets:
                    # Assign first planet as home colony
                    home_planet = home_sys.planets[0]

                    # Adjust planet conditions to match species preferences (BUG-63)
                    if empire.race_config is not None:
                        GameInitializer._adjust_homeworld_to_race(home_planet, empire.race_config)

                    # Ensure minimum resource quality for fair starts
                    GameInitializer._ensure_homeworld_resource_quality(home_planet)

                    empire.add_colony(home_planet)

                    # Seed initial population if empire has race_config
                    if empire.race_config is not None:
                        initial_pop = SpeciesPopulation(
                            race_id=empire.race_config.race_id,
                            count=home_planet.max_population,
                            happiness=0.7
                        )
                        home_planet.populations.append(initial_pop)
                        logger.info(f"GameInitializer: Seeded {initial_pop.count} population on {home_planet.name}")

                    logger.info(f"GameInitializer: Empire '{empire.name}' home at system {home_indices[i]}")

    @staticmethod
    def _adjust_homeworld_to_race(planet, race_config) -> None:
        """Adjust a starting planet's conditions to match species ideal environment (BUG-63)."""
        from game.strategy.data.planet import PlanetType

        # Set planet type from homeworld type
        if race_config.homeworld_type:
            try:
                planet.planet_type = PlanetType[race_config.homeworld_type]
            except KeyError:
                pass  # Keep existing type if invalid

        # Set surface conditions to species ideals
        planet.surface_gravity = race_config.gravity_ideal * 9.81
        planet.surface_temperature = race_config.temperature_ideal
        planet.surface_water = race_config.water_ideal

        # Build atmosphere from preferences (positive preferences = present gases)
        # Use 1 ATM total pressure, distributed by positive preference weights
        # Translate display names ("Oxygen") to chemical formulas ("O2") for rendering
        from game.strategy.data.race_config import GAS_NAME_TO_FORMULA
        atm_prefs = race_config.atmosphere_preferences
        positive_gases = {gas: val for gas, val in atm_prefs.items() if val > 0}

        if positive_gases:
            total_weight = sum(positive_gases.values())
            one_atm = 101325.0  # Pa
            planet.atmosphere = {}
            for gas, val in positive_gases.items():
                formula = GAS_NAME_TO_FORMULA.get(gas, gas)
                planet.atmosphere[formula] = (val / total_weight) * one_atm
            planet.surface_pressure = one_atm
        else:
            # No positive gas preferences - minimal atmosphere
            planet.atmosphere = {}
            planet.surface_pressure = 0.0

        logger.info(f"GameInitializer: Adjusted {planet.name} to match species preferences "
                 f"(type={planet.planet_type.name}, gravity={planet.surface_gravity/9.81:.1f}g, "
                 f"temp={planet.surface_temperature:.0f}K, water={planet.surface_water:.0%})")

    @staticmethod
    def _ensure_homeworld_resource_quality(planet) -> None:
        """Ensure homeworld resources meet minimum quality floor for fair starts."""
        from game.strategy.data.resource_generation_config import get_resource_generation_config
        cfg = get_resource_generation_config()
        floor = cfg.homeworld_quality_floor

        for resource_name, resource_data in planet.resources.items():
            if resource_data.get('quality', 0.0) < floor:
                resource_data['quality'] = floor

        logger.info(f"GameInitializer: Enforced quality floor {floor} on {planet.name}")
