# Phase 1: Golden phase-list test (TDD baseline)

**Status:** Not Started
**Objective:** Land a test that pins the current 14-phase tick order and arg-resolver shape. The test passes against the current code by introspecting `_process_tick`'s call sequence via mock instrumentation. Phase 2-3 will rewrite production to match this golden list explicitly.

---

## Tasks

### Task 1.1: Capture current phase order via instrumented mock [Medium]
**File:** `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` (new)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_default_tick_phase_list.py -v`

- [ ] Module docstring referencing PROJ-365 Phase 1.
- [ ] Build a `TurnEngine` with mock engines (reuse `mock_engines.py` fixtures).
- [ ] Wrap `_time_phase` to capture `(phase_name, callable_repr, args_signature)` tuples in order.
- [ ] Run `_process_tick(tick=1, ...)` and `_process_tick(tick=5, ...)` (covering tick==1-only branches).
- [ ] Build the expected golden list — extract from `turn_engine.py:703-782` exactly. Format:
  ```python
  GOLDEN_PHASE_ORDER = [
      'harvesting',
      'resources',
      'fuel_gen',
      'planet_energy',
      'resupply',
      'production',
      'environmental',
      'instant_orders',
      'actions',
      'planet_actions',
      'activation_timers',
      'planet_modifier_effects',  # (or whatever phase_key is chosen for the line-751 call)
      'movement_calc',
      'movement_apply',
      'combat',
  ]
  ```
- [ ] Assert captured order == GOLDEN_PHASE_ORDER.

**Notes:** _(filled during implementation)_

### Task 1.2: tick==1-only behaviors [Simple]
**File:** Same

- [ ] `test_log_empire_state_called_only_on_tick_1`:
  - Wrap `self._log_empire_state` and verify it's called twice on tick==1 (TURN START, AFTER CONSTRUCTION) and zero times on tick==5.
- [ ] These are characterization for the `tick_gating='only_tick_1'` descriptor field that Phase 2 will introduce.

**Notes:** _(filled during implementation)_

### Task 1.3: PROJ-320 moved_fleet_ids invariant guarded [Simple]
**File:** Same

- [ ] `test_combat_phase_receives_moved_fleet_ids_from_movement_diff`:
  - Stand up real (not mock) movement + conflict engines.
  - Move one fleet via `apply_movements`.
  - Assert combat phase receives `moved_fleet_ids = {<that fleet's id>}`.
- [ ] This is redundant with `test_turn_engine_phase_320_movement_diff.py` but pins the invariant inside the same module that documents the new descriptor design.

**Notes:** _(filled during implementation)_

### Task 1.4: Verify all tests green against current code [Simple]
- [ ] Run the file. All tests pass against the current imperative `_process_tick`. This is characterization — production code is unchanged.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [ ] Golden-list test green
- [ ] tick==1 gating characterization green
- [ ] PROJ-320 invariant assertion green
- [ ] Update plan.md phase table to `Complete`; Current State → Phase 2
