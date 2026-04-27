# Phase 1: Quantify and rank deeply-nested code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-310 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Build an AST-based tool that measures nesting depth per file/function. Produce a CSV and top-30 rankings.

---

## Tasks

### Task 1.1: Write the AST analysis tool [Medium]
**File:** `Projects/active_projects/PROJ-310/findings/nesting_analysis.py` (NEW)
**Tests:** Self-test on 1-2 known files

The tool should:
- Walk `game/**/*.py` (skip `tests/`)
- Parse each into an `ast.Module`
- For each `FunctionDef` / `AsyncFunctionDef`, compute:
  - `max_depth` = deepest control-flow + function nesting depth (count `If`, `For`, `While`, `Try`, `With`, `FunctionDef`, `AsyncFunctionDef`, `ClassDef` nodes on the path from the function root to its deepest leaf)
  - `total_loc` = function body line count
  - `longest_ladder_kind` = the kinds of nodes in the deepest path (e.g., `for→if→try→if`)
- Emit CSV with columns: `file,function,max_depth,total_loc,longest_ladder_kind`

- [ ] Write the script
- [ ] Run on 2 known files (one short, one big like `command_handlers.py`) and verify the metric matches a manual read
- [ ] Run on all of `game/` — output to `findings/nesting_metrics.csv`

**Notes:**

---

### Task 1.2: Build the rankings [Simple]
**File:** Two outputs — `findings/top30_by_function.md` and `findings/top30_by_file.md`
**Tests:** None.

- [ ] Sort `findings/nesting_metrics.csv` by `max_depth` descending; take top 30 → write to `findings/top30_by_function.md`
- [ ] Aggregate per file (sum of `max(0, max_depth - 3)` across functions in the file); take top 30 → write to `findings/top30_by_file.md`
- [ ] Spot-check the top 5 in each — does the file/function actually look bad on a quick read?

**Notes:**

---

### Task 1.3: Cross-reference with `radon` [Simple]
**File:** `findings/radon_complexity.txt`
**Tests:** None.

- [ ] Run `radon cc game/ -a -nb -j > findings/radon_complexity.txt` (or similar — radon outputs per-function complexity)
- [ ] Compare the worst-complexity functions to the worst-nesting functions — is there overlap?
- [ ] Note in the review whether complexity and nesting agree (high correlation expected)

**Notes:**

---

## Phase Completion Checklist
- [ ] Tool written and validated
- [ ] CSV exists for all of `game/`
- [ ] Top-30 rankings exist for both functions and files
- [ ] Radon cross-reference complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2)
