# PROJ-270 Continuation Prompt — Complete the Unified Battle Simulator Closure

Copy the prompt below into a new Claude Code session to finish PROJ-270.

---

## PROMPT TO PASTE

You are continuing **PROJ-270: Unified Battle Simulator Entry/Exit — Closure**, which is itself the continuation of PROJ-269. Most of the substantive architectural work is done; you're finishing the last ~20% — a couple of moderate refactors, the manual-smoke gate, the docs-finish touches, and final archival.

**You are the Implementation Agent.** Do NOT make code changes until context loading is complete and you have announced readiness. If anything you encounter is ambiguous, contradictory, or surprising, **stop and ask the user** — do not guess.

---

## PHASE 1: CONTEXT LOADING (MANDATORY — do all of this before touching code)

### 1a. Project-wide rules

Read [`CLAUDE.md`](../../../CLAUDE.md) thoroughly:
- The three non-negotiable rules (TDD always, docs check-before / update-after, clean-sheet design)
- System Migration Policy ("ERADICATE the old system completely")
- Long-term quality heuristics
- Commit / PR flow

### 1b. Protocols

Read in order:
- [`Projects/protocols/02_plan_protocol.md`](../../protocols/02_plan_protocol.md) — how to use the plan
- [`Projects/protocols/03a_continue_working.md`](../../protocols/03a_continue_working.md) — autonomous work loop
- [`Projects/protocols/04_audit_project.md`](../../protocols/04_audit_project.md) — needed for the project-closure step
- [`Projects/protocols/05_close_project.md`](../../protocols/05_close_project.md) — how to archive a project

### 1c. Architecture documentation (read BEFORE touching code)

- [`docs/README.md`](../../../docs/README.md) — reading order index
- [`docs/01_ARCHITECTURE.md`](../../../docs/01_ARCHITECTURE.md) — Battle Flow section was refreshed in PROJ-270; pay attention to the "PROJ-270 Phase 4" note
- [`docs/02_PATTERNS.md`](../../../docs/02_PATTERNS.md) §13 — "Spec Compiler + run_battle" pattern
- [`docs/03_CONVENTIONS.md`](../../../docs/03_CONVENTIONS.md) — naming + file layout
- [`docs/04_SERVICES.md`](../../../docs/04_SERVICES.md) — BattleService section has the PROJ-269/270 note
- [`docs/systems/combat_simulation.md`](../../../docs/systems/combat_simulation.md) — §0 "Unified Entry" + §1 "Battle Orchestration" + §2 "Battle Modes removed" — read in full
- [`docs/systems/strategy_layer.md`](../../../docs/systems/strategy_layer.md) — Strategic-to-Combat Bridge section has the PROJ-270 Phase 6 update

### 1d. Parent project — PROJ-269

Read in this order:

- [`Projects/active_projects/PROJ-269/plan.md`](../PROJ-269/plan.md) — **pay attention to the cross-link at the top of Current State pointing to PROJ-270**
- [`Projects/active_projects/PROJ-269/decisions.md`](../PROJ-269/decisions.md) — 18+ locked decisions including the Phase 5.5 "placeholder effects silently skipped" decision (PROJ-270 Phase 6 closed this)
- [`Projects/active_projects/PROJ-269/design.md`](../PROJ-269/design.md) — target DTOs
- [`Projects/active_projects/PROJ-269/phase_6_checklist.md`](../PROJ-269/phase_6_checklist.md) — what Phase 6 claimed to deliver

### 1e. THIS project — PROJ-270

Read EVERYTHING in this order:

1. [`Projects/active_projects/PROJ-270/plan.md`](plan.md) — start with **## Current State** which has a detailed inventory of completed vs deferred items
2. [`Projects/active_projects/PROJ-270/design.md`](design.md) — audit findings + architectural decisions + validator-to-outcome mapping
3. [`Projects/active_projects/PROJ-270/decisions.md`](decisions.md) — 9 locked architectural decisions (scope trim, visual-mode approach, acceptance criteria, etc.)
4. [`Projects/active_projects/PROJ-270/manifest.md`](manifest.md) — file inventory across all 8 phases
5. All 8 phase checklists in order — each has task-level completion notes:
   - [phase_1_checklist.md](phase_1_checklist.md) (Complete)
   - [phase_2_checklist.md](phase_2_checklist.md) (Complete)
   - [phase_3_checklist.md](phase_3_checklist.md) (Complete)
   - [phase_4_checklist.md](phase_4_checklist.md) (Partial — 4.4+4.5 done; 4.2/4.3/4.7 remain)
   - [phase_5_checklist.md](phase_5_checklist.md) (Partial — 5.1/5.2/5.3/5.5 done; 5.4 remains)
   - [phase_6_checklist.md](phase_6_checklist.md) (Track A complete, Track B deferred to PROJ-271)
   - [phase_7_checklist.md](phase_7_checklist.md) (Partial — 7.1/7.2/7.4/7.5 done; 7.3 deferred)
   - [phase_8_checklist.md](phase_8_checklist.md) (Partial — 8.1/8.2/8.3/8.5-partial done; 8.4/8.5-finish/8.6/8.7 remain)

### 1f. Code under review — read enough to form independent judgement

The **landed architectural contract** (do NOT break these; the pytest guards will fail if you do):

- [`game/simulation/battle_runner.py`](../../../game/simulation/battle_runner.py) — `run_battle(spec)`, `start_engine_from_spec`, `materialize_spec_ships`, `extract_outcome` — these are the only sanctioned ways to start / drive / conclude a battle
- [`game/simulation/battle_spec.py`](../../../game/simulation/battle_spec.py) — `BattleSpec` + nested DTOs
- [`game/simulation/battle_outcome.py`](../../../game/simulation/battle_outcome.py) — `BattleOutcome` + `ShipOutcome` (now with display fields from PROJ-270 Phase 4.5: name, ship_class, hp, max_hp, current_shields, max_shields)
- [`game/simulation/battle_config.py`](../../../game/simulation/battle_config.py) — trimmed to operational-options only; `ReturnDestination` re-exported from `game.core.return_destination`
- [`game/simulation/battle_controller.py`](../../../game/simulation/battle_controller.py) — now has `set_spec` + `get_outcome`; emits `BattleOutcome` at battle end
- [`game/simulation/combat/fleet_aura_manager.py`](../../../game/simulation/combat/fleet_aura_manager.py) — `initialize(ships, *, modifier_stack=...)` only; legacy `config=` kwarg deleted
- [`game/strategy/combat/spec_compiler.py`](../../../game/strategy/combat/spec_compiler.py) — emits REAL stat_keys (shield_capacity_mult, damage_mult) for storm + fleet multipliers
- [`combat_lab/services/scenario_run_helper.py`](../../../combat_lab/services/scenario_run_helper.py) — shared `run_scenario_via_run_battle(scenario, ...)` returning `(outcome, telemetry)`
- [`combat_lab/telemetry.py`](../../../combat_lab/telemetry.py) — `CombatLabTelemetry` forensic bundle
- [`game/ui/screens/battle_results_data.py`](../../../game/ui/screens/battle_results_data.py) — `extract_battle_results(outcome, return_destination)` — outcome-driven
- [`game/core/return_destination.py`](../../../game/core/return_destination.py) — `ReturnDestination` enum

The **regression guards** (these MUST stay green as you work):

- [`tests/unit/simulation/test_unified_entry_guard.py`](../../../tests/unit/simulation/test_unified_entry_guard.py) — 12 guards covering acceptance criteria
- [`tests/unit/combat_lab/test_template_no_legacy_setup.py`](../../../tests/unit/combat_lab/test_template_no_legacy_setup.py) — 9 guards
- [`tests/unit/simulation/battle_controller/test_outcome_emission.py`](../../../tests/unit/simulation/battle_controller/test_outcome_emission.py) — 4 tests

### 1g. Establish baseline

Run these and compare against the expected numbers:

```bash
pytest tests/ --tb=no -q
python -m combat_lab.run_tests --fast --no-history
python -m combat_lab.run_tests --no-history
git status
```

**Expected baselines** (from the last PROJ-270 session):
- `pytest`: **14608 passed**, 2 skipped, 3-4 failed (pre-existing build-queue UI + occasionally a flaky `test_colony_owner_id_matches_empire` or `test_three_components_weighted_selection` — both pass in isolation), 3 errors (pre-existing AI imports)
- Combat Lab fast: **162/162 green**
- Combat Lab full: **170/170 green**
- `git status`: likely clean if the prior session committed; if there are uncommitted PROJ-270 changes, confirm with the user before proceeding

**If pytest numbers are materially different, STOP and ask the user.** Something between sessions may have changed.

---

## PHASE 2: CONFIRMATION STEP (BEFORE any code changes)

After context loading, respond with:

**(a)** A summary (1-2 paragraphs) of what PROJ-270 accomplished so far and what specifically remains. Demonstrate you've actually read the checklists, not just skimmed.

**(b)** The baseline numbers you observed from Phase 1g.

**(c)** A **prioritized plan** for the remaining work. The deferred items from the last session are:

| Item | Phase | Scope | Risk |
|------|-------|-------|------|
| `BattleController.configure(spec)` tighten | 4.2/4.3 | Make `set_spec` required/inline | LOW |
| `BattleConfig.map_bounds` → `BattleSpec.boundary` | 5.4 | `RetreatManager` must consume `BoundaryRegion` | MEDIUM |
| Visual-mode UI fixture with real spec | 7.3 | Integration test; currently `teams=()` shortcuts | LOW |
| Docstring-example sweep | 8.5 finish | Scenario files + any stale examples | LOW |
| Manual-audit walkthrough | 8.4 | Checklist-driven acceptance audit | LOW |
| Manual launcher smoke | 8.7 + PROJ-269 residual | Interactive desktop session | LOW |
| Final project regression + audit | 8.7 | `validate_phase PROJ-270 all` + protocol 04 | LOW |
| Archive PROJ-269 + PROJ-270 | 8.6 | Move to `archived_projects/` | LOW |
| Create PROJ-271 planning skeleton | (new project) | flat_shield_bonus + suppressor battle-math (Track B) | — |

Propose an **ordering** (which items first, which last) with reasoning. Note any items you think should be dropped or re-scoped.

**(d)** **Questions for the user** — this is the critical step. Ask at least about:

1. **Manual launcher smoke**: do you have an interactive desktop session available right now, or should we defer 8.7 to a separate human-run session?
2. **Scope of 5.4 (map_bounds → boundary)**: `RetreatManager` is a substantial refactor. Is the user OK with keeping `BattleConfig.map_bounds` as a legacy-compat shim indefinitely, OR do they want the full refactor now?
3. **PROJ-271 scope**: should you create a PROJ-271 planning package at the end of PROJ-270, or leave that to a future session?
4. **Archival timing**: PROJ-269 is still in `active_projects/` pending its own manual launcher smoke. Should PROJ-270 closure also wait, or archive independently?
5. Any other ambiguity you spot while reading — raise it. **Do not guess.**

**(e)** Explicit statement: "I am ready to proceed. After user answers the questions above, I will start with [specific task name]."

---

## PHASE 3: EXECUTE THE PLAN

Once the user has answered your questions:

1. Work through tasks using **Strict TDD** (CLAUDE.md Rule 1). Failing test first, then implementation.
2. Use `pytest tests/ --testmon` for incremental testing.
3. After each task: check off subtasks in the phase checklist, add implementation notes, update `plan.md` Current State before switching tasks.
4. Keep exactly ONE todo `in_progress` at a time.
5. If you discover an unexpected design question, do NOT guess — add an entry in `decisions.md` OR ask the user.

### Task-specific guidance

**Task 4.2/4.3 (configure(spec) tighten):** Current shape is `controller.configure(config)` + `controller.set_spec(spec)` — two separate calls. Tighten to `controller.configure(config, spec=spec)` with `spec` required. Migrate all 3 live callers (`app.py`, `test_lab/screen.py`, `test_execution_service.py`). Regression: 14608 pytest + 162 combat_lab.

**Task 5.4 (map_bounds → boundary):** `RetreatManager.__init__(map_bounds: Tuple[float, float, float, float])` reads (min_x, min_y, max_x, max_y) for edge-escape geometry. `BattleSpec.boundary: BoundaryRegion` supports `RectBoundary`, `CircleBoundary`, `UnboundedRegion`. The refactor: `RetreatManager` accepts `boundary: Optional[BoundaryRegion]`; calls `boundary.contains_point(pos)` / `boundary.closest_exit(pos)` or similar. Retreat-disabled when `boundary is None` or `isinstance(boundary, UnboundedRegion)`. Non-trivial because the existing code does raw coordinate math at lines 191 + 224. **Before starting, read `game/simulation/combat/boundary.py` to understand the available API.** If the boundary API doesn't expose what RetreatManager needs, flag to user before adding methods.

**Task 7.3 (visual-mode UI fixture):** `tests/fixtures/test_scenarios.py::create_mock_test_scenario` sets `empty_spec.teams = ()` so `materialize_spec_ships` short-circuits. A realistic fixture would need a minimal `TeamSpec` with 1 ship. Low ROI because no test currently requires it. Consider deleting this from the remaining scope if the user agrees.

**Task 8.4 (manual-audit walkthrough):** Walk through the acceptance criterion from [decisions.md](decisions.md) Decision 3. Verify each of (a)-(e) is still satisfied after any new changes you make. Document results in `Projects/active_projects/PROJ-270/findings/acceptance_audit.md`.

**Task 8.5 finish-touches:** Scan for residual stale docstrings. The prior session updated `combat_simulation.md` §0, `01_ARCHITECTURE.md` Battle Flow, `04_SERVICES.md` BattleService, `strategy_layer.md` Strategic-to-Combat Bridge, `base.py` + `__init__.py` docstring examples, and `02_PATTERNS.md` §13 was already clean. Grep for any remaining `battle_engine.start(` / `scenario.setup(battle_engine)` / `BattleMode` references in docs and production docstrings; clean up.

**Task 8.6 (archival):** Follow [Projects/protocols/05_close_project.md](../../protocols/05_close_project.md). Requires user verification first.

**Task 8.7 (manual launcher smoke):** `python launcher.py` → Combat Lab visual+headless+batch, Battle Setup 2v2 with complex toggles, Strategy fleet conflict with damage persistence. Report results.

**PROJ-271 scaffolding (if user agrees):** Run `python Projects/scripts/create_project.py "Strategic Modifier Battle-Math Track B" --id PROJ-271` and populate:
- `plan.md` — Track B scope (flat_shield_bonus + suppressors)
- `decisions.md` — scope decisions
- `phase_1_checklist.md` — `SHIELD_BONUS_ADD` stat_key + `AbilityStatBinding`
- `phase_2_checklist.md` — compiler emit real stat_key for flat_shield_bonus
- `phase_3_checklist.md` — suppressor opponent-team routing
- `phase_4_checklist.md` — integration tests + manual smoke

---

## PHASE 4: STOP CONDITIONS

Stop when ANY of these occurs:
- All remaining PROJ-270 tasks complete + user has verified
- Context approaching 80%
- Blocker requiring user input
- Tests failing that you cannot resolve

**When stopping:** follow protocol 02 — update `plan.md` Current State with comprehensive handoff, save memory (`C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\`) if the memory's PROJ-270 status entry is out of date, and provide a session summary.

---

## KEY PROTECTIONS — DO NOT BREAK

1. **Strict TDD**: every task begins with a failing test
2. **Regression guards** in `test_unified_entry_guard.py` MUST stay green — if you find them too restrictive, discuss before adjusting; do NOT silently loosen them
3. **Combat Lab 162/162 fast + 170/170 full** MUST stay green
4. **No new `pytest tests/` failures** beyond the known pre-existing 3 build-queue + 3 AI imports + 2 occasional flaky (colony + three_components)
5. **Ask, don't guess** when anything is unclear
6. **No backwards-compat shims** — CLAUDE.md Rule 3. If you're tempted to add one, stop and propose the clean-sheet alternative to the user

---

## ACKNOWLEDGED KNOWN QUIRKS

These are working as intended — don't "fix" them without discussion:

- `BattleScreen.start(team0_ships, team1_ships)` is a test-convenience bypass that doesn't build a spec. `_on_battle_ended` falls back to `_build_fallback_outcome` (synthesizes outcome from engine). This is intentional legacy support for existing tests and does NOT violate the unified-entry contract (outcome is still emitted).
- `game/ui/navigation/` directory was deleted during PROJ-270 — `ReturnDestination` lives at `game/core/return_destination.py` instead (circular-import avoidance).
- `ShipOutcome` display fields (`name`, `hp`, `max_hp`, etc.) default to None/0 for backwards-compat with direct construction (tests).
- `mock_controller.get_outcome.return_value = None` is REQUIRED in test fixtures that mock a BattleController (otherwise `Mock()` returns a Mock, not None, bypassing the fallback).

---

## SUCCESS CRITERIA FOR THIS SESSION

You have succeeded when:

1. All PROJ-270 tasks you committed to in Phase 2(c) are complete
2. Regression gates are all green (pytest + combat_lab)
3. `plan.md` Current State reflects actual project status
4. All 8 phase checklists are up to date
5. If applicable: PROJ-270 archived (following protocol 05); PROJ-271 planning package created (if user requested)
6. User has verified

**Good luck. PROJ-270 is 85% done as of session start; you're bringing it across the finish line.**
