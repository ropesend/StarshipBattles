# PROJ-259: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Screen Transitions (Issue #14)
`game/app.py` has 23 `_switch_scene()` calls (plus the definition on line 188). The method is minimal:
```python
def _switch_scene(self, state: GameState, scene: IScene) -> None:
    self.state = state
    self.active_scene = scene
```
No bugs were found. All 23 transitions are valid. The motivation is formalization: an explicit transition table makes it easy to audit which transitions are legal, add guards (e.g., "can only enter STRATEGY from MENU or BATTLE"), and support a state stack for return-to-previous behavior (currently handled by ad-hoc `self.return_state`, `self.builder_return_state`, `self._keybindings_return_state` fields).

**Current transition map (extracted from app.py):**
| From | To | Trigger Method |
|------|----|---------------|
| MENU | BUILDER | `start_builder()` (line 209) |
| MENU | BATTLE_SETUP | `start_battle_setup()` (line 230) |
| MENU | STRATEGY | `_on_new_game_start()` (line 281), `_start_quickstart()` (line 338), `_on_load_game()` (line 386) |
| MENU | FORMATION | `start_formation_editor()` (line 411) |
| MENU | TEST_LAB | `start_test_lab()` (line 420) |
| MENU | RESEARCH_TREE | `start_research_tree()` (line 431) |
| MENU | GALAXY_TEST | `start_galaxy_test()` (line 445) |
| BUILDER | MENU | `on_builder_return()` (line 222) |
| BUILDER | STRATEGY | `on_builder_return()` (line 220) |
| BATTLE | BATTLE_SETUP | `_return_to("battle_setup")` (line 644) |
| BATTLE | TEST_LAB | `_return_to("test_lab")` (line 641) |
| BATTLE | STRATEGY | `_return_to("strategy")` (line 645) |
| BATTLE_SETUP | MENU | `_handle_battle_setup_action("return_to_menu")` (line 747) |
| BATTLE_SETUP | BATTLE | `start_battle()` (line 522) |
| FORMATION | MENU | `on_formation_return()` (line 415) |
| TEST_LAB | MENU | `_handle_test_lab_action("return_to_menu")` (line 701) |
| TEST_LAB | BATTLE | `_handle_test_lab_action("start_test_battle")` (line 703) |
| RESEARCH_TREE | MENU | `on_research_tree_return()` (line 436) |
| GALAXY_TEST | MENU | `on_galaxy_test_return()` (line 450) |
| STRATEGY | BUILDER | `_handle_strategy_action("open_builder")` (line 652) |
| STRATEGY | MENU | `_handle_strategy_action("quit_to_menu")` (line 662) |
| STRATEGY | KEYBINDINGS | `start_keybindings()` (line 463) |
| KEYBINDINGS | STRATEGY | `on_keybindings_return()` (line 474) |
| KEYBINDINGS | MENU | `on_keybindings_return()` (line 476) |

**Return state patterns:**
- `self.builder_return_state`: Set before entering BUILDER, checked on exit (MENU or STRATEGY)
- `self._keybindings_return_state`: Set before entering KEYBINDINGS, checked on exit (MENU or STRATEGY)
- `self.return_state`: Set to BATTLE_SETUP or TEST_LAB, used for battle return routing

### TurnEngine Constructor (Issue #8)
`game/strategy/engine/turn_engine.py` line 132-151: 20 parameters total.
- 1 positional: `battle_resolver` (Optional)
- 1 required keyword: `registries` (GameRegistries)
- 13 optional engine keywords: `movement_engine`, `production_engine`, `order_processor`, `conflict_engine`, `resource_engine`, `population_engine`, `resupply_engine`, `harvesting_engine`, `action_engine`, `environmental_engine`, `planet_energy_engine`, `planet_action_engine`, `component_activation_engine`
- 2 other optional: `ai_factory`, `event_bus`

Factory function `create_default_turn_engine()` exists at line 637 but just calls `TurnEngine(registries=registries, ai_factory=ai_factory)`.

### BattleEngine Tick Loop (Issue #22)
`game/simulation/systems/battle_engine.py` line 406-438: `update()` method has 5 phases already extracted to private methods:
1. `_rebuild_grid()` (line 439) -- rebuild spatial grid, return alive ships
2. `_update_ai_and_ships()` (line 452) -- run AI controllers, ship updates, aura updates
3. `_collect_new_attacks()` (line 466) -- gather attacks from ships
4. `_process_attacks()` (line 475) -- dispatch projectile/beam/launch attacks
5. Inline: `collision_system.process_ramming()` + `projectile_manager.update()` (lines 434-438)

The sequence is stable with no change requests in git history.

---

## Design: Screen State Machine

### ScreenStateMachine Class

Location: `game/core/state_machine.py`

```python
from dataclasses import dataclass
from typing import Callable, Dict, FrozenSet, Generic, Optional, TypeVar

S = TypeVar('S')  # State type (GameState)

TransitionGuard = Callable[[S, S], bool]  # (from_state, to_state) -> allowed

@dataclass(frozen=True)
class TransitionRule:
    """A permitted transition between two states."""
    from_state: S
    to_state: S
    guard: Optional[TransitionGuard] = None  # Optional extra check


class ScreenStateMachine(Generic[S]):
    """
    Explicit state machine for screen transitions.
    
    Features:
    - Transition table: only declared transitions are allowed
    - Guards: optional per-transition callable predicates
    - State stack: push/pop for return-to-previous (replaces ad-hoc return_state fields)
    - on_exit / on_enter hooks: per-state callables for cleanup/setup
    
    Raises StateException on illegal transitions.
    """
    
    def __init__(
        self,
        initial_state: S,
        transitions: FrozenSet[tuple[S, S]],  # Set of (from, to) pairs
        guards: Optional[Dict[tuple[S, S], TransitionGuard]] = None,
        on_enter: Optional[Dict[S, Callable]] = None,
        on_exit: Optional[Dict[S, Callable]] = None,
    ):
        self._state = initial_state
        self._transitions = transitions
        self._guards = guards or {}
        self._on_enter = on_enter or {}
        self._on_exit = on_exit or {}
        self._state_stack: list[S] = []
    
    @property
    def state(self) -> S:
        return self._state
    
    def transition(self, to_state: S) -> None:
        """Transition to a new state. Raises StateException if not allowed."""
        ...
    
    def push_and_transition(self, to_state: S) -> None:
        """Push current state onto stack, then transition."""
        ...
    
    def pop_and_return(self) -> S:
        """Pop previous state from stack and transition back."""
        ...
    
    def can_transition(self, to_state: S) -> bool:
        """Check if transition is allowed without performing it."""
        ...
```

### Transition Table for Starship Battles

The transition set is derived from the 24 transitions documented above. It is declared as a `frozenset` of `(from_state, to_state)` tuples in `game/app.py` and passed to `ScreenStateMachine.__init__()`.

### State Stack Usage

Replace the three ad-hoc return-state fields:
- `self.builder_return_state` -> `state_machine.push_and_transition(BUILDER)`; on return: `state_machine.pop_and_return()`
- `self._keybindings_return_state` -> same pattern
- `self.return_state` for battle routing -> same pattern (push BATTLE_SETUP or TEST_LAB before entering BATTLE)

### Integration with app.py

`Game.__init__()` creates `ScreenStateMachine(initial_state=GameState.MENU, transitions=TRANSITION_TABLE)`.

`_switch_scene()` is replaced by a new method that calls `self.state_machine.transition(state)` then sets `self.active_scene = scene`. The `self.state` property delegates to `self.state_machine.state`.

### Layer Placement

`ScreenStateMachine` goes in `game/core/state_machine.py` because:
- It is a generic infrastructure class with no UI/Pygame dependencies
- It uses the `GameState` enum from `game/core/constants.py`
- It follows the pattern of other core infrastructure (SingletonMeta, ValidationResult)

---

## Design: TurnEngineConfig

### TurnEngineConfig Dataclass

Location: `game/strategy/engine/turn_engine_config.py`

```python
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.interfaces.engines import (
        IMovementEngine, IProductionEngine, IOrderProcessor,
        IConflictEngine, IConsumableEngine, IPopulationEngine,
        IResupplyEngine, IHarvestingEngine, IActionExecutionEngine,
        IEnvironmentalHazardEngine, IPlanetEnergyEngine,
        IPlanetActionEngine, IComponentActivationEngine,
    )


@dataclass(frozen=True)
class TurnEngineConfig:
    """
    Configuration bundle for TurnEngine sub-engines.
    
    All fields default to None, meaning TurnEngine will lazily create
    the default implementation. Provide explicit values for testing
    or custom configurations.
    
    Frozen to prevent mid-turn mutation.
    """
    movement_engine: Optional['IMovementEngine'] = None
    production_engine: Optional['IProductionEngine'] = None
    order_processor: Optional['IOrderProcessor'] = None
    conflict_engine: Optional['IConflictEngine'] = None
    resource_engine: Optional['IConsumableEngine'] = None
    population_engine: Optional['IPopulationEngine'] = None
    resupply_engine: Optional['IResupplyEngine'] = None
    harvesting_engine: Optional['IHarvestingEngine'] = None
    action_engine: Optional['IActionExecutionEngine'] = None
    environmental_engine: Optional['IEnvironmentalHazardEngine'] = None
    planet_energy_engine: Optional['IPlanetEnergyEngine'] = None
    planet_action_engine: Optional['IPlanetActionEngine'] = None
    component_activation_engine: Optional['IComponentActivationEngine'] = None
```

### Refactored TurnEngine Constructor

```python
class TurnEngine:
    def __init__(
        self,
        battle_resolver: Optional['IBattleResolver'] = None,
        *,
        registries: GameRegistries,
        config: Optional[TurnEngineConfig] = None,
        ai_factory: Optional[Any] = None,
        event_bus=None,
    ):
        cfg = config or TurnEngineConfig()
        self._movement_engine = cfg.movement_engine
        self._production_engine = cfg.production_engine
        # ... etc for all 13 engines
```

### Migration Strategy

1. Add `TurnEngineConfig` class and `config` parameter to `TurnEngine.__init__()`
2. Keep old individual kwargs temporarily, with deprecation
3. Update all callers (production code uses `create_default_turn_engine()`, tests use constructor directly)
4. Remove old individual kwargs once all callers are migrated
5. Update `create_default_turn_engine()` to accept optional `TurnEngineConfig`

### Factory Function Update

```python
def create_default_turn_engine(
    registries: GameRegistries,
    ai_factory=None,
    config: Optional[TurnEngineConfig] = None,
) -> TurnEngine:
    return TurnEngine(
        registries=registries,
        ai_factory=ai_factory,
        config=config,
    )
```

---

## Design: Battle Engine Tick Phases

### ITickPhase Protocol

Location: `game/simulation/systems/tick_phase.py`

Follows the `IEndCondition` pattern from `battle_end_conditions.py` -- protocol-based, with concrete implementations.

```python
from typing import Any, Dict, List, Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.systems.battle_engine import BattleEngine


@runtime_checkable
class ITickPhase(Protocol):
    """Protocol for a single phase within a battle engine tick."""
    
    @property
    def name(self) -> str:
        """Unique phase name for logging and debugging."""
        ...
    
    @property
    def priority(self) -> int:
        """Execution order. Lower numbers run first."""
        ...
    
    def execute(self, engine: 'BattleEngine') -> None:
        """Execute this phase for the current tick."""
        ...


class TickPhaseRegistry:
    """Ordered registry of tick phases.
    
    Phases are registered with a priority and executed in priority order
    during each tick. The default registration preserves the current
    BattleEngine.update() sequence.
    """
    
    def __init__(self):
        self._phases: List[ITickPhase] = []
    
    def register(self, phase: ITickPhase) -> None:
        """Add a phase and re-sort by priority."""
        ...
    
    def execute_all(self, engine: 'BattleEngine') -> None:
        """Execute all registered phases in priority order."""
        ...
    
    @property
    def phases(self) -> List[ITickPhase]:
        """Return phases in execution order (sorted by priority)."""
        ...
```

### Default Phase Implementations

Five concrete phases matching the current `update()` body:

| Priority | Phase Class | Current Method | Lines |
|----------|-------------|----------------|-------|
| 100 | `RebuildGridPhase` | `_rebuild_grid()` | 439-450 |
| 200 | `AIAndShipUpdatePhase` | `_update_ai_and_ships()` | 452-464 |
| 300 | `AttackProcessingPhase` | `_collect_new_attacks()` + `_process_attacks()` | 466-487 |
| 400 | `RammingPhase` | `collision_system.process_ramming()` | 434 |
| 500 | `ProjectileUpdatePhase` | `projectile_manager.update()` | 438 |

Priority spacing of 100 allows inserting custom phases between defaults.

### Integration with BattleEngine

```python
class BattleEngine:
    def __init__(self, ...):
        ...
        self._tick_phases = self._create_default_phases()
    
    def _create_default_phases(self) -> TickPhaseRegistry:
        registry = TickPhaseRegistry()
        registry.register(RebuildGridPhase())
        registry.register(AIAndShipUpdatePhase())
        registry.register(AttackProcessingPhase())
        registry.register(RammingPhase())
        registry.register(ProjectileUpdatePhase())
        return registry
    
    def update(self) -> None:
        if self.is_battle_over():
            return
        self.tick_counter += 1
        self.recent_beams = []
        self._tick_phases.execute_all(self)
```

Each phase class calls the existing private methods on the engine instance, so existing behavior is preserved exactly. The private methods remain on `BattleEngine` as implementation detail -- phases are thin wrappers that delegate to them.

### Phase Access to Engine State

Phase `execute(engine)` receives the `BattleEngine` instance, giving access to:
- `engine.ships`, `engine.ai_controllers`, `engine.grid`
- `engine.projectile_manager`, `engine.collision_system`
- `engine.recent_beams`, `engine.logger`
- Private methods: `engine._rebuild_grid()`, `engine._update_ai_and_ships()`, etc.

This is intentional -- phases are internal to the simulation layer and are not cross-layer. The `BattleEngine` is the execution context.

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Key Patterns Reused
- **Protocol + TypeGuard** (`game/core/protocols.py`): Used for `ITickPhase`
- **IEndCondition** (`game/simulation/systems/battle_end_conditions.py`): Pattern model for `ITickPhase` (protocol + concrete classes + registry)
- **Frozen dataclass** (`GameRegistries`): Pattern model for `TurnEngineConfig`
- **Strategy engine interfaces** (`game/strategy/interfaces/engines.py`): Type references for `TurnEngineConfig` fields

### Dependencies and Risks
1. **PROJ-258 dependency**: ApplicationContext must exist before this project starts. If PROJ-258 is delayed, Phase 1 (state machine) can start independently since it does not require ApplicationContext.
2. **Test fixture updates**: `tests/unit/strategy/turn_engine/conftest.py` creates `TurnEngine` with individual kwargs. Must be updated for `TurnEngineConfig`.
3. **No behavior changes**: All three refactors are structural only. If any test fails after refactoring, it indicates a bug in the refactor, not a deliberate behavior change.
