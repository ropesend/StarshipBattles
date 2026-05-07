# Phase 1: Tier-6 documentation drift + convention violations

**Status:** Not Started
**Objective:** Land 8 small mechanical fixes for documentation drift and convention violations. Per-concern commits.

---

## Tasks

### Task 1.1: T6.1 — PlanetaryFacility legacy `resource_levels` fallback decision [Medium]
**File:** `game/strategy/data/planetary_facility.py:73`, `tests/unit/strategy/data/test_planetary_facility_characterization.py:95-108`

- [ ] Surface to user: "CLAUDE.md says old saves are disposable. Codex flagged the `resource_levels` legacy alias at line 73 (and the legacy component-state preservation at lines 80-81) as a save-file migration shim. Per CLAUDE.md, delete it. Confirm before I delete?"
- [ ] On user confirm: delete the fallback. Update characterization tests at `test_planetary_facility_characterization.py:95-108` to remove the legacy-alias assertions (or rewrite to assert the alias raises).
- [ ] On user decline: document the keep-rationale in [decisions.md](decisions.md) and skip task.
- [ ] Commit (if delete): `refactor(planetary-facility): remove legacy resource_levels save-compat per user direction (PROJ-349 T6.1)`

**Notes:**

### Task 1.2: T6.2 — broad-catch annotation [Simple]
**File:** `game/ui/panels/race_environment_panel.py:322-333`

- [ ] Read the broad catch. Document the intent (likely "swallow rendering errors so a single bad value doesn't crash the whole panel").
- [ ] Add `# Intentional broad catch: <reason>` per `CLAUDE.md` convention.
- [ ] Commit: `chore(race-environment-panel): annotate intentional broad catch per CLAUDE.md (PROJ-349 T6.2)`

**Notes:**

### Task 1.3: T6.3 — ActionExecutionEngine DI fix [Medium]
**File:** `game/strategy/engine/action_execution_engine.py:55-68, 165-168`, `tests/unit/strategy/engine/test_action_execution_engine_gaps.py:128-156`

- [ ] Read both spans. The injected `action_time_resolver` is accepted at lines 55-68 but never used — line 165-168 calls the static resolver instead.
- [ ] Decide: use the injected resolver (DI was intended) OR remove the parameter (DI was vestigial).
- [ ] Default: use the injected resolver. Document choice in [decisions.md](decisions.md).
- [ ] Update `_resolve_action_time` (or whatever) to consult `self.action_time_resolver` if non-None.
- [ ] Rewrite `test_action_execution_engine_gaps.py:128-156` from "asserts injected instance is never consulted" → "asserts injected instance IS consulted".
- [ ] Commit: `fix(action-execution-engine): consume injected action_time_resolver instead of static (PROJ-349 T6.3)`

**Notes:**

### Task 1.4: T6.4 — hardcoded ability lists → registry scan [Medium]
**File:** `game/ui/screens/planet_abilities_controller.py:29-48`

- [ ] Read lines 29-48. Hardcoded ability-name lists violate `docs/03_CONVENTIONS.md:500-512`.
- [ ] Replace with a registry-driven scan: `[name for name in registry.iter_abilities() if predicate(name)]` or similar. Match an existing registry-scan pattern from elsewhere in the codebase.
- [ ] Update tests if any pin the hardcoded list.
- [ ] Commit: `refactor(planet-abilities-controller): replace hardcoded ability list with registry scan (PROJ-349 T6.4)`

**Notes:**

### Task 1.5: T6.5 — LLMUnexpectedError in ErrorCode taxonomy [Simple]
**File:** `game/services/llm/errors.py`

- [ ] Read existing ErrorCode enum/taxonomy.
- [ ] Add `LLM_UNEXPECTED` (or matching naming) to ErrorCode.
- [ ] Wire `LLMUnexpectedError.code = ErrorCode.LLM_UNEXPECTED`.
- [ ] Add a test asserting `LLMUnexpectedError().code is not None`.
- [ ] Commit: `fix(llm-errors): add LLMUnexpectedError to ErrorCode taxonomy (PROJ-349 T6.5)`

**Notes:**

### Task 1.6: T6.6 — strategy load dialog as blocking modal [Medium]
**File:** `game/ui/screens/strategy_screen_lifecycle.py:64-77`, `strategy_window_manager.py:122-143`, `strategy_event_router.py:47-73`

- [ ] Read `show_load_game_dialog()` at lines 64-77 — currently creates raw `SaveSelectionWindow` and discards.
- [ ] Read `StrategyWindowManager` slot list at lines 122-143 — no load/save slot.
- [ ] Read `iter_live_modals()` at `strategy_event_router.py:47-73` — modal detection misses load.
- [ ] Add a `load_dialog` slot (or similar) to `StrategyWindowManager`. Track instance lifecycle. Make `iter_live_modals` include it.
- [ ] Add a regression test: open load dialog; tick strategy event router; assert input is blocked.
- [ ] Commit: `fix(strategy-modal): track load dialog as blocking modal (PROJ-349 T6.6)`

**Notes:**

### Task 1.7: T6.7 — docs timestamp [Simple]
**File:** `docs/05_ERROR_HANDLING.md`

- [ ] Bump "Last verified" timestamp to today's date.
- [ ] Commit: `docs(error-handling): bump last-verified timestamp (PROJ-349 T6.7)`

**Notes:**

### Task 1.8: T6.8 — facade `_session` lint enforcement decision [Medium]
**File:** `Tools/lint_test_files.py` (possibly)

- [ ] Surface to user: "Facade `_session` is convention-protected only — no runtime/lint enforcement. Options: (a) add lint rule banning `<facade>._session` access from outside the facade module, (b) accept convention-only with a note. Recommend (a) for safety."
- [ ] Execute per user direction; commit `chore(lint): enforce facade _session boundary (PROJ-349 T6.8)` or note rationale in decisions.md.

**Notes:**

### Task 1.9: Phase 1 verification
- [ ] `pytest tests/unit/ -q` — all pass.
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update Current State to Phase 2.

---

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] ~7-8 commits landed
- [ ] plan.md phase row → `Complete`
