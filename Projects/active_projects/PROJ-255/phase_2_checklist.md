# Phase 2: Type Hints on Critical Paths

**Objective:** Add full parameter and return type annotations to constructors and hot-path methods in the 4 most critical files.

**Key Principle:** Annotations are non-breaking additions. Target the most coupled and performance-sensitive code first.

---

## Target Files and Methods

### `game/ai/controller.py`
- [ ] `AIController.__init__(self, ship, grid, enemy_team_id)` — add types for all params

### `game/simulation/entities/ship_stats.py`
- [ ] `ShipStatsCalculator.__init__(self, vehicle_classes, *, resource_catalog, planetary_resource_ids)` — add types for all params

### `game/strategy/engine/turn_engine.py`
- [ ] `process_turn(empires, galaxy, save_path, *, session)` — add types for all params and return
- [ ] `_process_tick(self, tick, empires, galaxy, save_path)` — add types for all params and return

### `game/strategy/engine/game_session.py`
- [ ] `GameSession.__init__(self, config, ai_factory)` — add types for `ai_factory`
- [ ] `handle_command(self, command)` — add types for `command` and return

---

## Checklist

### Discovery
- [ ] Read each target method — determine the correct types from usage context
- [ ] Check for existing Protocol/interface definitions that parameters should conform to
- [ ] Identify any `TYPE_CHECKING` imports needed to avoid circular imports

### Implementation
- [ ] Add type annotations to `AIController.__init__`
- [ ] Add type annotations to `ShipStatsCalculator.__init__`
- [ ] Add type annotations to `TurnEngine.process_turn` and `_process_tick`
- [ ] Add type annotations to `GameSession.__init__` and `handle_command`
- [ ] Add any required `TYPE_CHECKING` imports

### Verification
- [ ] Run full test suite (`python scripts/test_sharded.py`) — no regressions
- [ ] Run `python -c "from game.ai.controller import AIController"` — no import errors
- [ ] Run `python -c "from game.simulation.entities.ship_stats import ShipStatsCalculator"` — no import errors
- [ ] Run `python -c "from game.strategy.engine.turn_engine import TurnEngine"` — no import errors
- [ ] Run `python -c "from game.strategy.engine.game_session import GameSession"` — no import errors
