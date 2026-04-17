# PROJ-269 Continuation Prompt — Phase 6 (Legacy Deletion)

Copy the prompt below into a new Claude Code session to resume work on PROJ-269.

---

## PROMPT TO PASTE

You are continuing **PROJ-269: Unified Battle Simulator Entry/Exit**.
Phases 1 through 5.5 are complete. Phase 6 (final legacy-deletion phase)
needs to be executed. Phase 6 is irreversible — code gets deleted, not
just refactored — so this requires careful staged work.

You are the **Implementation Agent**. Do NOT make code changes until
context loading is complete and you have announced readiness. You may
encounter design questions; log them in `decisions.md` rather than guess.

### CONTEXT LOADING (do all of this before writing any code)

**1. Read the project-wide rules in `CLAUDE.md`:**
   - The three non-negotiable rules: TDD always, docs check-before /
     update-after, clean-sheet design.

**2. Read the protocols (in this order):**
   - `Projects/protocols/02_plan_protocol.md` (how to use the plan)
   - `Projects/protocols/03a_continue_working.md` (autonomous loop)

**3. Read the PROJ-269 package (in this order):**
   - `Projects/active_projects/PROJ-269/plan.md` — pay close attention to
     the **"Phase 6 Handoff"** section in Current State; that's your roadmap
   - `Projects/active_projects/PROJ-269/decisions.md` — 18+ locked decisions;
     the post-Phase-5.5 entries explain non-obvious design choices you
     must respect
   - `Projects/active_projects/PROJ-269/design.md` — DTO schemas + target
     architecture; still authoritative
   - `Projects/active_projects/PROJ-269/phase_6_checklist.md` — the
     15-task list you'll work through
   - `Projects/active_projects/PROJ-269/manifest.md` — file inventory
     (note path divergences section)
   - `Projects/active_projects/PROJ-269/phase_5_5_checklist.md` — most
     recent completed phase; read its Notes for context on what
     `ModifierStack` plumbing now exists

**4. Read the architecture foundation docs:**
   - `docs/README.md` (reading order)
   - `docs/01_ARCHITECTURE.md` — note the post-PROJ-269 Phase 1-5.5
     additions (BattleSpec/BattleOutcome DTOs, run_battle, etc.)
   - `docs/02_PATTERNS.md` §13 — the "Battle Mode Strategy" pattern is
     marked DEPRECATED with a pointer to the spec compiler pattern;
     your Phase 6 work removes the deprecated path
   - `docs/03_CONVENTIONS.md` — naming + file org

**5. Read the unified-flow doc:**
   - `docs/systems/combat_simulation.md` — §0 "Unified Entry" describes
     the new architecture (boundary, formation, telemetry, modifier_stack
     all wired). Phase 6 will rewrite §1 "Battle Orchestration" to
     remove BattleMode references after deletions.

**6. Read the current state of the code Phase 6 will touch (do not
modify any of this — just load it):**
   - `game/simulation/battle_runner.py` — your unified entry; needs to
     stop using `BattleController`/`BattleConfig` (Tasks 6.1/6.2/6.3)
   - `game/simulation/battle_controller.py` — currently used by
     `run_battle`; Phase 6 ideally bypasses it entirely
   - `game/simulation/battle_config.py` — `BattleMode` enum + config
     dataclass; both up for deletion or radical reshaping
   - `game/simulation/combat/battle_mode_handler.py` — 4 classes to delete
   - `game/ui/services/battle_factories.py` — 4 `create_*_battle` functions
     to delete
   - `game/strategy/adapters/simulation_adapter.py` —
     `SimulationBattleResolver` with ship-mutation side channels; rewrite
     to use `build_strategy_battle_spec` + `run_battle` (Phase 5.5
     ModifierStack pipeline replaces the mutations)
   - `game/strategy/data/fleet_battle_adapter.py` — `update_from_battle_results`
     replaced by `PostBattleHook`; can be deleted after Task 6.5/6.11
   - `combat_lab/runner.py` — `USE_BATTLE_RUNNER` flag + dual paths;
     **read the Phase 6 Handoff carefully** — Task 6.7 is blocked by
     the compiler only supporting `StaticTargetScenario`
   - `combat_lab/spec_compiler.py` — needs extending to support the
     other 4 templates (Duel/Propulsion/Resource/Comparison) BEFORE
     Task 6.7 can be done
   - `combat_lab/scenarios/templates.py` — 5 templates;
     `ComparisonScenario._run_baseline_battle` needs a rewrite (Task 6.8)
   - `game/ui/screens/battle_setup_screen.py` —
     `_apply_complex_modifiers` ship mutation needs to go (Task 6.4)
   - `game/ui/screens/test_lab/test_executor.py` — 4 paths to migrate
     (Task 6.9; highest UI risk)
   - `combat_lab/services/test_execution_service.py` — `_is_started=True`
     hack to remove (Task 6.10)

**7. Establish baseline:**
   - Run `pytest tests/ --tb=no -q` — record pass count. Should be
     **14709 passed, 2 skipped, 3 failed, 3 errors** (the 3 fail / 3
     error are pre-existing baseline; do not try to fix them).
   - Run `python -m combat_lab.run_tests --fast --no-history` —
     record pass count. Should be **162 passed**.
   - Run `git status` — confirm clean working tree.
   - Run `python Projects/scripts/validate_phase.py PROJ-269 5_5` —
     should PASS (validates Phase 5.5 is closed).

### CONFIRMATION STEP

After context loading, BEFORE starting any task, respond with:

  **(a)** A one-paragraph summary of where PROJ-269 stands and what
       Phase 6 needs to accomplish.
  **(b)** Three locked architectural decisions most relevant to Phase 6
       (look in decisions.md).
  **(c)** The pytest + combat_lab baselines from step 7.
  **(d)** Any discrepancies you found between docs and code (per
       CLAUDE.md Rule 2, flag them).
  **(e)** Your proposed task order for Phase 6, accounting for the
       blocker called out in the plan's Phase 6 Handoff section.
  **(f)** Explicit statement that you are ready to begin (and which
       task you'll start with).

### WORK STYLE

- Strict TDD per CLAUDE.md Rule 1 — every task starts with a failing
  test, then implementation.
- Use `pytest tests/path/to/test.py --tb=short` for incremental runs.
- After each task: check off subtasks in `phase_6_checklist.md`, add
  implementation notes, update `plan.md` Current State before
  switching tasks.
- One task `in_progress` on the TodoWrite list at a time.
- If you hit an unexpected design question, do NOT guess — add an
  entry in `decisions.md` with rationale OR ask the user.

### CRITICAL CONSTRAINTS

- **The Combat Lab fast suite (162 scenarios) MUST stay green.** Any
  change that breaks even one combat_lab scenario is a regression.
- **`pytest tests/`** — the +14709 baseline must be maintained or
  increased. The 3 pre-existing failures + 3 pre-existing import
  errors are out of scope.
- **`run_battle(spec)` is the only sanctioned engine entry.** When
  migrating call sites, every replacement must go through `run_battle`.
  Do not invent alternate entry points.
- **Phase 5.5's `ModifierStack` pipeline replaces ship-mutation side
  channels.** When Task 6.5/6.11 deletes `_apply_shield_interference`
  / `_apply_strategic_modifiers`, the equivalent effect comes from
  the strategy compiler emitting the right `ModifierEntry` entries.
  Compilers currently emit placeholder effects (`stat_key="placeholder"`)
  for content the engine doesn't yet apply — that's intentional, not
  a bug. Real effect mapping is post-PROJ-269 content work.
- **No backward compatibility shims.** Per CLAUDE.md Rule 3 + the
  System Migration Policy, this phase deletes the old paths
  completely. No fallbacks, no `if legacy_mode:` branches, no
  commented-out code "in case we need it".

### STOP CONDITION

Stop when ANY of these occurs:
- Phase 6 complete: all 15 tasks checked, validate_phase 6 passes,
  full regression green, manual smoke clean, plan.md updated
- Context usage approaches 80%
- Blocker that requires user input (decisions.md not enough)
- Tests failing that you cannot resolve

When stopping, follow protocol 02 — update Current State with
specific handoff context, list what the next agent needs to know.

### KEY FILES TO TOUCH (by Phase 6 task)

- 6.7a (compiler extension): `combat_lab/spec_compiler.py`,
  `tests/unit/combat_lab/test_spec_compiler.py`
- 6.7: `combat_lab/runner.py`
- 6.8: `combat_lab/scenarios/templates.py` (`ComparisonScenario`)
- 6.10: `combat_lab/services/test_execution_service.py`
- 6.5/6.11: `game/strategy/adapters/simulation_adapter.py`
- 6.4: `game/ui/screens/battle_setup_screen.py`
- 6.6: `game/strategy/data/fleet_battle_adapter.py`
- 6.9: `game/ui/screens/test_lab/test_executor.py`
- 6.1/6.2/6.3: `game/simulation/combat/battle_mode_handler.py`,
  `game/simulation/battle_config.py`, `game/ui/services/battle_factories.py`,
  AND extensive call-site migration (35 files audited; many tests
  need updating)
- 6.13: `docs/systems/combat_simulation.md` (rewrite §1)
- 6.14: `docs/02_PATTERNS.md` (remove §13 entirely once code is gone)

### START

Once context loading is complete and you have produced the (a)–(f)
confirmation, begin with **Task 6.7a (compiler extension)** unless your
audit reveals a different correct first step. Without 6.7a, Task 6.7
cannot complete safely (~80 combat_lab scenarios depend on the legacy
fallback path).

Good luck. PROJ-269 is the largest refactor in the repo's history;
Phase 6 is the cleanup that makes it real.
