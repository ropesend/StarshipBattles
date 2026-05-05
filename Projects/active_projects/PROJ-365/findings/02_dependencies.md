# PROJ-355 Dependency Map

## 1. TurnEngine.process_turn() callers
**Production:** `game/strategy/engine/game_session.py:226` (game loop).

**Integration tests (~24 calls):**
- `tests/integration/colonization/test_edge_cases.py:71, 124, 143, 157, 193`
- `tests/integration/gameplay_loop/test_commands_colonization.py` (6 sites)
- `tests/integration/gameplay_loop/test_fleet_operations.py` (7 sites)
- `tests/integration/gameplay_loop/test_turn_execution.py` (7 sites)
- `tests/integration/save_load/*` (~15 sites across 5 files)

## 2. create_default_turn_engine() callers
- `game/strategy/engine/turn_engine.py:813` (docstring example)
- `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py:198, 208, 232, 246`
- `tests/unit/strategy/turn_engine/test_dependency_injection.py:351, 364`

## 3. TurnEngineConfig importers (PROJ-259)
- `game/strategy/engine/turn_engine.py:75, 181`
- `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py:220`
- `tests/unit/strategy/turn_engine/test_turn_engine_init_precedence.py:18`
- `tests/unit/strategy/engine/test_turn_engine_config.py:7`

## 4. Engine interfaces consumed (all in `game/strategy/interfaces/engines.py`)
- `IMovementEngine` (line 48)
- `IProductionEngine` (line 124)
- `IOrderProcessor` (line 168)
- `IConflictEngine` (line 233)
- `IConsumableEngine` (line 283)
- `IPopulationEngine` (line 415)
- `IResupplyEngine` (line 316)
- `IHarvestingEngine` (line 372)
- `IActionExecutionEngine` (line 448)
- `IEnvironmentalHazardEngine` (line 494)
- `IPlanetEnergyEngine` (line 535)
- `IPlanetActionEngine` (line 569)
- `IComponentActivationEngine` (line 690)
- `IOrganicsConsumptionEngine` (line 607)
- `IHappinessEngine` (line 654)

## 5. Tests mocking individual engines
- `tests/unit/strategy/mocks/mock_engines.py` — mock implementations of every IXxx interface.
- `tests/unit/strategy/turn_engine/test_dependency_injection.py:170-351` — 15+ injection tests.
- `tests/unit/strategy/turn_engine/test_turn_processing.py` — phase-ordering tests (will need migration to descriptor model).
- `tests/integration/strategy/turn_engine/test_harvesting.py` — phase-specific.

## 6. PlanetModifierEffectEngine lazy import (line 751)
```python
from game.strategy.engine.planet_modifier_effect_engine import PlanetModifierEffectEngine
PlanetModifierEffectEngine(registries=self._registries).process_modifier_effects_tick(tick, empires)
```
**Why lazy:** historical/coupling reasons — instantiated per tick, stateless, no per-turn accumulation. **Hoist-safe** when migrating to descriptors: this becomes a pre-built engine reference in the descriptor list.

## 7. _time_phase usage
22 call sites, all inside `_process_tick` (lines 571-778). **No external usage** — safe to refactor for descriptor-driven dispatch.

## 8. last_environmental_events accumulation
- Init: `turn_engine.py:220`
- Reset: line 513 (each `process_turn`)
- Write: line 729 (`extend(env_events)`)
- **External consumer: NONE.** Tests only inspect; no UI consumes. Likely orphan PROJ-189 infrastructure. PROJ-355 should preserve it as-is (deletion is out of scope).

## 9. Save/load per-phase state
- No `__getstate__` / `__setstate__` on TurnEngine.
- `_phase_times` dict resets each `process_turn`.
- TurnStateSnapshot (lines 527-531) handles pre-turn rollback safety, not phase-internal state.
**TurnEngine instance state is ephemeral.** Descriptor refactor does NOT affect save/load.
