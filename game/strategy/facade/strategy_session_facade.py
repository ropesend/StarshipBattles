"""Strategy Session Facade.

Provides a strict facade for UI-to-engine communication using CQRS-lite pattern.
All state mutations go through Commands, all reads return immutable DTOs.
"""
import logging
from typing import List, Optional, TYPE_CHECKING

from game.core.hex_math import HexCoord

logger = logging.getLogger(__name__)
from game.core.validation import ValidationResult
from game.strategy.facade.dto import (
    FleetInfo,
    StarInfo,
    SystemInfo,
    PlanetInfo,
    EmpireInfo,
    ColonySummary,
    FleetSummary,
    BuildQueueSourceDTO,
    ColonyDemographicView,
    SpeciesDemographicView,
)

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.strategy.engine.game_session import GameSession
    from game.strategy.engine.commands import Command


class StrategySessionFacade:
    """Facade for UI interaction with the strategy game session.

    This facade provides the single point of access for all UI-to-engine
    communication, implementing a CQRS-lite pattern:
    - Commands (writes): State mutations via handle_command()
    - Queries (reads): Return immutable DTOs, never domain objects

    The UI layer should never access GameSession internals directly.
    All domain objects are converted to DTOs before being returned.

    Attributes:
        _session: The underlying GameSession (private, not for UI access)
    """

    def __init__(self, session: 'GameSession') -> None:
        """Initialize the facade with a GameSession.

        Args:
            session: The GameSession instance to wrap
        """
        self._session = session
        # PROJ-254: Lazy index caches for O(1) lookups
        self._planet_index: Optional[dict] = None  # id -> Planet
        self._all_stars_cache: Optional[List[StarInfo]] = None
        self._all_stars_cache_turn: int = -1
        self._fleets_by_hex_cache: Optional[dict] = None  # HexCoord -> [Fleet]
        self._fleets_by_hex_turn: int = -1
        # PROJ-287: Lazy-init session-scoped race registry
        self._race_registry: Optional['IRaceRegistry'] = None

    # =========================================================================
    # COMMANDS (Write Path)
    # =========================================================================

    def handle_command(self, command: 'Command') -> ValidationResult:
        """Execute a command against the game session.

        All state mutations should go through this method. The command
        is validated and executed by the underlying GameSession.

        Args:
            command: The command to execute

        Returns:
            ValidationResult indicating success or failure with error details
        """
        return self._session.handle_command(command)

    def process_turn(self) -> None:
        """Process the current turn.

        This advances the game state by one turn, executing all queued
        orders, resolving movement, and processing AI actions.
        """
        self._session.process_turn()
        # PROJ-254: Invalidate caches after turn processing changes game state
        self._fleets_by_hex_cache = None
        self._planet_index = None
        self._all_stars_cache = None

    # --- Command Dispatch Helpers ---
    def dispatch_issue_colonize(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueColonizeCommand."""
        from game.strategy.engine.commands import IssueColonizeCommand
        return self.handle_command(IssueColonizeCommand(**kwargs))

    def dispatch_issue_move(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueMoveCommand."""
        from game.strategy.engine.commands import IssueMoveCommand
        return self.handle_command(IssueMoveCommand(**kwargs))

    def dispatch_issue_intercept(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueInterceptCommand."""
        from game.strategy.engine.commands import IssueInterceptCommand
        return self.handle_command(IssueInterceptCommand(**kwargs))

    def dispatch_issue_join_fleet(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueJoinFleetCommand."""
        from game.strategy.engine.commands import IssueJoinFleetCommand
        return self.handle_command(IssueJoinFleetCommand(**kwargs))

    def dispatch_queue_colonize_mission(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch QueueColonizeMissionCommand."""
        from game.strategy.engine.commands import QueueColonizeMissionCommand
        return self.handle_command(QueueColonizeMissionCommand(**kwargs))

    def dispatch_clear_orders(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch ClearOrdersCommand."""
        from game.strategy.engine.commands import ClearOrdersCommand
        return self.handle_command(ClearOrdersCommand(**kwargs))

    def dispatch_issue_transfer(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueTransferCommand."""
        from game.strategy.engine.commands import IssueTransferCommand
        return self.handle_command(IssueTransferCommand(**kwargs))

    def dispatch_issue_implode_planet(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueImplodePlanetCommand."""
        from game.strategy.engine.commands import IssueImplodePlanetCommand
        return self.handle_command(IssueImplodePlanetCommand(**kwargs))

    def dispatch_issue_stellerate_star(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueStellerateStarCommand."""
        from game.strategy.engine.commands import IssueStellerateStarCommand
        return self.handle_command(IssueStellerateStarCommand(**kwargs))

    def dispatch_issue_open_warp_point(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueOpenWarpPointCommand."""
        from game.strategy.engine.commands import IssueOpenWarpPointCommand
        return self.handle_command(IssueOpenWarpPointCommand(**kwargs))

    def dispatch_issue_close_warp_point(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueCloseWarpPointCommand."""
        from game.strategy.engine.commands import IssueCloseWarpPointCommand
        return self.handle_command(IssueCloseWarpPointCommand(**kwargs))

    def dispatch_issue_create_dyson_sphere(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueCreateDysonSphereCommand."""
        from game.strategy.engine.commands import IssueCreateDysonSphereCommand
        return self.handle_command(IssueCreateDysonSphereCommand(**kwargs))

    def dispatch_issue_self_destruct(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueSelfDestructCommand."""
        from game.strategy.engine.commands import IssueSelfDestructCommand
        return self.handle_command(IssueSelfDestructCommand(**kwargs))

    def dispatch_queue_implode_planet_mission(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch QueueImplodePlanetMissionCommand."""
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand
        return self.handle_command(QueueImplodePlanetMissionCommand(**kwargs))

    def dispatch_queue_stellerate_star_mission(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch QueueStellerateStarMissionCommand."""
        from game.strategy.engine.commands import QueueStellerateStarMissionCommand
        return self.handle_command(QueueStellerateStarMissionCommand(**kwargs))

    def dispatch_queue_open_warp_point_mission(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch QueueOpenWarpPointMissionCommand."""
        from game.strategy.engine.commands import QueueOpenWarpPointMissionCommand
        return self.handle_command(QueueOpenWarpPointMissionCommand(**kwargs))

    def dispatch_queue_close_warp_point_mission(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch QueueCloseWarpPointMissionCommand."""
        from game.strategy.engine.commands import QueueCloseWarpPointMissionCommand
        return self.handle_command(QueueCloseWarpPointMissionCommand(**kwargs))

    def dispatch_queue_create_dyson_sphere_mission(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch QueueCreateDysonSphereMissionCommand."""
        from game.strategy.engine.commands import QueueCreateDysonSphereMissionCommand
        return self.handle_command(QueueCreateDysonSphereMissionCommand(**kwargs))

    def dispatch_issue_warp(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueWarpCommand."""
        from game.strategy.engine.commands import IssueWarpCommand
        return self.handle_command(IssueWarpCommand(**kwargs))

    def dispatch_issue_build_order(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssueBuildOrderCommand."""
        from game.strategy.engine.commands import IssueBuildOrderCommand
        return self.handle_command(IssueBuildOrderCommand(**kwargs))

    def dispatch_remove_build_order(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch RemoveBuildOrderCommand."""
        from game.strategy.engine.commands import RemoveBuildOrderCommand
        return self.handle_command(RemoveBuildOrderCommand(**kwargs))

    def dispatch_split_fleet(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch SplitFleetCommand."""
        from game.strategy.engine.commands import SplitFleetCommand
        return self.handle_command(SplitFleetCommand(**kwargs))

    def dispatch_delete_order(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch DeleteOrderCommand."""
        from game.strategy.engine.commands import DeleteOrderCommand
        return self.handle_command(DeleteOrderCommand(**kwargs))

    def dispatch_reorder_order(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch ReorderOrderCommand."""
        from game.strategy.engine.commands import ReorderOrderCommand
        return self.handle_command(ReorderOrderCommand(**kwargs))

    def dispatch_add_to_construction_queue(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch AddToConstructionQueueCommand."""
        from game.strategy.engine.commands import AddToConstructionQueueCommand
        return self.handle_command(AddToConstructionQueueCommand(**kwargs))

    def dispatch_remove_from_construction_queue(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch RemoveFromConstructionQueueCommand."""
        from game.strategy.engine.commands import RemoveFromConstructionQueueCommand
        return self.handle_command(RemoveFromConstructionQueueCommand(**kwargs))

    def dispatch_reorder_construction_queue(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch ReorderConstructionQueueCommand."""
        from game.strategy.engine.commands import ReorderConstructionQueueCommand
        return self.handle_command(ReorderConstructionQueueCommand(**kwargs))

    def dispatch_issue_planet_order(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch IssuePlanetOrderCommand."""
        from game.strategy.engine.commands import IssuePlanetOrderCommand
        return self.handle_command(IssuePlanetOrderCommand(**kwargs))

    def dispatch_clear_planet_orders(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch ClearPlanetOrdersCommand."""
        from game.strategy.engine.commands import ClearPlanetOrdersCommand
        return self.handle_command(ClearPlanetOrdersCommand(**kwargs))

    def dispatch_delete_planet_order(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch DeletePlanetOrderCommand."""
        from game.strategy.engine.commands import DeletePlanetOrderCommand
        return self.handle_command(DeletePlanetOrderCommand(**kwargs))

    def dispatch_set_atmosphere_target(self, **kwargs) -> 'ValidationResult':
        """Helper to dispatch SetAtmosphereTargetCommand."""
        from game.strategy.engine.commands import SetAtmosphereTargetCommand
        return self.handle_command(SetAtmosphereTargetCommand(**kwargs))

    # =========================================================================
    # QUERIES (Read Path) - Return DTOs only, never domain objects
    # =========================================================================

    # --- Fleet Queries ---

    def _get_fleet_by_id(self, fleet_id: int):
        """Internal helper to get a fleet by ID across all empires.

        Delegates to GameSession._get_fleet_by_id() for O(1) lookup with fallback.

        Args:
            fleet_id: The fleet ID to find

        Returns:
            The Fleet domain object if found, None otherwise
        """
        return self._session._get_fleet_by_id(fleet_id)

    def _get_empire_by_id(self, empire_id: int):
        """Internal helper to get an empire by ID.

        Args:
            empire_id: The empire ID to find

        Returns:
            The Empire domain object if found, None otherwise
        """
        for empire in self._session.empires:
            if empire.id == empire_id:
                return empire
        return None

    def get_fleet(self, fleet_id: int) -> Optional[FleetInfo]:
        """Get fleet information by ID.

        Args:
            fleet_id: The unique fleet identifier

        Returns:
            FleetInfo DTO if found, None otherwise
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return None
        return FleetInfo.from_fleet(fleet)

    def _build_fleet_hex_index(self) -> dict:
        """Build HexCoord -> [Fleet] lookup dict (PROJ-254)."""
        index: dict = {}
        for empire in self._session.empires:
            for fleet in empire.fleets:
                loc = fleet.location
                if loc not in index:
                    index[loc] = []
                index[loc].append(fleet)
        return index

    def get_fleets_at_hex(self, hex_coord: HexCoord) -> List[FleetInfo]:
        """Get all fleets at a specific hex coordinate.

        PROJ-254: Uses per-turn cached hex index for O(1) lookup.

        Args:
            hex_coord: The hex coordinate to query

        Returns:
            List of FleetInfo DTOs for fleets at the hex
        """
        current_turn = getattr(self._session, 'turn_number', 0)
        if self._fleets_by_hex_cache is None or self._fleets_by_hex_turn != current_turn:
            self._fleets_by_hex_cache = self._build_fleet_hex_index()
            self._fleets_by_hex_turn = current_turn

        fleets = self._fleets_by_hex_cache.get(hex_coord, [])
        return [FleetInfo.from_fleet(f) for f in fleets]

    def get_fleet_path_preview(
        self, fleet_id: int, target_hex: HexCoord
    ) -> Optional[List[HexCoord]]:
        """Calculate a path preview for a fleet to a target.

        This is used for UI pathfinding preview without committing
        to a move order.

        Args:
            fleet_id: The fleet to calculate path for
            target_hex: The destination hex

        Returns:
            List of HexCoords representing the path, or None if invalid
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return None
        return self._session.preview_fleet_path(fleet, target_hex)

    def get_fleet_path_projection(
        self, fleet_id: int, max_turns: int = 50
    ) -> List[dict]:
        """Get turn-by-turn path projection for a fleet.

        Args:
            fleet_id: The fleet to get projection for
            max_turns: Maximum number of turns to project

        Returns:
            List of dicts with turn-by-turn movement info
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return []
        return self._session.get_fleet_path_projection(fleet, max_turns)

    # --- System Queries ---

    def get_all_systems(self) -> List[SystemInfo]:
        """Get information about all star systems.

        Returns:
            List of SystemInfo DTOs for all systems in the galaxy
        """
        return [
            SystemInfo.from_star_system(system)
            for system in self._session.galaxy.systems.values()
        ]

    def get_all_stars(self) -> List[StarInfo]:
        """Get information about all stars in the galaxy.

        Returns enriched StarInfo DTOs with system context (system name,
        global location, planet count, companion star count).

        PROJ-254: Cached per turn — galaxy structure doesn't change mid-turn.

        Returns:
            List of StarInfo DTOs for all stars across all systems
        """
        current_turn = getattr(self._session, 'turn_number', 0)
        if self._all_stars_cache is not None and self._all_stars_cache_turn == current_turn:
            return self._all_stars_cache

        results = []
        for system in self._session.galaxy.systems.values():
            for star in system.stars:
                results.append(StarInfo.from_star(
                    star,
                    system_name=system.name,
                    system_global_location=system.global_location,
                    planet_count=len(system.planets),
                    total_star_count=len(system.stars),
                ))
        self._all_stars_cache = results
        self._all_stars_cache_turn = current_turn
        return results

    def get_system_at_hex(self, hex_coord: HexCoord) -> Optional[SystemInfo]:
        """Get the system at a specific hex coordinate.

        Args:
            hex_coord: The hex coordinate to query (can be global center or any hex in system)

        Returns:
            SystemInfo DTO if a system exists at the hex, None otherwise
        """
        system = self._session.galaxy.get_system_at_location(hex_coord)
        if system is None:
            return None
        return SystemInfo.from_star_system(system)

    def get_system_containing_fleet(self, fleet_id: int) -> Optional[SystemInfo]:
        """Get the system containing (or closest to) the fleet.
        
        This handles cases where the fleet is in empty space within a system's logic bounds
        but not at a specific system object.
        
        Args:
            fleet_id: The fleet to find system for.
            
        Returns:
            SystemInfo DTO if fluidly within a system, None if in deep space.
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None: 
            return None
            
        return self.get_system_near_hex(fleet.location)

    def get_system_near_hex(self, hex_coord: HexCoord, max_dist: int = 8) -> Optional[SystemInfo]:
        """Get the system at or near the given hex coordinate.
        
        This is useful for resolving clicks that might be slightly off a system's strict location,
        or for finding the enclosing system when an entity is in 'empty space' within a system.
        
        Args:
            hex_coord: The hex coordinate to query.
            max_dist: Maximum distance to scan for a system (default 8 hexes).
            
        Returns:
            SystemInfo DTO if a system is found, None otherwise.
        """
        # 1. Try strict lookup first
        system = self._session.galaxy.get_system_at_location(hex_coord)
        if system:
            return SystemInfo.from_star_system(system)
            
        # 2. Proximity check
        from game.core.hex_math import hex_distance
        closest_system = None
        min_dist = max_dist + 1
        
        for sys in self._session.galaxy.systems.values():
            dist = hex_distance(sys.global_location, hex_coord)
            if dist < min_dist:
                min_dist = dist
                closest_system = sys
                
        if closest_system:
            return SystemInfo.from_star_system(closest_system)
            
        return None

    # --- Planet Queries ---

    def _build_planet_index(self) -> dict:
        """Build planet ID -> Planet lookup dict (PROJ-254)."""
        index = {}
        for system in self._session.galaxy.systems.values():
            for planet in system.planets:
                index[planet.id] = planet
        return index

    def _get_planet_by_id(self, planet_id: int):
        """Internal helper to get a planet by ID using index (PROJ-254).

        Args:
            planet_id: The planet ID to find

        Returns:
            The Planet domain object if found, None otherwise
        """
        if self._planet_index is None:
            self._planet_index = self._build_planet_index()
        return self._planet_index.get(planet_id)

    def get_planet(self, planet_id: int) -> Optional[PlanetInfo]:
        """Get planet information by ID.

        Args:
            planet_id: The unique planet identifier

        Returns:
            PlanetInfo DTO if found, None otherwise
        """
        planet = self._get_planet_by_id(planet_id)
        if planet is None:
            return None
        return PlanetInfo.from_planet(planet)

    def get_planets_at_hex(self, hex_coord: HexCoord) -> List[PlanetInfo]:
        """Get planets whose global position exactly matches the given hex coordinate.

        Only returns planets at the specific hex — not all planets in the system.
        A planet's global position is ``system.global_location + planet.location``.
        Uses radius search to resolve which system owns the hex when a strict
        lookup misses (e.g. clicking an inner hex that isn't the system center).

        Args:
            hex_coord: The exact global hex coordinate to match against planet positions.

        Returns:
            List of PlanetInfo DTOs for planets at this exact hex (may be empty).
        """
        # 1. Try strict lookup first (fast & correct for exact hits)
        system = self._session.galaxy.get_system_at_location(hex_coord)
        
        # 2. If strict failed, try radius/ownership lookup (robust for area clicks)
        if system is None:
            from game.strategy.data.pathfinding import get_system_at_hex
            system = get_system_at_hex(self._session.galaxy, hex_coord, radius=50)
            
        if system is None:
            return []
        
        target_planets = []
        for p in system.planets:
            p_global = system.global_location + p.location
            if p_global == hex_coord:
                target_planets.append(p)
                
        return [PlanetInfo.from_planet(planet) for planet in target_planets]

    # --- Empire Queries ---

    def get_all_empires(self) -> List[EmpireInfo]:
        """Get information about all empires.

        Returns:
            List of EmpireInfo DTOs for all empires
        """
        return [
            EmpireInfo.from_empire(empire)
            for empire in self._session.empires
        ]

    def get_empire(self, empire_id: int) -> Optional[EmpireInfo]:
        """Get empire information by ID.

        Args:
            empire_id: The unique empire identifier

        Returns:
            EmpireInfo DTO if found, None otherwise
        """
        empire = self._get_empire_by_id(empire_id)
        if empire is None:
            return None
        return EmpireInfo.from_empire(empire)

    def get_empire_colonies(self, empire_id: int) -> List[ColonySummary]:
        """Get colony summaries for an empire.

        Args:
            empire_id: The empire to get colonies for

        Returns:
            List of ColonySummary DTOs for the empire's colonies
        """
        empire = self._get_empire_by_id(empire_id)
        if empire is None:
            return []
        return [ColonySummary.from_planet(planet) for planet in empire.colonies]

    def get_empire_fleets(self, empire_id: int) -> List[FleetSummary]:
        """Get fleet summaries for an empire.

        Args:
            empire_id: The empire to get fleets for

        Returns:
            List of FleetSummary DTOs for the empire's fleets
        """
        empire = self._get_empire_by_id(empire_id)
        if empire is None:
            return []
        return [FleetSummary.from_fleet(fleet) for fleet in empire.fleets]

    def get_empire_build_queues(self, empire_id: int) -> List[BuildQueueSourceDTO]:
        """Get all build queue sources for an empire.

        Args:
            empire_id: The unique empire identifier

        Returns:
            List of BuildQueueSourceDTOs for the empire
        """
        from game.strategy.data.build_queue_source import collect_all_build_queues_for_empire
        empire = self._get_empire_by_id(empire_id)
        if empire is None:
            return []
        sources = collect_all_build_queues_for_empire(empire, registries=self._session.registries)
        return [BuildQueueSourceDTO.from_domain(source) for source in sources]

    def get_hex_build_queues(self, empire_id: int, hex_coord: HexCoord) -> List[BuildQueueSourceDTO]:
        """Get all build queue sources at a hex for a specific empire.

        Args:
            empire_id: The unique empire identifier
            hex_coord: The target coordinate to search

        Returns:
            List of BuildQueueSourceDTOs at that hex.
        """
        from game.strategy.data.build_queue_source import collect_build_queues_at_hex
        empire = self._get_empire_by_id(empire_id)
        if empire is None:
            return []
        sources = collect_build_queues_at_hex(hex_coord, self._session.galaxy, empire, registries=self._session.registries)
        return [BuildQueueSourceDTO.from_domain(source) for source in sources]

    # --- Game State Queries ---

    def get_human_player_ids(self) -> List[int]:
        """Get the empire IDs of human players.

        Returns:
            List of empire IDs that are controlled by human players
        """
        return list(self._session.human_player_ids)

    def get_turn_number(self) -> int:
        """Get the current turn number.

        Returns:
            The current turn number (1-indexed)
        """
        return self._session.turn_number

    # --- Colony Demographics (PROJ-288) ---

    def get_colony_demographic_view(
        self, planet_id: int
    ) -> Optional[ColonyDemographicView]:
        """One-shot snapshot of a colony's per-species + per-resource state.

        Bundles everything a demographics-style UI panel needs (per-species
        habitability + happiness + projected growth + food slider state +
        per-resource harvest/upkeep/yard/net + total upkeep across the
        colony) into a single immutable DTO so consumers don't re-derive
        the math each frame.

        Returns ``None`` for unowned planets, missing planet ids, or
        species whose ``race_id`` cannot be resolved by the session
        ``IRaceRegistry`` (those species are silently dropped — UI can
        warn separately if it cares).

        See `docs/04_SERVICES.md` § PlanetEconomyProjector and PROJ-288
        design.md § 3 for the underlying contracts.
        """
        # Inline imports keep the facade's top-level import surface narrow,
        # mirroring the pattern used by the command-dispatch helpers and by
        # `get_race_registry` (PROJ-287).
        from game.strategy.formulas.colony_output import projected_growth_rate
        from game.strategy.formulas.habitability import score_planet_for_race
        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )

        planet = self._get_planet_by_id(planet_id)
        if planet is None or planet.owner_id is None:
            return None

        race_registry = self.get_race_registry()
        economy = self._resolve_economy_config()
        registries = getattr(self._session, "registries", None)

        projector = PlanetEconomyProjector(
            registries=registries,
            economy_config=economy,
            race_registry=race_registry,
        )
        projections = projector.project(planet)

        species_views: list = []
        for pop in planet.populations:
            race_config = race_registry.get_race(pop.race_id)
            if race_config is None:
                # Save drift / typo: skip rather than crash. The projector's
                # habitability multiplier already excludes these species too.
                continue
            cfg = planet.get_species_config(pop.race_id)
            display_name = (
                getattr(race_config, "race_name", "")
                or getattr(race_config, "name", "")
                or pop.race_id
            )
            species_views.append(SpeciesDemographicView(
                race_id=pop.race_id,
                race_name=display_name,
                count=pop.count,
                habitability=score_planet_for_race(planet, race_config),
                happiness=pop.happiness,
                growth_rate=projected_growth_rate(planet, pop, race_config, cfg),
                food_ratio=cfg.last_food_ratio,
                food_allocation=cfg.food_allocation,
            ))

        species_views.sort(key=lambda s: s.count, reverse=True)

        # Sum per-resource upkeep across species into the empire-aggregation
        # summary. Mirrors `OrganicsConsumptionEngine._process_colony` math.
        total_upkeep: dict = {}
        for pop in planet.populations:
            count = getattr(pop, "count", 0)
            if count <= 0:
                continue
            cfg = planet.get_species_config(pop.race_id)
            for resource_id, per_pop_rate in economy.population_consumption.items():
                total_upkeep[resource_id] = (
                    total_upkeep.get(resource_id, 0.0)
                    + count * cfg.food_allocation * per_pop_rate
                )

        return ColonyDemographicView(
            planet_id=planet.id,
            planet_name=planet.name,
            species=tuple(species_views),
            resource_projections=tuple(projections.values()),
            total_upkeep=total_upkeep,
        )

    def _resolve_economy_config(self):
        """Pull the active EconomyConfig from the session, falling back to
        the module default. The session attribute is optional — older
        sessions may not carry it, in which case `get_default_economy_config`
        lazy-loads `data/economy.json`."""
        economy = getattr(self._session, "economy_config", None)
        if economy is not None:
            return economy
        from game.strategy.config.economy_config import get_default_economy_config
        return get_default_economy_config()

    # --- Race Registry (PROJ-287) ---

    def get_race_registry(self) -> 'IRaceRegistry':
        """Get the session-scoped race registry (PROJ-287).

        Returns a cached ``CachedRaceRegistry`` wrapping a ``RaceLibrary``.
        The registry is lazily constructed on first access and reused for
        the remainder of the session, so UI panels and formulas can resolve
        ``race_id -> RaceConfig`` without per-call filesystem reads.

        Callers that mutate races (e.g. the race editor on save) must call
        ``registry.invalidate(race_id)`` after a successful save to keep
        subsequent reads coherent.
        """
        if self._race_registry is None:
            from game.strategy.systems.race_library import (
                CachedRaceRegistry,
                RaceLibrary,
            )
            self._race_registry = CachedRaceRegistry(RaceLibrary())
        return self._race_registry

    # --- Event Log Queries (PROJ-77) ---

    def get_turn_events(self, turn: int = None) -> List[dict]:
        """Get events for a specific turn (or current turn if None).

        Args:
            turn: The turn number to query. Defaults to current turn.

        Returns:
            List of event dicts (immutable for UI consumption).
        """
        if turn is None:
            turn = self._session.turn_number
        events = self._session.event_log.get_events_for_turn(turn)
        return [e.to_dict() for e in events]

    def get_all_events(self) -> List[dict]:
        """Get all events from the event log.

        Returns:
            List of all event dicts (immutable for UI consumption).
        """
        return [e.to_dict() for e in self._session.event_log.get_all_events()]

    def get_events_by_category(self, category: str) -> List[dict]:
        """Get events filtered by category.

        Args:
            category: Category string or EventCategory enum value to filter by.

        Returns:
            List of matching event dicts (immutable for UI consumption).
        """
        events = self._session.event_log.get_events_by_category(category)
        return [e.to_dict() for e in events]

    # --- Validation Queries ---

    def can_colonize(
        self, fleet_id: int, planet_id: Optional[int]
    ) -> ValidationResult:
        """Check if a fleet can colonize a planet.

        This validates colonization without executing the command.

        Args:
            fleet_id: The fleet to check
            planet_id: The target planet (or None to check current location)

        Returns:
            ValidationResult indicating whether colonization is valid
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return ValidationResult.error("Fleet not found.")

        planet = None
        if planet_id is not None:
            planet = self._get_planet_by_id(planet_id)
            if planet is None:
                return ValidationResult.error("Planet not found.")

        return self._session.turn_engine.validate_colonize_order(
            self._session.galaxy, fleet, planet
        )

    def can_move_to(self, fleet_id: int, target_hex: HexCoord) -> ValidationResult:
        """Check if a fleet can move to a target hex.

        This validates movement by checking if a path exists.

        Args:
            fleet_id: The fleet to check
            target_hex: The destination hex

        Returns:
            ValidationResult indicating whether the move is valid
        """
        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return ValidationResult.error("Fleet not found.")

        path = self._session.preview_fleet_path(fleet, target_hex)
        if path is None:
            return ValidationResult.error("No path to target hex.")

        return ValidationResult.success()

    # --- Colony Pod Queries (PROJ-55) ---

    def get_fleet_remaining_pods(self, fleet_id: int) -> dict:
        """Get remaining colony pods for a fleet (available minus committed).

        Drop pods are universal — any pod works on any planet type.

        Args:
            fleet_id: The fleet to check

        Returns:
            Dict with 'drop_pod' key mapped to remaining (uncommitted) count.
            Example: {"drop_pod": 2}
            Returns empty dict if fleet not found.
        """
        from game.strategy.validation.colonize_validator import ColonizeValidator

        fleet = self._get_fleet_by_id(fleet_id)
        if fleet is None:
            return {}

        available = ColonizeValidator.count_drop_pods(fleet)
        committed = ColonizeValidator.count_committed_colonize_orders(fleet)
        return {'drop_pod': available - committed}

    # --- Game State Queries (PROJ-208 Phase 4) ---

    def get_save_path(self) -> Optional[str]:
        """Get the current save game file path.

        Returns:
            The save file path, or None if not yet saved.
        """
        return self._session.save_path

    # --- Storm Queries (PROJ-215 Phase 5) ---

    def get_storm_names_at_hex(self, hex_coord: HexCoord) -> List[str]:
        """Get storm names affecting a global hex coordinate.

        Uses AreaEffectManager to query the galaxy's zone spatial index
        for storms at the given hex.

        Args:
            hex_coord: Global hex coordinate to query.

        Returns:
            List of storm names at this hex, or empty list if no storms.
        """
        from game.strategy.services.area_effect_manager import AreaEffectManager

        manager = AreaEffectManager()
        effects = manager.get_effects_at_global_hex(self._session.galaxy, hex_coord)
        return effects.storm_names if effects.in_storm else []
