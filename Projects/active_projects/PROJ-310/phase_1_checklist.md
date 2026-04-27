# Phase 1: Quantify and rank deeply-nested code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-310 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Write the script
- [x] Run on 2 known files (one short, one big like `command_handlers.py`) and verify the metric matches a manual read
- [x] Run on all of `game/` — output to `findings/nesting_metrics.csv`

**Notes:**
- Sanity check: `component_state.py` reports max depth 0 on every method (matches manual read — file is all flat dataclass methods). `command_handlers.py` reports max depth 3 on `add_move_order_if_needed`; verified against the source — `if start_hex is None` → `for order in reversed(...)` → `if order.type == OrderType.MOVE` is exactly the path the AST identified.
- The tool emits **two** depth metrics: `max_depth` (raw AST count, where every `elif` adds +1) and `visual_depth` (treats elif chains as a single level, matching how a human reads indentation). This is critical because Python's AST represents `elif X:` as `If(orelse=[If(...)])`, so a flat 12-way dispatch shows AST depth 12 but visual depth 1. Both are reported in the CSV; the rankings split into two files (`top30_by_function.md` for AST, `top30_by_visual_depth.md` for visual).
- Headline numbers: 5313 functions analyzed; **AST depth ≥ 4 = 297 funcs (5.6%)**; **visual depth ≥ 4 = 192 funcs (3.6%)**. 178 of 491 files (36.3%) contain at least one deep function. (The earlier "69.1% of files" figure was a regex-on-indentation count that fired on every nested `for x in ...:` pair that included an `if` clause — the AST signal is sharper.)

---

### Task 1.2: Build the rankings [Simple]
**File:** Two outputs — `findings/top30_by_function.md` and `findings/top30_by_file.md`
**Tests:** None.

- [x] Sort `findings/nesting_metrics.csv` by `max_depth` descending; take top 30 → write to `findings/top30_by_function.md`
- [x] Aggregate per file (sum of `max(0, max_depth - 3)` across functions in the file); take top 30 → write to `findings/top30_by_file.md`
- [x] Spot-check the top 5 in each — does the file/function actually look bad on a quick read?
- [x] Bonus: top 30 by **visual** depth → `findings/top30_by_visual_depth.md`

**Notes:**
- Spot-check (top 5 by AST): all five are 12+-way `if/elif/elif/...` button/event dispatch ladders in `game/ui/screens/`. Visually flat (1 indent), but cyclomatic complexity is high (CC 25-52 per radon). They are real maintenance smells but the right fix is dispatch-table not de-nesting.
- Spot-check (top 5 by visual): `LayerPanel.rebuild` (depth 7, 175 LOC, `for→if→for→if→for→if→if`) — confirmed a genuinely deep nested-loop. `_collect_effects` (depth 6, 5-deep `for` ladder) — confirmed iteration over per-system → per-region → per-effect-source. These are the real targets.

---

### Task 1.3: Cross-reference with `radon` [Simple]
**File:** `findings/radon_complexity.txt`
**Tests:** None.

- [x] Run `radon cc game/ -a -nb -j > findings/radon_complexity.txt`
- [x] Compare the worst-complexity functions to the worst-nesting functions — is there overlap?
- [x] Note in the review whether complexity and nesting agree (high correlation expected)

**Notes:**
- Top-30 cyclomatic-complexity (`findings/radon_top30.txt`) overlaps heavily with top-30 nesting. `RaceSetupScreen.process_event` (cc=52, AST depth 9), `BattleSetupInputHandler._handle_button` (cc=37, AST depth 14), `format_planet_info` (cc=28, AST depth 7), `_collect_effects` (cc=28, visual depth 6), `_format_orders` (cc=28, AST depth 15) all appear in both lists. Strong agreement: when a function shows up here it earns its place via both metrics. The overlap argues that any of the recommendations would land hits worth measuring.

---

## Phase Completion Checklist
- [x] Tool written and validated
- [x] CSV exists for all of `game/`
- [x] Top-30 rankings exist for both functions and files
- [x] Radon cross-reference complete
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2)
