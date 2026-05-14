"""
GameInitializer - Handles galaxy and empire initialization.

Extracted from GameSession (PROJ-87 Phase 6) to isolate initialization
logic from session management.

Provides a single entry point for creating new game galaxies with empires.
"""
import logging
import random
from typing import Any, List, Optional, Tuple

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.strategy.data.empire import Empire

logger = logging.getLogger(__name__)
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.engine.game_config import GameConfig
from game.strategy.generation.placement_strategies import (
    RandomPlacementStrategy,
    DensityBasedPlacementStrategy,
)
from game.strategy.generation.density.density_map import DensityMap
from game.strategy.generation.loaders.galaxy_layouts_loader import GalaxyLayoutsLoader


# FEAT-27: at N=1 with E>1 the lone star system must contain at least
# one planet per empire. Some system blueprints (e.g. binary_no_planets,
# empty_warp_hub) can roll 0–1 planets, so when an attempt produces too
# few planets we regenerate up to this many times before raising.
_PLANET_SHORTAGE_RETRY_ATTEMPTS: int = 10


class _PlanetShortageError(Exception):
    """Internal: raised by _setup_initial_scenario when the lone N=1
    system has fewer planets than empires. Caught by `initialize()` to
    drive the regeneration retry loop."""


class GameInitializer:
    """
    Handles initialization of new game galaxies and empires.

    Provides a single static entry point for creating game content.
    """

    @staticmethod
    def initialize(
        config: GameConfig,
        *,
        planet_mutator: Any = None,
        empire_mutator: Any = None,
    ) -> Tuple[Galaxy, List[Empire]]:
        """
        Initialize a new game galaxy and empires from configuration.

        FEAT-27 — At N=1 with multiple empires, the lone system must
        contain enough planets for each empire to homestead. If the
        first generated system is short on planets we re-roll up to
        ``_PLANET_SHORTAGE_RETRY_ATTEMPTS`` times before raising
        ``ValidationException``.

        Args:
            config: Game configuration with player, galaxy, and seed settings.
            planet_mutator: PROJ-370 ``IPlanetMutator``. When supplied (the
                production path via ``GameSession``), homeworld population
                seeding routes through ``add_species_population``. When
                ``None`` (test fixtures), falls back to direct list append.
                Per PROJ-370 review MAJ-002.
            empire_mutator: PROJ-370 ``IEmpireMutator``. When supplied,
                attempt-restart colony reset routes through
                ``clear_colonies``. When ``None``, direct list clear.

        Returns:
            Tuple of (Galaxy, list[Empire]) ready for gameplay.
        """
        # Create empires from config (deterministic — does not consume RNG)
        empires = GameInitializer._create_empires(config)

        last_error: Optional[_PlanetShortageError] = None
        for attempt in range(_PLANET_SHORTAGE_RETRY_ATTEMPTS):
            galaxy = Galaxy(radius=config.galaxy_radius)
            attempt_config = config
            if attempt > 0 and config.galaxy_seed is not None:
                # Perturb the seed deterministically so each retry rolls a
                # fresh blueprint without polluting global random state.
                # Use dataclasses.replace to keep all other fields intact.
                from dataclasses import replace
                attempt_config = replace(config, galaxy_seed=config.galaxy_seed + attempt)

            systems = GameInitializer._initialize_galaxy(galaxy, attempt_config)

            try:
                # Reset any colony state from a prior failed attempt before
                # re-running placement (empires are reused across attempts).
                # PROJ-370 review MAJ-002: route through IEmpireMutator
                # unconditionally. If no mutator was supplied (test paths
                # that call initialize() directly), lazy-construct an
                # EmpireWriteService — same shape as the lazy-defaults in
                # superweapon_order_processor / post_battle_hook.
                emp_mut = empire_mutator
                if emp_mut is None:
                    from game.strategy.services.empire_write_service import (
                        EmpireWriteService,
                    )
                    emp_mut = EmpireWriteService()
                for empire in empires:
                    emp_mut.clear_colonies(empire)
                GameInitializer._setup_initial_scenario(
                    systems, empires, attempt_config,
                    planet_mutator=planet_mutator,
                )
                break
            except _PlanetShortageError as exc:
                last_error = exc
                logger.info(
                    "GameInitializer: planet shortage at N=1 on attempt %d/%d (%s); regenerating",
                    attempt + 1, _PLANET_SHORTAGE_RETRY_ATTEMPTS, exc,
                )
                continue
        else:
            raise ValidationException(
                "Galaxy generation could not produce a single-system layout "
                f"with at least {len(empires)} planets after "
                f"{_PLANET_SHORTAGE_RETRY_ATTEMPTS} attempts. "
                "Try a different seed or fewer players.",
                code=ErrorCode.VALIDATION_FAILED.value,
                context={
                    "system_count": config.system_count,
                    "num_empires": len(empires),
                    "attempts": _PLANET_SHORTAGE_RETRY_ATTEMPTS,
                    "last_error": str(last_error) if last_error else None,
                },
            )

        # PROJ-219: Set galaxy back-references for auto fleet registration
        for empire in empires:
            empire.set_galaxy(galaxy)

        # PROJ-305: wire fleet lookups so FleetAbilitySource surfaces in the
        # ability iterator. Without this, _fleet_provider yields nothing and
        # fleet sector-effects (e.g. Flagship Shield Projector) never render.
        GameInitializer._wire_fleet_lookups(galaxy, empires)

        return galaxy, empires

    @staticmethod
    def _wire_fleet_lookups(galaxy: Galaxy, empires: List[Empire]) -> None:
        """PROJ-305: register fleet-at-hex / fleets-in-system callbacks with
        the unified ability iterator. The closures hold a reference to the
        empires list (mutable — new fleets and dead empires are both seen).
        """
        from game.strategy.services.ability_iterator import set_fleet_lookups

        def _at_hex(system, hex_coord):
            for empire in empires:
                for fleet in getattr(empire, 'fleets', []) or []:
                    if getattr(fleet, 'location', None) == hex_coord:
                        yield fleet

        def _in_system(system):
            sys_loc = getattr(system, 'global_location', None)
            if sys_loc is None:
                return
            # System contains every hex within radius 50 of its global_location.
            # Cheap path: check fleets whose location is within that radius.
            from game.core.hex_math import hex_distance
            for empire in empires:
                for fleet in getattr(empire, 'fleets', []) or []:
                    floc = getattr(fleet, 'location', None)
                    if floc is None:
                        continue
                    try:
                        if hex_distance(floc, sys_loc) <= 50:
                            yield fleet
                    except Exception:  # Intentional broad catch: hex impl errors don't poison iteration
                        continue

        set_fleet_lookups(at_hex=_at_hex, in_system=_in_system)

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
    def _empire_home_indices(num_empires: int, num_systems: int) -> List[int]:
        """FEAT-27: pick a home-system index for each empire.

        Two modes:
          * **N = 1 (shared-system mode):** every empire goes to system 0.
            Distinct planets are assigned downstream in
            ``_setup_initial_scenario``.
          * **N ≥ 2 (separated mode):** evenly spread empire homes across
            the galaxy with a hand-rolled linspace so each empire gets a
            unique system. The caller has already validated
            ``num_empires <= num_systems`` via ``GameConfig.__post_init__``.

        Returns:
            List of length ``num_empires`` with system indices.
        """
        if num_empires <= 1 or num_systems == 1:
            return [0] * num_empires
        # Hand-rolled linspace(0, N-1, E, dtype=int) — avoids a numpy dep.
        # For E=4, N=8 this produces [0, 2, 5, 7] (vs the old stair-step
        # [0, 2, 4, 6] which clustered empires at the low end).
        return [
            round(i * (num_systems - 1) / (num_empires - 1))
            for i in range(num_empires)
        ]

    @staticmethod
    def _setup_initial_scenario(
        systems: list,
        empires: List[Empire],
        config: GameConfig,
        *,
        planet_mutator: Any = None,
    ) -> None:
        """Set up starting colonies and homeworlds for all empires.

        FEAT-27 — At N=1 every empire shares ``systems[0]`` and is given
        a distinct planet. If the lone system has fewer planets than
        empires this raises ``_PlanetShortageError`` so that
        ``initialize()`` can drive a regeneration retry.

        PROJ-370 review MAJ-002: ``planet_mutator`` (when supplied) routes
        homeworld population seeding through ``IPlanetMutator``. ``None``
        falls back to direct list append for test paths.
        """
        if not systems:
            return

        num_empires = len(empires)
        num_systems = len(systems)
        home_indices = GameInitializer._empire_home_indices(num_empires, num_systems)

        # FEAT-27: at N=1, every empire colonises a distinct planet within
        # the lone system. Verify supply up-front so we can request a
        # regeneration retry instead of half-applying placement.
        if num_systems == 1 and num_empires > 1:
            lone = systems[0]
            if len(lone.planets) < num_empires:
                raise _PlanetShortageError(
                    f"single system '{lone.name}' has {len(lone.planets)} "
                    f"planet(s); need {num_empires}"
                )

        # Per-system counter so we hand each empire a different planet
        # when several empires share a home system (only at N=1, but the
        # mechanic is general).
        next_planet_in_system: dict[int, int] = {}

        for i, empire in enumerate(empires):
            sys_idx = home_indices[i]
            if sys_idx >= num_systems:
                continue
            home_sys = systems[sys_idx]
            if not home_sys.planets:
                continue

            planet_offset = next_planet_in_system.get(sys_idx, 0)
            if planet_offset >= len(home_sys.planets):
                # Should be unreachable at N≥2 (one empire per system) and
                # at N=1 it's caught above. Defensive fallback — log and
                # skip rather than overwrite a planet's owner.
                logger.warning(
                    "GameInitializer: no free planet in system %s for empire '%s'",
                    home_sys.name, empire.name,
                )
                continue
            home_planet = home_sys.planets[planet_offset]
            next_planet_in_system[sys_idx] = planet_offset + 1

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
                # PROJ-370 review MAJ-002: route through IPlanetMutator
                # unconditionally. Lazy-construct PlanetWriteService when
                # `planet_mutator` is None (test paths that call
                # ``_setup_initial_scenario`` directly).
                pl_mut = planet_mutator
                if pl_mut is None:
                    from game.strategy.services.planet_write_service import (
                        PlanetWriteService,
                    )
                    pl_mut = PlanetWriteService()
                pl_mut.add_species_population(home_planet, initial_pop)
                logger.info(f"GameInitializer: Seeded {initial_pop.count} population on {home_planet.name}")

            logger.info(
                "GameInitializer: Empire '%s' home at system %d planet %d",
                empire.name, sys_idx, planet_offset,
            )

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

        # PROJ-283 Phase 4: read setpoints from registry-driven preferences
        # (replaces the deleted `gravity_ideal`/`temperature_ideal`/etc. fields).
        prefs = race_config.preferences
        planet.surface_gravity = prefs["gravity"].setpoint  # already m/s^2
        planet.surface_temperature = prefs["temperature"].setpoint
        planet.surface_water = prefs["water"].setpoint

        # Build atmosphere from gas-factor setpoints (Pa already).
        atmosphere = {
            factor_id.split(".", 1)[1]: pref.setpoint
            for factor_id, pref in prefs.items()
            if factor_id.startswith("gas.") and pref.setpoint > 0
        }
        if atmosphere:
            planet.atmosphere = atmosphere
            planet.surface_pressure = sum(atmosphere.values())
        else:
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

        for resource_name, resource_data in planet.deposits.items():
            if resource_data.get('quality', 0.0) < floor:
                resource_data['quality'] = floor

        logger.info(f"GameInitializer: Enforced quality floor {floor} on {planet.name}")
