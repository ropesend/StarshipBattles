# Phase 4: Task 3.20 second bullet investigation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-491 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Determine whether PROJ-479 Phase 3 Task 3.20 second bullet (`_per_player_ui_state.load(...)` private-attr access at lines 1189-1231) is a real production seam gap or just test-side coupling that can be fixed with the existing public API.

**Background:** PROJ-479 deferred this with the assumption that a "public state-restore API" needs to be introduced. Codex consult flagged this as [unverified] — neither agent has read the production class. This phase resolves the question before committing to either PROJ-491 or PROJ-493 work.

---

## Tasks

### Task 4.1: Identify the production class
**File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py` (lines 1189-1231)
**Tests:** none — read-only

- [x] Open `tests/unit/ui/screens/test_strategy_game_state_manager.py` at lines 1189-1231.
- [x] Identify the import path of the class whose `_per_player_ui_state` is accessed.  
  _Finding:_ ``StrategyGameStateManager`` at ``game/ui/screens/strategy_game_state_manager.py``. The actual ``_per_player_ui_state.load(...)`` test reads are at lines **1287/1288/1307/1347/1456/1457/1480/1488** (PROJ-479's line ref to 1189-1231 was approximate).
- [x] Read the production class definition.  
  _Finding:_ The container is a ``PerPlayerUiState`` instance constructed in ``StrategyGameStateManager.__init__`` (line 73). The class itself lives at ``game/ui/screens/per_player_ui_state.py`` and exposes **fully public** ``save``, ``load``, ``has``, ``discard`` methods.

### Task 4.2: Check for existing public restore API
**File:** the production class identified in Task 4.1
**Tests:** none — read-only

- [x] Search for methods named `restore`, `load`, `apply_per_player_state`, `set_player_state`, etc.  
  _Finding:_ ``StrategyGameStateManager`` exposes only **private** methods that touch the container: ``_capture_outgoing_player_state``, ``_restore_incoming_player_state``, ``_apply_turn_start_state``. The container itself (``PerPlayerUiState``) has the public ``load``/``save``/``has``/``discard`` API, but the manager does not re-export it.
- [x] Check the docstring / public-API contract section of the class.  
  _Finding:_ No documented public restore API. The container's docstring even says it is "owned by ``StrategyGameStateManager``" and called by the manager's turn-start helpers — i.e. encapsulated, not re-exported.
- [x] Determine: does a public method exist that performs the same operation as `_per_player_ui_state.load(...)`?  
  _Finding:_ **No public manager-level accessor exists.** ``manager._per_player_ui_state.load(...)`` reaches through a private attribute to call the container's public method. Adding a one-line ``@property def per_player_ui_state(self)`` (or a ``restore_per_player_state(empire_id, slot)`` method) on the manager would close the gap — that's a small production change, not a test rewrite.

### Task 4.3: Decision and routing
**File:** `plan.md` + `decisions.md`
**Tests:** none

- [x] **If public API exists:** keep task in PROJ-491. Add a new task to Phase 1 (Task 1.20: rewrite test_strategy_game_state_manager.py lines 1189-1231 to use the public API). Document in `decisions.md`.  
  _Result:_ Not applicable — no public API exists at the manager level.
- [x] **If no public API exists:** move task to PROJ-493. Add a new phase or task to PROJ-493 describing the production seam (`def restore_per_player_state(self, ...)`). Document the routing decision in BOTH this project's `decisions.md` AND PROJ-493's `decisions.md`.  
  _Result:_ Routed to PROJ-493. Decision recorded in this project's ``decisions.md`` and in ``Projects/active_projects/PROJ-493/decisions.md``.
- [x] In either case, update `plan.md` Current State with the decision and the new task location.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Decision recorded in `decisions.md`
- [x] Task routed to PROJ-491 Phase 1 OR moved to PROJ-493 with cross-references
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State

_Source: PROJ-479 Phase 3 Task 3.20 second bullet. See [findings/source_review.md](findings/source_review.md)._
