# PROJ-309: Design Document

## Initial Analysis

The user's directive: "take the top 10 files and break them down in a way that makes them difficult to grow."

A 1500-line file is hard to navigate, hard to test in isolation, and gravitationally pulls more code into itself ("the function I'm adding is similar to one already in this file, so I'll add it here"). Breaking files into smaller, single-responsibility modules creates structural pressure against accretion.

### Verified target list (2026-04-26)
The top-10 by `wc -l` of `game/**/*.py`:
1. race_setup_screen.py — 1588
2. strategy_renderer.py — 1205
3. test_lab/renderer.py — 1193
4. core/protocols.py — 1087
5. command_handlers.py — 1072
6. test_lab/test_run_details.py — 957
7. strategy_session_facade.py — 922
8. workshop_viewmodel.py — 873
9. app.py — 849
10. strategy_window_manager.py — 817

## Architecture

### Pattern: Public API stability
Each top-10 file is imported by many callers. A naive split into N new modules requires updating every caller. To minimize churn:

- **Option A — re-export shim:** the original file becomes a thin module that re-exports from the new sub-modules. Callers import unchanged. *Risk: re-exports can become a graveyard if not actively used.*
- **Option B — caller migration:** new modules expose a clean API; every caller is updated to import from the new locations. *Risk: large diff surface; merge conflicts likely.*

**Choice: per-file basis, decided in Phase 2.** For files with few callers (`app.py`), Option B is fine. For files with hundreds of callers (`core/protocols.py`), Option A may be necessary. The Phase-2 design step makes this call per file.

### Pattern: Single Responsibility decomposition
The decomposition direction matters. Bad split: "first half / second half" of a file. Good split: cohesive sub-modules where each piece has one reason to change.

For each file, Phase 2 produces a per-file design document at `findings/<file>_decomposition.md` describing:
- The current module's responsibilities (often >5 distinct ones)
- Proposed sub-modules and what each owns
- Public API surface (which symbols stay top-level)
- Caller-update strategy (Option A or B)
- Test plan

### Pattern: System Migration Policy applies
Once a file is decomposed:
- If Option A (re-export shim): the shim is a transitional artifact. Schedule its removal in a follow-up project after enough caller migrations land. Do NOT keep shims indefinitely (per Migration Policy).
- If Option B (full migration): no graveyard — original file is deleted in the same commit.

### Per-file initial sketches

These are starting points for Phase-2 design, NOT final decisions:

**1. `race_setup_screen.py` (1588)**
- Probable sub-modules: `race_setup/genome_panel.py`, `race_setup/traits_panel.py`, `race_setup/preview_panel.py`, `race_setup/controls_panel.py`, `race_setup_screen.py` (orchestrator)
- Looks like a god-screen with 4-5 logical tabs/sections

**2. `strategy_renderer.py` (1205)**
- Probable sub-modules per render layer: `strategy_render/background.py`, `.../planets.py`, `.../fleets.py`, `.../overlay.py`, `.../hud.py`, `strategy_renderer.py` (composer)

**3. `test_lab/renderer.py` (1193)**
- Probably parallel to strategy_renderer.py — split by render concern

**4. `core/protocols.py` (1087)**
- Currently a single mega-file containing all interface protocols. Split by domain: `core/protocols/combat.py`, `core/protocols/strategy.py`, `core/protocols/ai.py`, `core/protocols/ui.py`, `core/protocols/registry.py` (re-export from `core/protocols/__init__.py`)
- Heavily imported — Option A (re-export) is mandatory here. Mirror the package layout used elsewhere

**5. `command_handlers.py` (1072)**
- Currently has many handler classes in one file. Split: `strategy/engine/handlers/build_order.py`, `.../fleet_orders.py`, `.../planet_orders.py`, `.../research.py`, etc. Re-export from `command_handlers.py` for caller stability

**6. `test_lab/test_run_details.py` (957)**
- Likely a UI screen with sub-panels — split per panel

**7. `strategy_session_facade.py` (922)**
- Facade aggregating many sub-domain facades. Split into per-domain slices and have the public facade compose them: `facade/fleet_slice.py`, `facade/planet_slice.py`, etc.

**8. `workshop_viewmodel.py` (873)**
- View-state + command handling + validation likely entangled. Split by concern

**9. `app.py` (849)**
- Bootstrap + main loop + screen management. Three obvious sub-concerns

**10. `strategy_window_manager.py` (817)**
- Window lifecycle + event routing. Two obvious sub-concerns

## Dependencies & Risks

1. **Risk: split introduces import cycles.**
   When a god-file is split, new modules sometimes need to reference each other.
   **Mitigation:** Phase-2 design step explicitly checks for cycles. Resolve via dependency inversion if needed (define a protocol in a third module).

2. **Risk: tests break en masse because they imported via paths that changed.**
   **Mitigation:** Option A (re-export shim) preserves import paths, eliminating this risk. For Option B, run targeted tests after each migrated caller.

3. **Risk: PROJ-309 fights with PROJ-298 / PROJ-306 if those touch the same files.**
   `command_handlers.py` was just touched by PROJ-298. `battle_runner.py` and the strategy facade are touched by PROJ-306.
   **Mitigation:** Sequence — PROJ-309 starts AFTER PROJ-298 and PROJ-306 land. Update plan.md Current State if those projects shift.

4. **Risk: large refactor introduces subtle behavior bugs.**
   Splitting code paths can change initialization order, side effects, etc.
   **Mitigation:** Each sub-phase (one file at a time) ends with full sharded suite. If suite drops below 15389, the split is faulty — investigate before moving on.

5. **Risk: 10 separate refactors take months.**
   This is genuinely a multi-month project if done seriously.
   **Mitigation:** Phase 3 has 10 sub-tasks (one per file). They can be sequenced individually; the project doesn't need to land in one PR. Track each sub-phase's status in the Phase 3 checklist.

## Key Patterns to Reuse
- **PROJ-87 / PROJ-86 / PROJ-88 / PROJ-89** (Facade/delegate decomposition pattern, archived) — these were the original god-class decompositions. Read their design.md files for proven patterns.
- **Re-export shim pattern** — used in `commands.py` (now-deleted alias declarations), `formula_system.py` (now-deleted shim). Same shape but for a whole module's API surface.

## Opportunities Discovered
- After all 10 files are split, run `radon` (added in PROJ-297) to confirm the cyclomatic-complexity distribution improved.
- A `Tools/check_file_size.py` script for CI: fail (or warn) on any `game/**/*.py` over 500 LOC. Out of scope for this project; capture as follow-up.
- The 500-LOC convention will, over time, cause the other 52 files >500 LOC to be split organically as they're touched.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
