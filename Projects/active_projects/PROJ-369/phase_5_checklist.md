# Phase 5: AST guard + per-phase mock-context tests + docs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-369 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):**
- `tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py` (verify still passes; harden if drift)
- `tests/unit/strategy/turn_engine/test_phase_isolation_with_mock_context.py` (new)
- `docs/systems/strategy_layer.md` (modify)
- `docs/02_PATTERNS.md` § 35 (modify)

**Objective:** Lock in the post-PROJ-369 invariants with regression-strength tests and update documentation. The AST guard test (already created in Phase 3) is verified harder. New per-phase isolation tests demonstrate the descriptor pattern's testability win: each phase invocable with a mock engine exposing only the engines it reads.

---

## Pre-flight

- [ ] Verify Phase 4 status is `verified` (or `committed`) per `phase_dag.py status`

---

## Tasks

### Task 5.1: Harden the AST guard test [Medium]
**File:** `tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py -v`

- [ ] Add test `test_run_phases_called_exactly_twice_in_process_turn`: AST-walk `process_turn`, count `Call` nodes whose `.func.attr == '_run_phases'`. Assert exactly 2.
- [ ] Add test `test_no_inline_engine_method_calls_in_process_turn_loop`: AST-walk `process_turn`. Assert no direct `self.<engine>.process_<X>(...)` calls outside `_run_phases` (whitelist: progress callback, snapshot capture, BUG-109 logging).
- [ ] Add test `test_TurnEngineConfig_create_default_is_only_function_local_engine_import_site`: AST-walk `turn_engine_config.py`'s `create_default` method, allow function-local engine imports. AST-walk `turn_engine.py`, assert zero function-local engine imports.
- [ ] **Verify:** all tests pass
- [ ] **Verify:** the tests would fail if any task in Phase 4 were reverted (sanity check the regex correctness against current code)

**Notes:**

### Task 5.2: Per-phase mock-context isolation tests [Complex]
**File:** `tests/unit/strategy/turn_engine/test_phase_isolation_with_mock_context.py` (new)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_phase_isolation_with_mock_context.py -v`

- [ ] Demonstrate descriptor isolation by exercising each tick descriptor with a `MagicMock` engine exposing ONLY the property the descriptor reads.
- [ ] One parametrized test (or one test per descriptor — choose during execution):
  ```python
  @pytest.mark.parametrize("descriptor", DEFAULT_TICK_PHASE_LIST + DEFAULT_END_OF_TURN_PHASE_LIST,
                           ids=lambda d: d.phase_key)
  def test_descriptor_invokes_via_mock_engine_with_minimal_attrs(descriptor):
      """Each descriptor's callable_target only reads the engine attribute(s)
      its phase_key implies. Pin this by constructing a spec_set MagicMock
      that provides only those attributes."""
      mock_engine = MagicMock(spec_set=['_registries', descriptor.phase_key.replace('_', '_engine_no_translate')])
      # ... build minimal mock_ctx
      target = descriptor.callable_target(mock_engine)
      args, kwargs = descriptor.args_resolver(mock_ctx)
      target(*args, **kwargs)  # should not raise AttributeError
      # assert the phase's engine method was called once
  ```
  Note: phase_key → engine attr mapping is descriptor-dependent (e.g. `'movement_calc'` → `movement_engine`). Build a small lookup dict.
- [ ] At minimum, write 5 such tests covering: `harvesting`, `combat` (with `moved_fleet_ids` shape), `organics_consumption`, `quality_improvement`, `population_growth` — these cover the breadth of arg shapes (single-list, set-kwarg, etc.).
- [ ] **Verify:** tests pass and demonstrate the testability win — each phase exercised in isolation, no full TurnEngine construction needed.

**Notes:**

### Task 5.3: Update `docs/systems/strategy_layer.md` [Medium]
**File:** `docs/systems/strategy_layer.md`
**Tests:** `pytest tests/unit/test_docs_consistency.py -v` (if such a test exists)

- [ ] Find the "Turn execution" / "TurnEngine" section.
- [ ] Replace any mention of `create_default_turn_engine(registries)` with `TurnEngineConfig.create_default(registries, ai_factory=…)` followed by `TurnEngine(registries=…, config=cfg)`.
- [ ] Add a new subsection: "Phase descriptor execution" — describe how `DEFAULT_TICK_PHASE_LIST` (15 entries) and `DEFAULT_END_OF_TURN_PHASE_LIST` (6 entries) drive the entire turn body via `_run_phases`. Reference `turn_phase_registry.py`.
- [ ] Update the `> **Last verified:** YYYY-MM-DD` blockquote per docs/03_CONVENTIONS.md §9.

**Notes:**

### Task 5.4: Update `docs/02_PATTERNS.md` § 35 (TurnEngineConfig) [Medium]
**File:** `docs/02_PATTERNS.md`
**Tests:** `pytest tests/unit/test_docs_consistency.py -v` (if such a test exists)

- [ ] Find § 35 (TurnEngineConfig pattern).
- [ ] Rewrite the "When to Use" guidance: "`TurnEngineConfig.create_default(registries, …)` is the canonical injection entry point for production callers. Tests that need to override specific engines construct a base config via `create_default` then use `dataclasses.replace(cfg, foo_engine=mock)` to swap."
- [ ] Document the precedence rule: `TurnEngine(config=cfg, tick_phases=…, end_of_turn_phases=…)` — explicit phase-list kwargs win over whatever the config implies.
- [ ] Cross-link to PROJ-365 (per-tick descriptor list) and PROJ-369 (this project's completion).
- [ ] Update `> **Last verified:**` blockquote.

**Notes:**

### Task 5.5: Final full-suite verification [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count ≥ baseline + (1 + 4 + 1 + 3 + 5) = baseline + 14 new tests across all 5 phases (Phase 1 added 4, Phase 2 added 3, Phase 3 added 4 AST tests, Phase 4 added 1, Phase 5 added 5+)
- [ ] **Acceptance:** zero regressions

**Notes:**

### Task 5.6: Manual end-to-end smoke [Medium]
**Tests:** Manual

- [ ] Launch the game; create a new save; advance 5 turns; verify no crashes, no behavioral regressions in production / movement / combat / population growth.
- [ ] Load an existing save (if compatible); advance 5 turns; verify the same.
- [ ] Document any observations in `findings/manual_smoke.md`.

**Notes:**

### Task 5.7: Commit Phase 5 [Simple]

- [ ] Commit message: `feat(PROJ-369): Phase 5 — AST guard hardening, per-phase mock-context tests, and documentation`
- [ ] Run `phase_complete.py PROJ-369 5`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] AST guard test passes with hardened invariants
- [ ] Per-phase mock-context tests demonstrate descriptor isolation
- [ ] `docs/systems/strategy_layer.md` describes the unified phase-execution pattern
- [ ] `docs/02_PATTERNS.md` § 35 reflects `TurnEngineConfig.create_default()` as canonical
- [ ] All `> **Last verified:**` blockquotes updated
- [ ] Manual smoke verified
- [ ] Update status at top of this file to `Complete (Committed)`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Run final-audit gate per `claude-proj-audit`
- [ ] On clean audit: merge `proj/PROJ-369/main` to `main`; archive project
