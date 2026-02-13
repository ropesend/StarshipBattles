# Phase 6: BattleUIService Contract Hardening and GameRenderer Decoupling

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Review each getattr() call in `_convert_ship()` (lines 152-195)
- [x] For Ship properties that are guaranteed to exist (defined in `__init__`), replace `getattr(ship, 'prop', default)` with `ship.prop`
- [x] Known safe direct access (defined in Ship.__init__):
  - `ship.is_derelict` (has `@property`, defaults to checking hp)
  - `ship.current_shields` (computed property on Ship)
  - `ship.max_shields` (computed property on Ship)
  - `ship.current_speed` (PhysicsBody property)
  - `ship.max_speed` (cached property)
  - `ship.mass` (cached property)
  - `ship.total_thrust` (cached property)
  - `ship.turn_speed` (cached property)
  - `ship.total_shots_fired` (initialized in Ship.__init__)
  - `ship.crew_onboard` - KEEP getattr (dynamically set by ShipStatsCalculator, not in __init__)
  - `ship.crew_required` - KEEP getattr (dynamically set by ShipStatsCalculator, not in __init__)
  - `ship.max_targets` (initialized with CombatConstants.DEFAULT_MAX_TARGETS)
  - `ship.ai_strategy` (initialized in Ship.__init__)
  - `ship.source_file` (set during loading)
- [x] Keep getattr() ONLY for properties that might genuinely be missing (crew_onboard, crew_required, ship.id)
- [x] Also replace `heading = getattr(ship, 'heading', None)` pattern -- Ship uses `angle` from PhysicsBody, use `ship.angle` directly
- [x] Run tests: `pytest tests/unit/ui/interfaces/test_battle_ui.py -v` - 15 passed
- [x] Updated obsolete defensive fallback tests in test_state_and_integration.py

---

### Task 6.2: Replace Hardcoded Radius Values in game_renderer.py [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** `pytest tests/ -v -k renderer`

- [x] Lines 93-96: Replace hardcoded radius percentages with LayerDefaults-derived values
- [x] Understood: hardcoded values (0.1, 0.35, 0.65, 0.9) were for component DOT positions (center of each layer), not layer boundaries
- [x] Replaced with derived formulas: (boundary_inner + boundary_outer) / 2 for each layer
- [x] Now uses LayerDefaults constants consistently for both boundary circles AND component positions
- [x] Run tests: `pytest tests/ -v -k renderer` - 32 passed

---

### Task 6.3: Remove Redundant pygame.math.Vector2 Usage in game_renderer.py [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** `pytest tests/ -v -k renderer`

- [x] Line 112: `comp_world_pos = ship.position + pygame.math.Vector2(off_x, off_y)` -- reviewed
- [x] Decision: SKIPPED (optional). pygame.math.Vector2 is acceptable in UI layer, ship.position is pygame.math.Vector2 from PhysicsBody
- [x] No change needed - using pygame Vector2 in UI layer is architecturally correct

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] BattleUIService getattr() count reduced from 20+ to 3 (crew_onboard, crew_required, ship.id)
- [x] game_renderer.py uses LayerDefaults-derived constants instead of magic numbers
- [x] Full test suite passes: `pytest tests/ -n 12` - 8185 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
