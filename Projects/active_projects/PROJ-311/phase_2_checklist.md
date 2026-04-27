# Phase 2: Audit baseline

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-311 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Write the script
- [ ] Self-test: run on `game/core/component_state.py` and `game/strategy/data/order_types.py` — manually count annotated functions and confirm script agrees
- [ ] Run on all of `game/` — output to `findings/unannotated.csv`
- [ ] Print the summary; record the per-subsystem coverage in `findings/baseline_summary.md`

**Notes:** Verified prior count: 1408 unannotated. Script should reproduce roughly this number (allow for small differences due to dunder handling).

---

### Task 2.2: Per-subsystem breakdown [Simple]
**File:** `findings/baseline_summary.md`
**Tests:** None.

For each top-level subsystem under `game/`, record:
- Subsystem path (e.g., `game/core/`, `game/simulation/`)
- Total functions
- Annotated / unannotated counts
- Coverage %

- [ ] Compute and save

**Notes:**

---

### Task 2.3: Pick wave order [Simple]
**File:** Update `plan.md` Current State
**Tests:** None.

- [ ] Default order: Core → Simulation → Strategy → AI → UI
- [ ] Confirm by looking at per-subsystem counts. If a subsystem is overwhelmingly large (e.g., UI has 800 unannotated), split it into sub-waves (UI-screens, UI-panels, etc.)
- [ ] Document final wave order in `findings/wave_order.md`

**Notes:**

---

## Phase Completion Checklist
- [ ] Audit script working
- [ ] CSV exists for all of `game/`
- [ ] Per-subsystem baseline documented
- [ ] Wave order set
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3)
