# PROJ-310: Design Document

## Initial Analysis

The 2026-04-26 code review claimed 373 of 555 source files (67%) contain code at 4+ indent levels. **Independent verification (2026-04-26):** actual count is **389 of 563** `.py` files in `game/` = **69.1%**. The user wants a focused review of these.

Deep nesting is a code smell, but not always a bug. Legitimate cases:
- Parsers and serializers (mirror the structure of nested data)
- State machines with many transitions
- Iteration over multidimensional structures (e.g., per-player → per-fleet → per-ship → per-component)

Illegitimate cases:
- Defensive `if x: if x.y: if x.y.z:` chains that should use early-return guards or null-coalescing
- `try / for / if / else` ladders inside event handlers
- "I'll just add one more if-branch here" accretion

The review must distinguish between these so any follow-up refactor targets the illegitimate cases.

## Methodology

### Step 1: Build the AST tool
A small Python script walks `game/` files, parses each into an AST, and computes:
- **Per file:** number of statement nodes at depth ≥ 4 (where depth = nested function/class/control-flow nodes)
- **Per function:** maximum nesting depth, total LOC
- **Per ladder:** the longest single nested chain in the function

Script output: a CSV with columns `file, function, max_depth, total_loc, longest_ladder_kind`.

### Step 2: Rank
Top 30 functions by `max_depth`. Top 30 files by total deep-nesting node count.

### Step 3: Categorize
For each top-30 function, the reviewer classifies the cause:
- **defensive:** chains of `if obj is not None:` etc.
- **try-ladder:** `try` blocks containing more `try` blocks
- **state-machine:** legitimate but possibly tabulatable
- **parser:** legitimate, mirrors data structure
- **loop-stack:** legitimate when iterating multi-level data; smell when each level is pulled inline
- **accretion:** organic growth, no single root cause

### Step 4: Recommend
For each archetype that contains >1 illegitimate case:
- Refactor approach (early-return, extract, table-lookup, polymorphism, ...)
- Estimated scope (number of functions to touch)
- Suggested follow-up project (or roll into PROJ-309 if the file is already in PROJ-309's top-10)

## Architecture

### Why investigate before refactoring
Without categorization, a "fix all the deep nesting" project would mechanically restructure parser/state-machine code that should stay as-is. The investigation surfaces what's worth fixing, what isn't, and how.

### Why this is its own project
The user's directive ("focused review") explicitly asked for the review separately from action. The review's output may seed multiple follow-up projects of varying size. A monolithic "deep nesting cleanup" project would be vague and over-scoped.

### Output deliverable shape
`findings/nesting_review.md` should contain:
1. **Executive summary** (3-5 sentences): how big is the problem, what are the patterns
2. **Quantitative metrics** (top-30 tables for files and functions)
3. **Archetype catalog**: for each archetype, what it looks like + 1-2 concrete examples + verdict (legitimate / refactor)
4. **Recommended follow-up projects**: each sized (S/M/L), each with concrete files-to-touch
5. **What NOT to refactor**: explicit list of legitimate deep nesting that should be left alone

## Dependencies & Risks

1. **Risk: AST tool over-counts (e.g., counts list comprehensions as nested) or under-counts (e.g., misses some nesting forms).**
   **Mitigation:** spot-check 5 files manually after the script runs — does the metric agree with the human read?

2. **Risk: review recommends low-value refactors.**
   "Reduce nesting in `foo.py` from 5 to 4" with no behavior change is busywork.
   **Mitigation:** Step 4 explicitly requires each recommendation to articulate a concrete benefit (readability, testability, or fixing a known bug pattern). Recommendations failing this bar are dropped.

3. **Risk: review duplicates work in PROJ-309.**
   Several top-10 files (race_setup_screen, command_handlers) likely also harbor the worst deep nesting. Decomposition naturally reduces nesting.
   **Mitigation:** Step 4 explicitly notes which recommendations are absorbed by PROJ-309 (no separate project needed) vs. new work.

## Key Patterns to Reuse
- **AST analysis pattern**: similar tools exist for detecting other code smells; reuse structure
- **Investigative-project pattern** (PROJ-87 etc.): a research project produces a design doc; subsequent projects execute. PROJ-310 is the same shape

## Opportunities Discovered
- The CSV output could feed a dashboard tracking deep-nesting trends over time. Out of scope; capture as follow-up.
- Could integrate `radon` (added in PROJ-297) — its complexity metrics correlate with nesting depth. Worth cross-referencing in the review.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
