import random
from game.core.logger import log_debug, log_info, log_warning
from game.strategy.data.fleet import Fleet, OrderType
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.battle_state import BattleResults
    from game.strategy.interfaces.battle_resolver import IBattleResolver
    from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
    from game.strategy.engine.production_engine import ProductionEngine
    from game.strategy.engine.fleet_order_processor import FleetOrderProcessor


@dataclass
class ValidationResult:
    is_valid: bool
    message: str = ""
    error_code: Optional[str] = None


class TurnEngine:
    """
    Engine for processing strategy turns.

    PROJ-11 Phase 4: Supports dependency injection of IBattleResolver
    for clean separation between strategy and simulation layers.

    PROJ-12 Phase 3: Delegates to specialized engines:
    - FleetMovementEngine: Movement calculation and application
    - ProductionEngine: Construction queue processing
    - FleetOrderProcessor: Order lifecycle management
    """

    def __init__(self, battle_resolver: Optional['IBattleResolver'] = None):
        """
        Initialize the turn engine.

        Args:
            battle_resolver: Optional battle resolver implementation.
                           If None, defaults to SimulationBattleResolver.
        """
        # Battle seed counter for deterministic battles
        self._battle_seed_counter = 0

        # PROJ-11: Inject battle resolver for clean layer separation
        if battle_resolver is None:
            from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
            self._battle_resolver = SimulationBattleResolver()
        else:
            self._battle_resolver = battle_resolver

        # PROJ-12 Phase 3: Lazy-initialized specialized engines
        self._movement_engine: Optional['FleetMovementEngine'] = None
        self._production_engine: Optional['ProductionEngine'] = None
        self._order_processor: Optional['FleetOrderProcessor'] = None

    @property
    def movement_engine(self) -> 'FleetMovementEngine':
        """Lazy initialization of FleetMovementEngine."""
        if self._movement_engine is None:
            from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
            self._movement_engine = FleetMovementEngine()
        return self._movement_engine

    @property
    def production_engine(self) -> 'ProductionEngine':
        """Lazy initialization of ProductionEngine."""
        if self._production_engine is None:
            from game.strategy.engine.production_engine import ProductionEngine
            self._production_engine = ProductionEngine()
        return self._production_engine

    @property
    def order_processor(self) -> 'FleetOrderProcessor':
        """Lazy initialization of FleetOrderProcessor."""
        if self._order_processor is None:
            from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
            self._order_processor = FleetOrderProcessor()
        return self._order_processor

    def _generate_battle_seed(self) -> int:
        """Generate a deterministic seed for battles."""
        self._battle_seed_counter += 1
        return self._battle_seed_counter

    def process_turn(self, empires, galaxy, save_path=None):
        """
        Execute one full turn (100 sub-ticks).

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial calculations
            save_path: Path to savegame folder for loading designs during production
        """
        # 1. Subturn Loop (Movement & Combat)
        for tick in range(1, 101):
            self._process_tick(tick, empires, galaxy)

        # 2. End-of-Turn Orders (Static actions like Colonize)
        for empire in empires:
            # Iterate copy since fleets may be modified during processing
            # (e.g., colonization can remove/dissolve fleets)
            for fleet in list(empire.fleets):
                self._process_end_turn_orders(fleet, empire, galaxy)

        # 3. Production Phase
        self.process_production(empires, galaxy, save_path)
        
    def validate_colonize_order(self, galaxy, fleet, target_planet) -> ValidationResult:
        """
        Validate if a fleet can colonize a specific planet (or 'Any' if target_planet is None).
        
        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object attempting to colonize
            target_planet: The Planet object or None for 'Any'
            
        Returns:
            ValidationResult
        """
        # 1. Base Validation: Fleet must exist
        if not fleet:
            return ValidationResult(False, "Fleet does not exist.")
            
        # 2. Get System/Location Context - Use O(1) spatial index
        # Get all planets at the fleet's global hex location
        all_planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
        valid_candidates = [p for p in all_planets_at_hex if p.owner_id is None]
        
        # 3. Check Logic
        if target_planet is None:
            # "Any Planet"
            if not valid_candidates:
                return ValidationResult(False, "No colonizable planets at this location.", "NO_CANDIDATES")
            return ValidationResult(True, "Valid candidate found.")
            
        else:
            # Specific Planet
            if target_planet.owner_id is not None:
                return ValidationResult(False, f"Planet {target_planet.name} is already owned.", "ALREADY_OWNED")
            
            # Check if planet is in valid candidates (verifies location)
            # We strictly check reference equality or ID equality if we had IDs
            if target_planet not in valid_candidates:
                # Determine detailed reason for better feedback
                # If owner is none (checked above), then it must be location.
                return ValidationResult(False, f"Planet {target_planet.name} is not at fleet location.", "WRONG_LOCATION")

            return ValidationResult(True, "Planet is valid for colonization.")

    def process_production(self, empires, galaxy=None, save_path=None):
        """Process construction queues for all colonies.

        PROJ-12 Phase 3: Delegates to ProductionEngine.

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for fleet spawning
            save_path: Path to savegame folder for loading designs
        """
        self.production_engine.process_production(empires, galaxy, save_path)

    def _spawn_complex(self, planet, design_id, empire, save_path=None):
        """Add completed complex to planet's facilities.

        PROJ-12 Phase 3: Delegates to ProductionEngine.
        Kept for backward compatibility.
        """
        self.production_engine._spawn_complex(planet, design_id, empire, save_path)

    def _spawn_ship(self, planet, design_id, empire, galaxy, save_path=None):
        """Spawn ship/satellite/fighter as fleet with ShipInstance.

        PROJ-12 Phase 3: Delegates to ProductionEngine.
        Kept for backward compatibility.
        """
        self.production_engine._spawn_ship(planet, design_id, empire, galaxy, save_path)

    def _process_tick(self, tick, empires, galaxy):
        """Process 1 sub-tick of movement and combat.

        PROJ-12 Phase 3: Delegates to specialized engines.

        Five-phase processing:
        Phase 0: Per-turn resource consumption (1/100th of per_turn costs)
        Phase 1: Execute JOIN_FLEET for any co-located fleets (instant, no movement cost)
        Phase 2: Calculate paths/next moves for all fleets (based on current positions)
        Phase 3: Apply all movements simultaneously
        Phase 4: Combat
        """

        # --- Phase 0: Per-turn Resource Consumption ---
        self._process_per_turn_resources(tick, empires)

        # --- Phase 1: Instant Orders (JOIN_FLEET) ---
        # PROJ-12: Delegate to FleetOrderProcessor
        self.order_processor.process_instant_orders(empires)

        # --- Phase 2: Calculate Moves ---
        # PROJ-12: Delegate to FleetMovementEngine
        move_queue = self.movement_engine.collect_movements(empires, galaxy, tick)

        # --- Phase 3: Apply Moves ---
        # PROJ-12: Delegate to FleetMovementEngine
        self.movement_engine.apply_movements(move_queue, galaxy)

        # --- Phase 4: Combat ---
        self._resolve_conflicts(empires)

    def _calculate_next_hex(self, fleet, galaxy):
        """Calculate (but don't apply) the next hex for a fleet.

        PROJ-12 Phase 3: Delegates to FleetMovementEngine.
        Kept for backward compatibility.

        Returns the next hex to move to, or None if no movement.
        Side effect: Updates fleet.path if needed.
        """
        return self.movement_engine.calculate_next_hex(fleet, galaxy)

    def _execute_move_step(self, fleet, galaxy):
        """Advance fleet 1 hex if it has a MOVE order and path.
        
        .. deprecated::
            This method exists for backward compatibility with tests.
            Use _calculate_next_hex directly in new code.
            In the main turn loop, _calculate_next_hex is called in Phase 1,
            and movement is applied in Phase 2.
        """
        import warnings
        warnings.warn(
            "_execute_move_step is deprecated. Use _calculate_next_hex and apply movement manually.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Use the canonical calculation method
        next_hex = self._calculate_next_hex(fleet, galaxy)
        
        if next_hex:
            # Apply the movement
            fleet.location = next_hex
            
            # If path complete, order is done
            if not fleet.path:
                fleet.pop_order()

    def _process_per_turn_resources(self, tick: int, empires) -> None:
        """
        Process per-turn resource consumption (1/100th per tick).

        Components with ResourceConsumption abilities using trigger='per_turn'
        consume resources spread across all 100 ticks of a turn.

        If a ship runs out of a required resource, the component that needs
        it is automatically disabled.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
        """
        for empire in empires:
            for fleet in empire.fleets:
                for ship in fleet.get_ship_instances():
                    if not ship.is_combat_capable():
                        continue

                    per_turn_costs = ship.get_all_resource_costs_per_turn()
                    for resource_type, total_cost in per_turn_costs.items():
                        if total_cost <= 0:
                            continue

                        # Consume 1/100th of the per-turn cost each tick
                        tick_cost = total_cost / 100.0
                        if not ship.consume_resource(resource_type, tick_cost):
                            # Resource depleted - auto-disable components that need it
                            self._auto_disable_components_for_resource(ship, resource_type)

    def _auto_disable_components_for_resource(self, ship, resource_type: str) -> None:
        """
        Auto-disable components that require a depleted resource.

        Finds all components with per_turn ResourceConsumption for the specified
        resource type and disables them.

        Args:
            ship: ShipInstance with the resource shortage
            resource_type: The depleted resource type
        """
        from game.core.registry import get_component_registry
        from game.strategy.services.ship_stats_service import ShipStatsService

        registry = get_component_registry()
        layers = ship.design_data.get('layers', {})

        for layer_name, components in layers.items():
            if isinstance(components, list):
                comp_list = components
            elif isinstance(components, dict):
                comp_list = components.get('components', [])
            else:
                continue

            for comp_entry in comp_list:
                comp_id = comp_entry.get('id', '') if isinstance(comp_entry, dict) else comp_entry
                comp_def = registry.get(comp_id)
                if comp_def is None:
                    continue

                abilities = getattr(comp_def, 'abilities', {}) or {}
                for ability_data in ShipStatsService._get_ability_list(abilities, 'ResourceConsumption'):
                    if (ability_data.get('trigger') == 'per_turn' and
                        ability_data.get('resource') == resource_type):
                        ship.set_component_enabled(comp_id, False)
                        log_info(f"Ship {ship.name}: Auto-disabled {comp_id} - insufficient {resource_type}")

    def _resolve_conflicts(self, empires):
        """Check for collisions and resolve battles."""
        # Map: Hex -> List[(Empire, Fleet)]
        hex_map = {}
        
        all_fleets = []
        for emp in empires:
            for f in emp.fleets:
                if f.location not in hex_map:
                    hex_map[f.location] = []
                hex_map[f.location].append((emp, f))
                
        # Check collisions
        for loc, occupants in hex_map.items():
            if len(occupants) < 2:
                continue
                
            # Check if multiple EMPIRES present
            occupied_empires = set(emp.id for emp, f in occupants)
            if len(occupied_empires) > 1:
                # CONFLICT!
                self._resolve_combat_at_hex(occupants)

    def _resolve_combat_at_hex(self, occupants):
        """Simple RNG resolution. Last standing empire wins."""
        # occupants: List[(Empire, Fleet)]
        
        # Group by Empire
        fleets_by_emp = {}
        for emp, f in occupants:
            if emp.id not in fleets_by_emp:
                fleets_by_emp[emp.id] = []
            fleets_by_emp[emp.id].append(f)
            
        # While > 1 empire has ships
        while len(fleets_by_emp) > 1:
            emp_ids = list(fleets_by_emp.keys())
            
            # Pick two random opposing fleets
            id1, id2 = random.sample(emp_ids, 2)
            f1 = fleets_by_emp[id1][0]
            f2 = fleets_by_emp[id2][0]
            
            # Roll
            survivor = self._resolve_combat(f1, f2)
            
            loser = f2 if survivor == f1 else f1
            loser_owner_id = loser.owner_id
            
            # Remove loser
            # 1. From list
            fleets_by_emp[loser_owner_id].remove(loser)
            if not fleets_by_emp[loser_owner_id]:
                del fleets_by_emp[loser_owner_id]
                
            # 2. From Empire (Global State)
            # We need reference to Empire object.
            # occupants has (Empire, Fleet). Find empire for loser.
            start_tuple = next(t for t in occupants if t[1] == loser)
            loser_empire = start_tuple[0]
            loser_empire.remove_fleet(loser)

    def _resolve_combat(self, f1: Fleet, f2: Fleet) -> Fleet:
        """
        Return the winner of single encounter.

        If both fleets have ShipInstance objects, uses the full battle
        simulation via BattleController. Otherwise falls back to RNG.
        """
        # Check if both fleets have proper ship instances for simulation
        if f1.has_ship_instances() and f2.has_ship_instances():
            return self._resolve_combat_simulated(f1, f2)

        # Fallback to simple RNG for legacy string-based ships
        log_debug(f"Using RNG combat resolution (no ShipInstances)")
        if random.random() > 0.5:
            return f1
        return f2

    def _resolve_combat_simulated(self, f1: Fleet, f2: Fleet) -> Fleet:
        """
        Resolve combat using the injected battle resolver.

        PROJ-11 Phase 4: Uses IBattleResolver interface for clean
        separation between strategy and simulation layers.

        Args:
            f1: First fleet (team 0)
            f2: Second fleet (team 1)

        Returns:
            The winning fleet
        """
        # Use the injected battle resolver
        seed = self._generate_battle_seed()
        result = self._battle_resolver.resolve_battle(f1, f2, seed=seed)

        # Apply results to fleets
        f1.update_from_battle_results(result.team0_survivors)
        f2.update_from_battle_results(result.team1_survivors)

        # Determine winner
        if result.winner == 0:
            return f1
        elif result.winner == 1:
            return f2
        else:
            # Draw - return fleet with more survivors
            return f1 if len(result.team0_survivors) >= len(result.team1_survivors) else f2

    def _apply_battle_results(
        self,
        f1: Fleet,
        f2: Fleet,
        results: 'BattleResults'
    ) -> None:
        """
        Apply battle results back to the source fleets.

        Updates ship damage/resource states and removes destroyed ships.
        """
        # Get surviving ships by team
        team0_survivors = [s for s in results.surviving_ships if s.team_id == 0]
        team1_survivors = [s for s in results.surviving_ships if s.team_id == 1]

        # Convert ShipState back to Ship for update_from_battle_results
        team0_ships = [s.to_ship() for s in team0_survivors]
        team1_ships = [s.to_ship() for s in team1_survivors]

        # Update fleets
        f1.update_from_battle_results(team0_ships)
        f2.update_from_battle_results(team1_ships)

        # Log results
        f1_destroyed = len(f1.get_ship_instances()) - len([
            s for s in f1.ships
            if hasattr(s, 'is_destroyed') and not s.is_destroyed
        ])
        f2_destroyed = len(f2.get_ship_instances()) - len([
            s for s in f2.ships
            if hasattr(s, 'is_destroyed') and not s.is_destroyed
        ])

        log_info(f"Battle results applied: Fleet {f1.id} lost {f1_destroyed} ships, "
                f"Fleet {f2.id} lost {f2_destroyed} ships")

    def _process_end_turn_orders(self, fleet, empire, galaxy):
        """Process static orders like COLONIZE.

        PROJ-12 Phase 3: Delegates to FleetOrderProcessor.

        Returns:
            True if fleet was consumed/deleted by the order, False otherwise.
        """
        return self.order_processor.process_end_turn_orders(fleet, empire, galaxy)

