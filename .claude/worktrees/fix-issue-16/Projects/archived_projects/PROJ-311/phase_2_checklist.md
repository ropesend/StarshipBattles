# Phase 2: Audit baseline

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-311 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Build an AST audit script that measures return-annotation coverage. Establish a per-subsystem baseline so progress can be measured.

**Prerequisites:** Phase 1 complete — convention is documented.

---

## Tasks

### Task 2.1: Build the audit script [Simple]
**File:** `Projects/active_projects/PROJ-311/findings/annotation_audit.py` (NEW)
**Tests:** Self-test on 1-2 known files.

The script should:
- Walk `game/**/*.py` (skip `tests/`)
- For each `FunctionDef` / `AsyncFunctionDef`, record:
  - file (relative to repo root)
  - function name (with class prefix if a method, e.g., `MyClass.foo`)
  - has-return-annotation (bool — `node.returns is not None`)
  - is-dunder (bool — name like `__foo__`)
  - is-public (bool — first char isn't `_`)
- Output CSV with columns: `file,function,has_return_annotation,is_dunder,is_public`
- Print summary: total, annotated, unannotated, coverage %, breakdown by `game/<subsystem>/`

- [x] Write the script
- [x] Self-test: run on `game/core/component_state.py` and `game/strategy/data/order_types.py` — manually count annotated functions and confirm script agrees
- [x] Run on all of `game/` — output to `findings/unannotated.csv`
- [x] Print the summary; record the per-subsystem coverage in `findings/baseline_summary.md`

**Notes:** Verified prior count: 1408 unannotated. Script should reproduce roughly this number (allow for small differences due to dunder handling).

Self-test results:
- `game/core/component_state.py`: 5 functions, 1 dunder, 4 non-dunder all annotated → 100%. Manual count agrees.
- `game/strategy/data/order_types.py`: 4 functions, 2 dunder, 2 non-dunder all annotated → 100%. Manual count agrees.
- `game/ui/screens/race_setup_screen.py` (larger sanity): 51 total, 1 dunder (`__init__`, unannotated), 50 non-dunder of which 12 annotated → 24% cov. Grep confirmed 12 lines with `->` arrow at def position; matches.

Full-game run: **5349 total / 416 dunder / 4933 non-dunder / 3525 annotated / 1408 unannotated → 71.46% coverage** — exact match to the design.md target figure.

Outputs:
- `findings/inventory.csv` (5349 rows, full inventory)
- `findings/unannotated.csv` (1408 rows, the Phase 3 backfill targets)
- `findings/audit_output.txt` (captured console)
- `findings/baseline_summary.md` (per-subsystem table + UI subdir breakdown)
- `findings/_breakdown.py` (helper that produced the UI/other-bucket detail; kept for reproducibility)

---

### Task 2.2: Per-subsystem breakdown [Simple]
**File:** `findings/baseline_summary.md`
**Tests:** None.

For each top-level subsystem under `game/`, record:
- Subsystem path (e.g., `game/core/`, `game/simulation/`)
- Total functions
- Annotated / unannotated counts
- Coverage %

- [x] Compute and save

**Notes:** Saved to `findings/baseline_summary.md`. Includes the headline numbers, per-subsystem table, a UI-subdir breakdown (because UI dominates), and the 'other' bucket detail.

---

### Task 2.3: Pick wave order [Simple]
**File:** Update `plan.md` Current State
**Tests:** None.

- [x] Default order: Core → Simulation → Strategy → AI → UI
- [x] Confirm by looking at per-subsystem counts. If a subsystem is overwhelmingly large (e.g., UI has 800 unannotated), split it into sub-waves (UI-screens, UI-panels, etc.)
- [x] Document final wave order in `findings/wave_order.md`

**Notes:** UI did need splitting — `game/ui/screens/` alone has 966 unannotated. Final 6-wave plan documented in `findings/wave_order.md`:
- **Wave A** = `game/core/` + `game/ai/` + the 'other' bucket (game/<top-level>, assets, engine) — **88 functions**
- **Wave B** = `game/simulation/` — **109 functions**
- **Wave C** = `game/strategy/` — **57 functions**
- **Wave D1** = `game/ui/` minus screens — **188 functions**
- **Wave D2** = `game/ui/screens/` first half (alphabetical) — **~480 functions**
- **Wave D3** = `game/ui/screens/` second half (alphabetical) — **~480 functions**

AI is folded into A (only 11 unann; not worth a separate slot). Total reconstructs to ~1402, matching the 1408 audit total within rounding from the alphabetical split between D2 and D3.

---

## Phase Completion Checklist
- [x] Audit script working
- [x] CSV exists for all of `game/`
- [x] Per-subsystem baseline documented
- [x] Wave order set
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3)
