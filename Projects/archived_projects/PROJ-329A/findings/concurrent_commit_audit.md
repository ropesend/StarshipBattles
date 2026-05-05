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

This produced 4 cross-project commits:

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

### Commit `ddfec64e0` — labeled "test(PROJ-333): add FleetMovementEngine characterization tests"

Actually contains:
- PROJ-333 `tests/unit/strategy/fleet_movement_engine/test_characterization.py` (NEW, 223 LOC)
- **PROJ-329B `EmpirePanelWindow` Pattern §33 retrofit:**
  - `game/ui/screens/empire_panel_window.py` (+49/-12)
  - `tests/fixtures/empire_panel_window_ui_builder.py` (NEW, 79 LOC)
  - `tests/unit/ui/screens/test_empire_panel_window.py` (NEW, 190 LOC)

**Bisect/revert impact:** A bisect that lands on `ddfec64e0` for a PROJ-333
fleet-movement-engine regression would incorrectly implicate
EmpirePanelWindow's two-stage construction. A revert of `ddfec64e0` to
undo a PROJ-333 issue would also remove the EmpirePanelWindow retrofit
and its fixture/tests. `git blame` on `empire_panel_window.py`'s
two-stage `__init__` lines points at a PROJ-333-labeled commit —
semantically wrong.

### Commit `9d16524f1` — labeled "test(PROJ-333): add ProductionSpawner characterization tests"

Actually contains:
- PROJ-333 `tests/unit/strategy/engine/test_production_spawner.py` (NEW, 269 LOC)
- **PROJ-329C `PlanetAbilitiesWindow` decomposition + Pattern §33 retrofit:**
  - `game/ui/screens/planet_abilities_controller.py` (NEW, 217 LOC) — extracted controller
  - `game/ui/screens/planet_abilities_window.py` (+363/-229) — sweeping decomposition
  - `tests/fixtures/planet_abilities_window_ui_builder.py` (NEW, 93 LOC)
  - `tests/unit/ui/screens/test_planet_abilities_window_lifecycle.py` (+42 net)

**Bisect/revert impact:** Largest contamination of the four — `9d16524f1`
bundles a 580+ LOC PROJ-329C decomposition (introducing a new production
file, `planet_abilities_controller.py`) with PROJ-333 characterization
tests. A bisect that lands on `9d16524f1` for a PROJ-333 production-spawner
regression would incorrectly implicate the PlanetAbilitiesWindow split.
A revert would delete `planet_abilities_controller.py` entirely and
revert 229 LOC of `planet_abilities_window.py` simplification. `git blame`
on the new controller file points at a PROJ-333-labeled commit —
semantically wrong, and the controller's existence is not even hinted at
in the labeled commit message.

## Disposition

All 4 contaminations are **NOT being rebased away.** Per CLAUDE.md
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

### Update 2026-05-04 — PROJ-343..348 closeout arc parallel run (3 more contaminations)

A second parallel-agent run executed PROJ-344..347 simultaneously after PROJ-343 closed. Three more cross-project commits resulted, even with explicit anti-contamination guidance in every agent prompt (`git status --short` before each `git add`, explicit file-name staging, `git reset HEAD <file>` if other agents' work appears staged):

#### Commit `a1025dd32` — labeled "fix(planet-list-window): add virtual_table placeholder for Pattern §33 bypass safety (PROJ-347 T4.1b)"

Actually contains:
- `tests/unit/ui/panels/test_race_identity_panel.py` (PROJ-346 vacuous-test rewrite — wrong project)
- ZERO PROJ-347 production changes — the intended `planet_list_window.py` placeholder was missed entirely and re-committed at `c4c228954` ("retry").

#### Commit `5ace65b24` — labeled "fix(empire-panel-window): keep Stage 1 pure under bypass — defer icon loading (PROJ-347 T4.4)"

Actually contains:
- `game/ui/screens/empire_panel_window.py` (PROJ-347 T4.4) ✓
- `tests/unit/ui/screens/test_empire_panel_window.py` (PROJ-347 T4.4 test) ✓
- **`tests/unit/ui/effects/test_hit_effects.py` (PROJ-346 PROJ-331 work — contamination)**

#### Commit `085136515` — labeled "test(PROJ-346): replace pygame_gui-only kill assertion with grid-state pin"

Per agent PROJ-344's self-report this commit absorbed PROJ-344's `Projects/projects_index.md` chore-update. `git show --stat` shows only `test_modifier_impact_grid.py` — the index update landed via a different commit. Attribution functional but tracing-unclear.

### Disposition (unchanged)

Per original disposition: contaminations not rebased. Work itself correct; commit attribution off. Updated count: **5 contaminated commits total** across two parallel runs (`cd7f84b59`, `2bbb260f6` from Wave 1; `a1025dd32`, `5ace65b24`, `085136515` from PROJ-343..348 closeout).

### Recommendation reinforcement (2026-05-04)

The 2026-05-04 closeout parallel run included explicit anti-contamination guidance in every agent prompt. Three contaminations occurred anyway. Conclusion: **agent-side discipline alone is insufficient** to prevent the race between `git add` and `git commit -m` when multiple processes share the same index. Stronger mechanisms required:

1. **Worktree isolation** — needs the harness fix from the original 2026-05-04 disposition; status unknown.
2. **Process-wide commit lock** — flock on a shared coordination file.
3. **Sequential execution** — slower but guarantees attribution.

## See also

- `Projects/active_projects/PROJ-329A/decisions.md` D-007 (per-class commit discipline)
- `Reviews/results/2026-05-04_222601_code_proj-330-proj-329a-phase-2-independent-code-review_req-req_20260504_222600_cac643/report.md` — full review with M1 + M2 findings
- Other Wave 1 agent reports noted similar contamination across PROJ-333 / 337 / 338 / 339 / 340 commits — see individual agent execution reports in their respective project decisions.md files.
