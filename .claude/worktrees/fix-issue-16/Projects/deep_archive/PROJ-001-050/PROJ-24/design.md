# PROJ-24: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source
- **Origin:** LPA-01 finding from PROJ-22 review (2026-01-27_general_legacy-cleanup-verification)
- **Issue:** ShipControllableAdapter uses `__getattr__`/`__setattr__` delegation for backward compatibility
- **Location:** `game/ai/interfaces/controllable.py:162-308`

## Initial Analysis

### Current IControllable Interface (18 methods)
The interface in `game/ai/interfaces/controllable.py` defines:

**Position/Movement (Read) - 6 methods:**
- `get_position()`, `get_velocity()`, `get_rotation()`, `get_radius()`, `get_max_speed()`, `get_current_speed()`

**Movement Controls (Write) - 4 methods:**
- `set_throttle()`, `set_turn_throttle()`, `rotate()`, `thrust_forward()`

**Identity/State - 2 methods:**
- `get_team_id()`, `is_alive()`

**Combat - 5 methods:**
- `get_weapon_range()`, `set_trigger_pulled()`, `get_current_target()`, `set_current_target()`, `get_max_targets()`

**Formation - 4 methods:**
- `get_formation_members()`, `get_formation_master()`, `is_in_formation()`, `get_formation_offset()`

### Missing Methods Required (~11)
- `get_turn_speed()` - Turn rate calculations
- `get_acceleration_rate()` - Formation drift threshold
- `get_is_thrusting()` - Formation velocity sync
- `set_rotation(angle)` - FormationBehavior angle snapping
- `set_in_formation(value)` - Formation state management
- `set_formation_master(master)` - Formation state management
- `get_secondary_targets()` / `set_secondary_targets()` - Multiplex targeting
- `get_components_by_ability(name, op)` - Formation integrity check
- `adjust_position(delta)` - Formation position correction
- `get_layers()` - Component inspection in core/system.py

## Swarm Findings Summary

### Architecture Analysis
Two parallel AIController implementations exist and are BOTH in active production use:

| Implementation | Files | Used By |
|---------------|-------|---------|
| Simulation Layer | `controller.py` + `behaviors.py` | `battle_engine.py`, `battle_orchestrator.py` |
| UI Layer | `core/system.py` + `core/behaviors.py` | `battle.py`, `setup.py`, `panels.py`, builder |

**Key Differences:**
- Query radius: BattleConfig vs hardcoded 200000
- Throttle defaults: AIConfig vs hardcoded 0.9
- Avoidance radius: BattleConfig vs hardcoded 1000

### Key Patterns to Reuse
- **Protocol Pattern**: `game/core/protocols.py` - Uses `@runtime_checkable` with TypeGuard
- **ABC Pattern**: `game/ai/interfaces/controllable.py` - Uses `@abstractmethod`
- **Deprecation Pattern**: `game/strategy/engine/game_session.py:66-81` - warnings.warn with stacklevel=2

### Dependencies & Risks

1. **FormationBehavior (HIGH RISK)**
   - Direct position mutation: `ship.position += correction`
   - Direct angle setting: `ship.angle = master.angle`
   - Complex state management across master/members
   - **Mitigation:** Use new `adjust_position()` and `set_rotation()` methods

2. **Reference vs Copy Semantics (MEDIUM)**
   - `get_position()` must return reference, not copy
   - Code relies on position object identity
   - **Mitigation:** Verify Vector2 handling in adapter

3. **Master Access Pattern**
   - `formation_master` returns raw Ship, not adapter
   - Code chains: `ship.formation_master.current_target`
   - **Mitigation:** Document this is intentional; master accesses raw Ship

4. **Component Access Abstraction Leak**
   - `get_components_by_ability()` exposes component internals
   - AI knows about HP, operational status
   - **Mitigation:** Accept for now; refactor to capability methods in future

### Test Impact

**Critical tests to update:**
- `tests/unit/ai/test_controllable_interface.py` - Add tests for new methods
- `tests/unit/ai/test_ai_controller_interface.py` - Verify interface usage

**Test strategy:**
- Run full suite after each file migration
- Add deprecation warnings to `__getattr__` to catch missed accesses
- Verify formation behavior with dedicated formation tests

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## Direct Access Inventory

### controller.py (~48 accesses)
- `self.ship.position` - 10 occurrences
- `self.ship.turn_throttle` - 4 occurrences
- `self.ship.engine_throttle` - 5 occurrences
- `self.ship.formation_members` - 3 occurrences
- `self.ship.in_formation` - 5 occurrences
- `self.ship.formation_master` - 5 occurrences
- `self.ship.current_target` - 5 occurrences
- `self.ship.is_alive` - 1 occurrence
- `self.ship.comp_trigger_pulled` - 2 occurrences
- `self.ship.radius` - 2 occurrences
- `self.ship.turn_speed` - 1 occurrence
- `self.ship.angle` - 2 occurrences
- `self.ship.max_targets` - 2 occurrences
- `self.ship.secondary_targets` - 2 occurrences
- `self.ship.get_components_by_ability()` - 2 occurrences

### behaviors.py (~35 accesses)
- `ship.position` - 8 occurrences
- `ship.comp_trigger_pulled` - 3 occurrences
- `ship.max_weapon_range` - 4 occurrences
- `ship.thrust_forward()` - 4 occurrences (already interface)
- `ship.rotate()` - 4 occurrences (already interface)
- `ship.angle` - 3 occurrences
- `ship.in_formation` - 2 occurrences
- `ship.formation_offset` - 4 occurrences
- `ship.radius` - 1 occurrence
- `ship.acceleration_rate` - 1 occurrence
- `ship.max_speed` - 1 occurrence
- `ship.engine_throttle` - 2 occurrences
- `ship.turn_throttle` - 1 occurrence
- `ship.turn_speed` - 1 occurrence

### core/system.py (~58 accesses)
Similar patterns to controller.py, plus:
- `self.ship.layers` - 3 occurrences

### core/behaviors.py (~22 accesses)
Similar patterns to behaviors.py
