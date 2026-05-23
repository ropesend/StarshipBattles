# PROJ-456 Phase 2: `build_context` legacy-kwarg sweep

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-456 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** None (Phase 1 not a hard prerequisite — write scopes are disjoint).
**Review Mode:** standard
**Objective:** Retire the dual-name `build_context` / `initial_yard` constructor kwarg on **`BuildQueueScreen`**. Migrate all `BuildQueueScreen(..., build_context=...)` callers to `initial_yard=`, then remove the legacy parameter from the signature and the `effective_initial_yard` resolution.

**Source-of-truth finding:** F-C-006 in [`findings/PROJ-456_findings.md`](findings/PROJ-456_findings.md).

**Scope clarification (codex r5 audit 2026-05-19):** F-C-006 is scoped to the **`BuildQueueScreen` constructor only**. The `BuildQueueController` class at `game/ui/panels/build_queue_controller.py:66-85` accepts `build_context` as a legitimate, non-legacy parameter — its callers are OUT OF SCOPE for this phase. When auditing, filter on the class name `BuildQueueScreen(...)`, NOT the raw kwarg name `build_context=`.

**Out-of-scope files (these are `BuildQueueController(build_context=...)` callers, controller API is legitimate):**
- `tests/unit/ui/panels/test_build_queue_controller.py:57-87`
- `tests/unit/ui/panels/test_build_queue_catalog_threading.py:20-30`
- `tests/unit/strategy/engine/test_production_repro.py:150-157,201-206`
- `tests/integration/ui/build_queue_screen/test_controller_multi_queue.py:77-116`

**Blast radius (verified 2026-05-19 against `BuildQueueScreen(...)` constructor sites only):** 1 production file + 1 test file (the lifecycle file has ~25 call sites internally).

---

## Tasks

### Task 2.1: Audit caller surfaces [Simple]
**Files:**
- `game/ui/screens/build_queue_screen.py:50-90` (target — `BuildQueueScreen.__init__`)
- `game/ui/screens/strategy_build_queue_manager.py:128` (production caller)
- `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (~25 in-scope sites)

- [x] Re-confirm `BuildQueueScreen(...)` scope. PowerShell-safe verification: `rg -n "BuildQueueScreen\([^)]*build_context\s*=" game tests` (try `--multiline` if calls span lines). Note any additional surfaces discovered as a `decisions.md` row.
- [x] Spot-check the out-of-scope controller files listed above; confirm they call `BuildQueueController(build_context=...)`, not `BuildQueueScreen(...)`. Do not touch them in this phase.
- [x] Read `build_queue_screen.py:50-90` — the `__init__` signature at 50-66 + the docstring at 67-87 + the resolution line at 90.
- [x] Confirm `initial_yard` is keyword-only and `build_context` is positional-or-keyword (per the F-C-006 framing).

### Task 2.2: Migrate the production caller [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/ -k "strategy_build_queue" -q`

- [x] Read the existing `BuildQueueScreen(..., build_context=...)` construction site (line 128 at HEAD).
- [x] **GREEN**: Replace `build_context=<value>` with `initial_yard=<value>`. Confirm semantic equivalence — both paths resolve to `effective_initial_yard` today.
- [x] Run targeted tests.

### Task 2.3: Migrate the BuildQueueScreen test caller [Simple]
**Files:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (the only in-scope test file under the F-C-006 / `BuildQueueScreen(...)` filter; ~25 call sites internally).

**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -q`

- [x] Sweep `BuildQueueScreen(..., build_context=<value>, ...)` → `BuildQueueScreen(..., initial_yard=<value>, ...)` for every call site in this file.
- [x] Run the test file after migration.
- [x] PowerShell-safe verification: `rg -n "BuildQueueScreen\([^)]*build_context\s*=" tests` returns 0 hits (use `--multiline` if calls span lines).
- [x] Do NOT touch the controller-API files (`tests/unit/ui/panels/test_build_queue_controller.py`, `test_build_queue_catalog_threading.py`, `tests/unit/strategy/engine/test_production_repro.py`, `tests/integration/ui/build_queue_screen/test_controller_multi_queue.py`); those legitimately use `BuildQueueController(build_context=...)`.

### Task 2.4: Delete the legacy parameter [Simple]
**File:** `game/ui/screens/build_queue_screen.py:50-90` + the `__init__` signature.
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -q`

- [x] **GREEN**: Remove `build_context=None` from the `__init__` signature (line 53 at HEAD).
- [x] **GREEN**: Drop the `effective_initial_yard = initial_yard if initial_yard is not None else build_context` resolution at line 90; replace with `effective_initial_yard = initial_yard`. (Or simplify further — inline `initial_yard` into the downstream calls if it has only one consumer.)
- [x] **GREEN**: Update the docstring at 84-87 — drop the "The legacy `build_context` positional/keyword arg is preserved for back-compat" paragraph; describe only the current `initial_yard` keyword.
- [x] Run targeted tests; confirm constructor signature no longer accepts `build_context=`.
- [x] **Verify with class-name filter** (PowerShell-safe): `rg -n "BuildQueueScreen\([^)]*build_context\s*=" game tests` returns 0 hits. Raw `build_context=` hits in `BuildQueueController(...)` / `factory.build_context = ...` / `screen.build_context = ...` / `panel_factory.py` are expected and out of scope.
- [x] Run sharded suite green.

---

## Phase Completion Checklist

When all 4 tasks are checked off:
- [x] F-C-006 flipped to `Status: resolved` in `findings/PROJ-456_findings.md`.
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-456 2` — PASSED.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 3.
- [x] Commit message: `PROJ-456 Phase 2: retire BuildQueueScreen build_context legacy kwarg (F-C-006; 1 prod + 1 test file migrated; controller-API callers out of scope per codex r5)`.
- [x] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
