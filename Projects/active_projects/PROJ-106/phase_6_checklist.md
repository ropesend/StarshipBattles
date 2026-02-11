# Phase 6: BattleUIService Contract Hardening and GameRenderer Decoupling

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Reduce fragile getattr() chains in BattleUIService by defining explicit Ship interface attributes, and decouple game_renderer.py from simulation-layer enums by using pre-calculated values.

---

## Context

### ADR-UI2-002: Excessive getattr() in BattleUIService
`game/ui/services/battle_ui_service.py:132-195` has 20+ `getattr()` calls with fallback defaults when converting Ship to ShipDTO. This indicates the Ship object's interface is not well-defined from the UI's perspective.

**Root cause analysis:** Most of these getattr() calls are for properties that Ship DOES have, but BattleUIService is being overly defensive. After examining ship.py, these properties exist:
- `is_derelict`, `current_shields`, `max_shields`, `current_speed`, `total_thrust`, `turn_speed` -- all are real Ship properties
- `total_shots_fired`, `crew_onboard`, `crew_required`, `max_targets`, `ai_strategy`, `source_file` -- also real properties

The getattr() pattern was likely a safety measure during early development. Now that Ship's interface is stable, we can replace most getattr() calls with direct attribute access.

### ADR-UI2-004: GameRenderer Coupling to Simulation Enums
`game/ui/renderer/game_renderer.py` imports `LayerType` and `LayerDefaults` from `game.core.constants`. This is actually a **core** import, not a simulation import. The code comment "Cross-layer imports (acceptable for rendering)" at line 4-6 already acknowledges this.

**Revised assessment:** LayerType and LayerDefaults are in `game.core.constants` (canonical location). The import on line 9 is `from game.core.constants import LayerType, LayerDefaults, ResourceType`. This is a core-to-UI dependency, which is architecturally correct (UI can depend on Core).

The real issue is the hardcoded radius percentages on lines 93-96 (0.1, 0.35, 0.65, 0.9) which duplicate values that should come from LayerDefaults. This is a code quality issue, not an architecture violation.

---

## Tasks

### Task 6.1: Replace Defensive getattr() with Direct Access in BattleUIService [Medium]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/interfaces/test_battle_ui.py -v`

- [ ] Review each getattr() call in `_convert_ship()` (lines 152-195)
- [ ] For Ship properties that are guaranteed to exist (defined in `__init__`), replace `getattr(ship, 'prop', default)` with `ship.prop`
- [ ] Known safe direct access (defined in Ship.__init__):
  - `ship.is_derelict` (has `@property`, defaults to checking hp)
  - `ship.current_shields` (computed property on Ship)
  - `ship.max_shields` (computed property on Ship)
  - `ship.current_speed` (PhysicsBody property)
  - `ship.max_speed` (cached property)
  - `ship.mass` (cached property)
  - `ship.total_thrust` (cached property)
  - `ship.turn_speed` (cached property)
  - `ship.total_shots_fired` (initialized in Ship.__init__)
  - `ship.crew_onboard` (initialized in Ship.__init__)
  - `ship.crew_required` (cached stat)
  - `ship.max_targets` (initialized with CombatConstants.DEFAULT_MAX_TARGETS)
  - `ship.ai_strategy` (initialized in Ship.__init__)
  - `ship.source_file` (set during loading)
- [ ] Keep getattr() ONLY for properties that might genuinely be missing (e.g., `source_file` which is set externally)
- [ ] Also replace `heading = getattr(ship, 'heading', None)` pattern (lines 166-168) -- Ship uses `angle` not `heading`, so use `ship.angle` directly
- [ ] Run tests: `pytest tests/unit/ui/interfaces/test_battle_ui.py -v`

---

### Task 6.2: Replace Hardcoded Radius Values in game_renderer.py [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** `pytest tests/ -v -k renderer`

- [ ] Lines 93-96: Replace hardcoded radius percentages with LayerDefaults constants
- [ ] Current: `0.1` (CORE), `0.35` (INNER), `0.65` (OUTER), `0.9` (ARMOR)
- [ ] Replace with: `LayerDefaults.CORE_RADIUS_PCT`, `LayerDefaults.INNER_RADIUS_PCT`, `LayerDefaults.OUTER_RADIUS_PCT`, and `0.9` for ARMOR (check if LayerDefaults has ARMOR_RADIUS_PCT)
- [ ] Note: Lines 84-87 already use `LayerDefaults.OUTER_RADIUS_PCT` etc. correctly -- this fix makes lines 93-96 consistent
- [ ] Run tests: `pytest tests/ -v -k renderer`

---

### Task 6.3: Remove Redundant pygame.math.Vector2 Usage in game_renderer.py [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** `pytest tests/ -v -k renderer`

- [ ] Line 112: `comp_world_pos = ship.position + pygame.math.Vector2(off_x, off_y)` -- check if this can use `game.core.math.Vector2` instead
- [ ] Note: This is in the UI layer where pygame is acceptable, but consistency is preferred
- [ ] If ship.position is already a pygame.math.Vector2 from physics layer, then this is fine as-is
- [ ] Decision: LOW PRIORITY. Only change if it causes no issues. Mark as optional.
- [ ] Run tests: `pytest tests/ -v -k renderer`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] BattleUIService getattr() count reduced from 20+ to only genuinely uncertain properties
- [ ] game_renderer.py uses LayerDefaults constants instead of magic numbers
- [ ] Full test suite passes: `pytest tests/ -n 12` (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
