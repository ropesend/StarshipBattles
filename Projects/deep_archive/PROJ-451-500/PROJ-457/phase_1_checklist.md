# PROJ-457 Phase 1: Extract one responsibility from `build_queue_screen.py` (961 → under 500)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-457 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 0 complete (LOC re-measured; rescope decisions made).
**Review Mode:** standard
**Objective:** Drop `game/ui/screens/build_queue_screen.py` from 961 LOC (or post-PROJ-456 re-measured value) to under the 500-LOC ceiling. Same recipe per phase: read the file, identify a cohesive responsibility, extract into a sibling module, rewire callers, run tests.

**Source-of-truth finding:** F-C-027 entry in [`findings/PROJ-457_findings.md`](findings/PROJ-457_findings.md).

**Codex r4 framing:** "After Job 8 removes the easy shim bulk, do the real structural extractions." This phase is one of three same-recipe extractions.

---

## Tasks

### Task 1.1: Read the file + identify candidate responsibilities [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** none — read-only audit.

- [x] Read `build_queue_screen.py` end-to-end. Identify the cohesive responsibility clusters within the class.
- [x] Common candidates per the F-C-027 finding text: **yard population**, **queue selection**, **drag handling**. The file already has a `build_queue_*` family split (per finding), so the extraction follows the same precedent (e.g. `build_queue_drag_handler.py` already exists per the manifest hint).
- [x] List each candidate cluster: which methods belong to it, which state fields, and the estimated LOC if extracted.
- [x] Pick the cluster with the best (largest LOC out) / (smallest API surface) ratio. Record the choice in `decisions.md`.
- [x] If no single cluster gets the file under 500, the phase becomes multi-extraction — split into Task 1.1a, 1.1b, etc., extracting two clusters in one phase. Codex r4 prefers "one cohesive responsibility per phase" if possible; multi-extraction is acceptable if needed.

### Task 1.2: Create the sibling module [Medium]
**File:** `game/ui/screens/build_queue_<responsibility>.py` (new — exact name decided in Task 1.1)
**Tests:** `tests/unit/ui/screens/test_build_queue_<responsibility>.py` (new)

- [x] Create the new sibling module file with proper docstring, imports, and the extracted class / function definitions.
- [x] Move the chosen cluster's methods + state fields into the new module.
- [x] Expose a narrow API: typically a single class or 1-3 free functions that the screen can call.
- [x] Follow existing naming conventions in the `build_queue_*` family.
- [x] Pattern reference: `docs/02_PATTERNS.md` §32 (Compositional Construction) — if the extracted responsibility is a stable, heavy collaborator, use the composition pattern. Otherwise prefer module-level free functions or a thin helper class.

### Task 1.3: Rewire `build_queue_screen.py` [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py tests/unit/ui/panels/test_build_queue_controller.py tests/integration/ui/build_queue_screen/test_controller_multi_queue.py -q`

- [x] Import the new module's API in `build_queue_screen.py`.
- [x] Replace each call to the old (now-moved) methods with a call to the new module's API.
- [x] Delete the old methods + state fields from `build_queue_screen.py`.
- [x] If the old methods had `self.` accesses, the new module either accepts the screen as a parameter or holds its own state — choose the cleaner API.
- [x] Run targeted tests; expect failures if any test reached into the now-extracted internals — those test sites need Task 1.4's migration.

### Task 1.4: Migrate test reads to the new module's API [Medium]
**Files:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`, `tests/unit/ui/panels/test_build_queue_controller.py`, `tests/integration/ui/build_queue_screen/test_controller_multi_queue.py`, and any others that reach the extracted internals.

- [x] For each test that was reading `screen._<extracted_method>` or `screen._<extracted_state>`, replace with the new module's API.
- [x] Add new dedicated tests for the extracted module: `tests/unit/ui/screens/test_build_queue_<responsibility>.py`. Target: behavior-locking characterization tests for the extracted cluster (input → output assertions; not just "does it instantiate").
- [x] Run each test file individually.

### Task 1.5: Verify LOC + sharded green [Simple]

- [x] (PowerShell-safe) `(Get-Content game/ui/screens/build_queue_screen.py | Measure-Object -Line).Lines` returns < 500. If still over, document in `decisions.md` and either (a) extract a second cluster in this phase or (b) accept the residual overage with a documented "next-touch" note.
- [x] (PowerShell-safe) `(Get-Content game/ui/screens/build_queue_<responsibility>.py | Measure-Object -Line).Lines` returns < 500 (new module respects the same ceiling).
- [x] Run sharded suite green: `python Tools/test_sharded/test_sharded.py`.
- [x] Run targeted tests: `pytest tests/unit/ui/screens/build_queue* tests/unit/ui/panels/build_queue* tests/integration/ui/build_queue_screen/ -q`.

---

## Phase Completion Checklist

When all 5 tasks are checked off:
- [x] F-C-027 status updated in `findings/PROJ-457_findings.md` — `build_queue_screen.py` row flipped to `Status: resolved` with LOC delta.
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-457 1` — PASSED.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 2.
- [x] Commit message: `PROJ-457 Phase 1: extract <responsibility> from build_queue_screen.py (961 -> <FINAL> LOC; F-C-027 partial close)`.
- [x] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
