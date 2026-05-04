# Concurrent-commit contamination — audit trail (PROJ-329A Phase 2)

**Source:** OpenCode review `req_20260504_222600_cac643` (review 3b of the
Wave 1+2+3 execution arc). Findings C1 + C2.

**Date:** 2026-05-04
**Scope:** Two commits on `feat/03c-phase-aware-execution` that bundle work
from PROJ-329A with work from a different project, violating the per-class
commit discipline (D-007 in `Projects/active_projects/PROJ-329A/decisions.md`).

## Background

During the Wave 1 execution batch (5 parallel agents writing tests + 5
parallel agents doing UIWindow retrofits + 1 agent doing strategy_screen
LOC decomposition), agents committed directly to `feat/03c-phase-aware-execution`
without git index serialization. Multiple agents ran `git add` then
`git commit` in overlapping windows; whichever agent reached `git commit`
first absorbed all currently-staged files, regardless of which agent
originally staged them.

This produced 2 cross-project commits:

### Commit `cd7f84b59` — labeled "test(research): characterize ResearchRenderer drawing behavior (PROJ-337)"

Actually contains:
- PROJ-337 `tests/unit/research/test_research_renderer_drawing.py` (NEW, 667 LOC)
- **PROJ-329A Phase 2 Task 2.1 (FoodAllocationEditor) entire refactor:**
  - `game/ui/screens/food_allocation_editor.py` (+89/-55)
  - `tests/fixtures/food_allocation_editor_ui_builder.py` (NEW, 80 LOC)
  - `tests/unit/ui/screens/test_food_allocation_editor.py` (+176)

**Bisect/revert impact:** A bisect that lands on `cd7f84b59` for a PROJ-337
regression would incorrectly implicate FoodAllocationEditor. A revert of
`cd7f84b59` to undo a PROJ-337 issue would also remove the FoodAllocationEditor
refactor.

### Commit `2bbb260f6` — labeled "feat(329A): retrofit PlanetSelectionWindow to two-stage construction (TDD-first)"

Actually contains:
- PROJ-329A Phase 2 Task 2.3 (PlanetSelectionWindow) refactor + fixture + tests (+444 LOC)
- **PROJ-330 Phase 1 (assets) + Phase 4 (selection) entire extractions:**
  - `game/ui/screens/strategy_screen_assets.py` (NEW, 88 LOC)
  - `game/ui/screens/strategy_screen_selection.py` (NEW, 99 LOC)
  - `tests/unit/ui/screens/test_strategy_screen_assets.py` (NEW, 170 LOC)
  - `tests/unit/ui/screens/test_strategy_screen_selection.py` (NEW, 184 LOC)
  - Plus `strategy_screen.py` -145 LOC and `strategy_screen_lifecycle.py` +14
  - Plus `test_strategy_screen.py` +20 / `test_strategy_screen_lifecycle.py` +21

**Bisect/revert impact:** Same problem inverted — a bisect/revert for
PROJ-329A would touch PROJ-330 work, and PROJ-330 has no independent
Phase 1 or Phase 4 commit. `git blame` on `strategy_screen_assets.py`
or `strategy_screen_selection.py` points at a PROJ-329A commit, which
is semantically wrong.

## Disposition

These contaminations are **NOT being rebased away.** Per CLAUDE.md
discipline ("Prefer to create a new commit rather than amending an
existing commit"; "Never run destructive git commands... unless the user
explicitly requests these actions"), rewriting published history is
off-table without explicit user direction. Repo CRLF behavior plus
parallel agent activity makes such rewrites particularly risky.

**The work itself is correct.** Reviewer 3b verified:
- Pattern §33 conformance: PASS for all 3 PROJ-329A Phase 2 classes.
- Behavioral parity for PROJ-330 helper extractions: PASS.
- LOC ceilings: all 8 files < 500.
- Test counts match claims (62 + 11 + 18 + 31).
- No semantic changes disguised as refactors.

## Recommendations for future parallel-agent runs

1. **Use worktree isolation if the harness supports it correctly** — the
   prior worktree harness pinned agents to a stale base commit
   (`60a389f56`) which is why we abandoned worktrees mid-Wave-1 and
   switched to direct-on-branch parallel agents. If the harness is
   fixed, isolation prevents this.
2. **OR serialize commits via a simple lock** — wrap each agent's
   `git add ... && git commit ...` sequence in a process-wide lock
   file (e.g., flock on a coordination file in `AgentCoordination/`).
3. **OR run agents sequentially** — slower but guarantees commit
   attribution. Trade-off depends on parallelism value vs commit-hygiene
   value.
4. **At minimum, instruct each agent to** `git status` **before** `git add`
   **and** `git reset HEAD <unrelated-file>` **if it sees files staged
   that don't belong to its scope.** Several Wave 1 agents did this
   successfully (PROJ-340 explicitly noted using this pattern); others
   didn't.

## See also

- `Projects/active_projects/PROJ-329A/decisions.md` D-007 (per-class commit discipline)
- `Reviews/results/2026-05-04_222601_code_proj-330-proj-329a-phase-2-independent-code-review_req-req_20260504_222600_cac643/report.md` — full review with M1 + M2 findings
- Other Wave 1 agent reports noted similar contamination across PROJ-333 / 337 / 338 / 339 / 340 commits — see individual agent execution reports in their respective project decisions.md files.
