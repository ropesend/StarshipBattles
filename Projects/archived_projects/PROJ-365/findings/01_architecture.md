# PROJ-355 Architecture Analysis

## 1. Tick-phase-registry documentation
**No** — `docs/systems/strategy_layer.md` describes phases 0-4 prescriptively but does not define a phase-registry pattern. PROJ-355 is greenfield design.

## 2. Phases table

| Phase | Engine | Method | Args | Special State |
|-------|--------|--------|------|---|
| 0a (harvesting) | HarvestingEngine | `process_harvesting_tick` | tick, empires, galaxy | — |
| 0b (resources) | ConsumableManagementEngine | `process_per_turn_consumption` | tick, empires | — |
| 0c (fuel_gen) | ResupplyEngine | `process_fuel_generation` | tick, empires | — |
| 0c1 (planet_energy) | PlanetEnergyEngine | `process_energy_tick` | tick, empires | — |
| 0d (resupply) | ResupplyEngine | `process_fleet_resupply` | tick, empires, galaxy | — |
| 0e (production) | ProductionEngine | `process_construction_tick` | tick, empires, galaxy, save_path | — |
| 0f (environmental) | EnvironmentalHazardEngine | `process_environmental_tick` | tick, empires, galaxy | Returns event list |
| 1 (instant_orders) | OrderProcessor | `process_instant_orders` | empires | — |
| 1.5 (actions) | ActionExecutionEngine | `process_action_ticks` | empires, galaxy, tick, component_registry, all_empires | — |
| 1.6 (planet_actions) | PlanetActionEngine | `process_planet_actions_tick` | tick, empires, component_registry | — |
| 1.7 (activation_timers) | ComponentActivationEngine | `process_activation_tick` | tick, empires | — |
| 1.8 (planet_modifier_effects) | PlanetModifierEffectEngine | `process_modifier_effects_tick` | tick, empires | Locally constructed (line 751) |
| 2 (movement_calc) | FleetMovementEngine | `collect_movements` | empires, galaxy, tick | Returns move_queue |
| 3 (movement_apply) | FleetMovementEngine | `apply_movements` | move_queue, galaxy | **Pre-state snapshot** (line 762) |
| 4 (combat) | ConflictResolutionEngine | `resolve_all_conflicts` | empires, galaxy, tick, moved_fleet_ids | **Derived from 2→3 diff** |

Source: `turn_engine.py:703-782`.

## 3. Cross-phase state — recommendation: TickContext object
Phase 3 mutates fleet locations; phase 4 needs a pre/post diff for `moved_fleet_ids` (PROJ-320, line 762-775).

**Proposed:**
```python
@dataclass
class TickContext:
    tick: int
    empires: list
    galaxy: object
    pre_movement_locations: dict[int, HexCoord] | None = None
    moved_fleet_ids: set[int] | None = None
```
A barrier-phase approach would create hard ordering dependencies; a context object decouples via data-passing and is easier to mock and extend.

## 4. Proposed `TickPhase` dataclass
```python
@dataclass(frozen=True)
class TickPhase:
    phase_key: str                              # Identity / timing bucket
    callable_target: Callable                   # Engine method to invoke
    args_resolver: Callable[[TickContext], tuple]  # Maps context to positional args
    error_policy: str = 'wrap'                  # 'wrap' | 'barrier'
    tick_gating: str | None = None              # 'only_tick_1' | None
    timing_bucket: str | None = None            # Defaults to phase_key
    post_exec_hook: Callable[[TickContext, Any], None] | None = None
```
**Rationale:** `args_resolver` decouples descriptors from a fixed call signature; `tick_gating` replaces inline `if tick == 1`; `post_exec_hook` absorbs the mid-phase `_log_empire_state` calls at lines 705 and 723-724.

## 5. Phase list location
**New module:** `game/strategy/engine/turn_phase_registry.py` exporting `DEFAULT_TICK_PHASE_LIST`.

Test override ergonomics:
```python
@pytest.fixture
def reordered_phases():
    phases = list(DEFAULT_TICK_PHASE_LIST)
    phases[2], phases[3] = phases[3], phases[2]
    return phases
```
TurnEngine accepts an optional `tick_phases=` kwarg.

## 6. TurnEngineConfig vs new module
**Decision:** new module. PROJ-259's `TurnEngineConfig` bundles engine *instances* (DI). PROJ-355's TickPhase descriptors are phase *metadata* (sequencing). Mixing the two violates SRP and would make TurnEngineConfig dual-purpose. They stay orthogonal.

## 7. Risks

- **Phase-order-pinning tests:** `test_turn_engine_phase_320_movement_diff.py` and `test_turn_processing.py` use `mock.call_args_list` / `call_order` to assert sequence. Must update to use the descriptor list, not internal calls.
- **Mid-phase logging at lines 705/724:** convert to `post_exec_hook` on the relevant descriptors with `tick_gating='only_tick_1'`.
- **End-of-turn engines (lines 571-602)** — outside the tick loop, also use `_time_phase`. PROJ-355 explicitly excludes them from the descriptor refactor; they keep their imperative form for now.
