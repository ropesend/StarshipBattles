# Phase 1A: Read-path policy (Pattern #5) + two static guards

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-472 1a`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Document the option-(b) read-path policy in Pattern #5, then add
the two read-path static guards (runtime-import + session-read) mirroring the
write-path guard's structure, each with positive controls and reasoned
allowlists. Guards land FIRST so Phase 1B/1C migrations are enforced as they
land. This phase introduces NO production-code migration.

**TDD note:** For guards, "the failing test first" = the positive-control
assertions and the directory scan that currently catches existing bypass sites.
Write the scan so it FAILS against current code (proving it catches bypasses),
then add the allowlist entries that make the *intended-transitional* sites pass,
leaving net-new bypasses red.

---

## Tasks

### Task 1A.1: Record the read-path policy in Pattern #5 [Medium]
**File:** `docs/02_PATTERNS.md` (Pattern #5, `:148-166`)
**Tests:** N/A (documented contract; consumed by the guards in 1A.2/1A.3)

- [x] In Pattern #5, add a "Read-path policy (PROJ-472)" subsection stating:
      use the facade for session-owned / mutation-adjacent / cross-screen-cached
      reads; allow a documented UI-safe surface for immutable config/value/enum/
      protocol types
- [x] Name the UI-safe read types explicitly: `GameConfig`, `RaceConfig`,
      `EnvironmentalPreference`, `HabitabilityFactor`, `ContainableKind`,
      `ActivationPhase` (and note the list is the guard allowlist's source of truth)
- [x] State the NON-allowlisted live surfaces by example: `BuildQueueSource`,
      `collect_build_queues_at_hex`, `FleetCapabilityCalculator`, `GameSession`,
      mutators, `turn_engine` helpers
- [x] Document the transitional surfaces honestly: `StrategyScreen` pass-through
      properties (`galaxy`/`empires`/`systems`/`active_empire`/`human_player_ids`)
      and `FacadeSessionState.session` remain allowlisted-with-reason; deprecation
      is follow-on (PROJ-475)
- [x] Verify code/doc consistency: the type names in the doc match the live
      symbols (no stale names)

### Task 1A.2: Add the runtime-import read guard [Complex]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py` (new)
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py`

- [x] Write positive-control tests FIRST (mirroring
      `test_facade_bypass_guard.py:208-238`): assert the matcher flags a runtime
      `from game.strategy.data.build_queue_source import BuildQueueSource`, flags
      `collect_build_queues_at_hex` and `FleetCapabilityCalculator`, and does NOT
      flag `game.strategy.facade.*`, `game.strategy.engine.commands`, or a
      `TYPE_CHECKING`-guarded strategy import
- [x] Implement the AST scan over `game/ui/**/*.py` (reuse the
      `_ui_python_files()` shape): parse `Import`/`ImportFrom`, skip nodes inside
      `if TYPE_CHECKING:` blocks, fail on non-allowlisted runtime `game.strategy.*`
      imports
- [x] Add the exact module/member allowlist: always-allow `game.strategy.facade.*`
      + `game.strategy.engine.commands`; UI-safe value/config/enum modules per
      Task 1A.1, each with a reason comment
- [x] Run the scan; confirm it currently FAILS (catches `build_queue_screen.py:23`,
      `fleet_data_source.py:241-245`, and the rest of the cluster) — this proves
      the guard works before 1B migrates them
- [x] Mark the live-cluster sites with an explicit TEMPORARY allowlist-with-reason
      entry (`# PROJ-472 1B will migrate`) so the suite is green at end of 1A and
      the entries are removed as 1B lands; net-new non-allowlisted imports stay red
- [x] Verify a `test_*` sanity test asserts the scan found > 0 files (parametrize
      can't silently produce zero tests), mirroring
      `test_facade_bypass_guard.py:157-164`

### Task 1A.3: Add the session-read guard [Complex]
**File:** `tests/static_guards/test_facade_read_path_session_guard.py` (new)
**Tests:** `pytest tests/static_guards/test_facade_read_path_session_guard.py`

- [x] Write positive-control tests FIRST: matcher flags `c.scene.session.empires`,
      `self._session.registries`, AND `self.facade.facade_state.session.services`;
      does NOT flag `self.facade.empires.all()` or `self.facade.handle_command(...)`
- [x] Implement AST matcher for `<expr>.session.<attr>`, `<expr>._session.<attr>`,
      and `<expr>.facade_state.session.<attr>` reads over `game/ui/**/*.py`,
      skipping `TYPE_CHECKING`
- [x] Add file+attribute-path+reason allowlist: `strategy_screen.py:160-189`
      pass-through property bodies + `:242-276` session property/setter (composition
      root, transitional); `strategy_game_state_manager.py` `session.active_empire`
      write seam; any intentional mutator seam — each with a reason comment
- [x] Run; confirm it currently FAILS on the 1C consumers
      (`strategy_detail_formatter.py:112,278,395-396`, `list_windows.py:69-70`,
      `hex_outlines.py:30,76-79`, `strategy_build_queue_manager.py:82-83`)
- [x] TEMPORARY allowlist those 1C sites with `# PROJ-472 1C will migrate` so 1A
      ends green; remove as 1C lands
- [x] Verify both guards are collected by the static-guard suite
      (`pytest tests/static_guards/`)

### Task 1A.4: Phase 1A verification [Medium]
**File:** n/a
**Tests:** `pytest tests/static_guards/`

- [x] `pytest tests/static_guards/` passes (both new guards green via temporary
      allowlist entries)
- [x] Confirm re-introducing a net-new non-allowlisted UI strategy import OR a
      net-new `.session.<read>` fails the relevant guard (manual spot check or a
      dedicated negative-control test)
- [x] Pattern #5 doc updated and consistent with the guard allowlists

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row 1A to `Complete` (ORCHESTRATOR — plan.md is coordinator-owned; worker does not edit it)
- [ ] Update plan.md Current State to point to Phase 1B (ORCHESTRATOR — coordinator-owned)

_Scope per orchestrator decisions baked into plan.md / decisions.md; consult at
`AgentCoordination/Scratchpad/Consult/proj472_preflesh/advice.md` §2._
