# Handoff: PROJ-291 — Phase 1 (C1 — Treasury Total includes Population Upkeep)

Resume **PROJ-291** at **Phase 1**. PROJ-291 is the gate that blocks PROJ-283..290 sign-off — three confirmed Critical bugs from a dual cross-project audit must land before the 8 projects can move from `Awaiting Verification` → `Archived`. PROJ-292 is the parallel sibling for High/Major/Minor cleanup; do NOT touch its work in this session.

## Orientation (read BEFORE touching the project plan)

PROJ-291 is small in code but architecturally consequential — Phase 2 reverses an explicit deferral made in PROJ-287's decisions.md. Load context first.

### 1. Audit provenance (read these THREE FIRST so you understand why this project exists)

- [`Projects/active_projects/PROJ-291/findings/INDEX.md`](Projects/active_projects/PROJ-291/findings/INDEX.md) — directs you to the dual audit + impartial subagent verdicts.
- [`Projects/active_projects/PROJ-291/findings/SUMMARY.md`](Projects/active_projects/PROJ-291/findings/SUMMARY.md) — the prior audit's executive summary; lists C1 / C2 / C3 with file:line locations.
- [`Projects/active_projects/PROJ-291/findings/pipeline_reachability_skeptic.md`](Projects/active_projects/PROJ-291/findings/pipeline_reachability_skeptic.md) — the report that caught C1 (the bug Phase 1 fixes).

### 2. Foundation docs (always read these before any work)

- `docs/README.md` — doc index.
- `docs/01_ARCHITECTURE.md` — layer rules. Critical for Phase 2: the `IRaceRegistry` protocol lives in `game/core/protocols.py` (cross-layer); engines may consume it.
- `docs/02_PATTERNS.md` — Pattern 2 (Protocol + TypeGuard), Pattern 3 (Dependency Injection). Phase 2 mirrors PROJ-285's optional-registry pattern.
- `docs/03_CONVENTIONS.md` — file org + test conventions.
- `CLAUDE.md` — the three non-negotiable rules. **Rule 1 (TDD)** is enforced explicitly in every phase checklist's Task ordering.

### 3. Task-specific docs

- `docs/systems/strategy_layer.md` § Demographics Loop — the engine consumers Phase 2 retrofits.
- `docs/04_SERVICES.md` § Race Registry (PROJ-287) — the interface Phase 2 wires into the engines.

### 4. Pattern-source code (read for context, even if you won't modify it)

- [`game/strategy/engine/harvesting_engine.py`](game/strategy/engine/harvesting_engine.py) — Phase 2's reference pattern. Already accepts `race_registry: Optional[Any] = None` with a None-fallback path that returns `multiplier=1.0`. Mirror this exact shape for `HappinessEngine` + `PopulationEngine`.
- [`game/strategy/engine/production_engine.py`](game/strategy/engine/production_engine.py) — same pattern; same mirror target.
- [`Projects/active_projects/PROJ-285/decisions.md`](Projects/active_projects/PROJ-285/decisions.md) — explains why the pattern shape is what it is (preserve 850+ pre-PROJ-285 MagicMock tests).

### 5. The files PROJ-291 modifies

**Phase 1 (C1):**
- [`game/strategy/engine/empire_economy_calculator.py:130-164`](game/strategy/engine/empire_economy_calculator.py#L130-L164) — Phase 1 Task 1.2 adds ONE line at line 147-150 (the `total_expenses[r]` summation) to include `+ snapshot.total_population_upkeep.get(r, 0.0)`.
- [`tests/unit/strategy/engine/test_empire_economy_calculator.py`](tests/unit/strategy/engine/test_empire_economy_calculator.py) — Phase 1 Task 1.1 adds `TestTreasuryTotalIncludesUpkeep` (write FIRST, watch it fail, then apply Task 1.2).
- `tests/integration/strategy/test_treasury_panel_e2e.py` (NEW) — Phase 1 Task 1.3 writes the e2e pin (closes prior-audit M3).

**Phase 2 (C3):**
- [`game/strategy/engine/happiness_engine.py:77-95`](game/strategy/engine/happiness_engine.py#L77-L95) — the dual-return on lines 93-95 is the bug (`return race_config` then `return race_config` regardless of mismatch).
- [`game/strategy/engine/population_engine.py:146-180`](game/strategy/engine/population_engine.py#L146-L180) — same shape.
- [`game/strategy/engine/turn_engine.py`](game/strategy/engine/turn_engine.py) — Phase 2 Task 2.6 wires the registry through to both engines (mirror how PROJ-285 already wires it for HarvestingEngine + ProductionEngine; grep for `HarvestingEngine(` in this file).

**Phase 3 (C2):**
- [`game/ui/screens/food_allocation_editor.py:258`](game/ui/screens/food_allocation_editor.py#L258) — the runtime crash site (reads deleted `EconomyConfig.food_per_pop_per_turn`).
- [`tests/unit/ui/screens/test_food_allocation_editor.py`](tests/unit/ui/screens/test_food_allocation_editor.py) — 13 broken fixtures all on `EconomyConfig(population_food_resource=..., food_per_pop_per_turn=...)`. Phase 3 Task 3.2 migrates them to `EconomyConfig(population_consumption={...})`.

## Only now: read the project files

1. [`Projects/active_projects/PROJ-291/design.md`](Projects/active_projects/PROJ-291/design.md) — § Architecture has the exact code shape for each fix.
2. [`Projects/active_projects/PROJ-291/decisions.md`](Projects/active_projects/PROJ-291/decisions.md) — full decisions log, including user-confirmed Q1 (registry retrofit) + Q2 (editor migration).
3. [`Projects/active_projects/PROJ-291/plan.md`](Projects/active_projects/PROJ-291/plan.md) § **Current State** — authoritative handoff context.
4. [`Projects/active_projects/PROJ-291/phase_1_checklist.md`](Projects/active_projects/PROJ-291/phase_1_checklist.md) — starts here.
5. [`Projects/active_projects/PROJ-291/manifest.md`](Projects/active_projects/PROJ-291/manifest.md) — files this project touches + cross-project overlap with PROJ-292.

## First action

Open `phase_1_checklist.md`. The literal next unchecked item is:

> **Task 1.1: Write the failing unit test [Simple]**
> Add `TestTreasuryTotalIncludesUpkeep` to `tests/unit/strategy/engine/test_empire_economy_calculator.py`. Construct an empire with 2 colonies × 2 species + non-zero population + populated `EconomyConfig(population_consumption={"organics": 0.001, "metals": 0.0001})`. Call `EmpireEconomyCalculator(...).calculate(empire)`. Assert `snapshot.total_expenses[r] == tributes + ships + complexes + population_upkeep` for every resource. Run the test — confirm it FAILS (the bug is at lines 147-150, the upkeep term is missing).

TDD ordering for the project:
1. Phase 1 (C1) — the smallest piece. One line of code + 2 tests. Establishes the rhythm.
2. Phase 2 (C3) — the largest piece. Engine retrofit. Six tasks: read the reference pattern; write failing tests for HappinessEngine + PopulationEngine; implement both; wire turn_engine.py.
3. Phase 3 (C2) — UI editor migration. Six tasks: read editor; rewrite preview function; migrate 13 fixtures; rewrite UI rows; retire shim if no callers remain.
4. Phase 4 — docs + sharded suite + sign-off handoff.

## Watchouts

1. **Phase 2 reverses PROJ-287 decisions.md line 16.** That deferral was made before multi-species colonies were a reachable game state. Phase 4 Task 4.2 documents the reversal in PROJ-287's decisions.md as a forward-link — don't forget it.

2. **Mirror PROJ-285's exact pattern.** Don't invent a new shape for the optional `race_registry` kwarg. Read `harvesting_engine.py` first; the shape is `race_registry: Optional[Any] = None` + None-fallback.

3. **Phase 2's third behaviour change.** When `race_registry is None` AND `race_id != empire.race_config.race_id`, the legacy fallback now returns `None` instead of returning the wrong `race_config`. The empire's `process_*` loops already have `if race_config is None: return` early-outs, so the species is gracefully skipped. Pin this with Test 3 in Tasks 2.2 + 2.3.

4. **Phase 3's editor row UI is the only place pygame_gui rendering touches the project.** Manual smoke is in Phase 4 Task 4.5 — deferred to user. Don't try to validate UI rendering yourself; trust the unit tests for the data path.

5. **PROJ-292 file overlap = `empire_economy_calculator.py`.** PROJ-291 Phase 1 modifies this file; PROJ-292 Phase 2 wraps it in a service facade. **Sequencing: PROJ-291 Phase 1 lands first.** PROJ-292 must verify Phase 1 is complete before starting its Phase 2.

6. **Pre-existing flake.** `tests/unit/quickstart/test_quickstart_builder.py::test_copy_designs_without_themes_preserves_original` is a long-standing theme-bleed flake. Not a PROJ-291 regression. Phase 4 Task 4.4 checks the diff against baseline (~14 known failures: 13 food-editor + 1 flake) and confirms the 13 food-editor failures are gone post-Phase 3.

7. **Save files are disposable per CLAUDE.md.** No backwards-compat shim for the `food_per_pop_per_turn` field. The editor migration is the proper fix per Q2 user choice.

8. **Context budget.** PROJ-291 is 4 phases × ~15-20 minutes each. Likely fits in one session; if not, hand off after Phase 2 (the largest phase).

9. **`Temp Review Docs/` cleanup.** Phase 4 Task 4.1 COPIED the audit reports to `findings/` (already done in scaffolding). The originals stay until user verifies the archive — don't delete `Temp Review Docs/` proactively.

## Protocol

Follow `Projects/protocols/03a_continue_working.md`. Phase completion is a checkpoint, not an exit. Run `python Projects/scripts/validate_phase.py PROJ-291 [phase]` before stopping.

Final test command for the project: `python Tools/test_sharded/test_sharded.py` — expect ~15080 tests, ~1 known failure (the long-standing flake; net 13 fewer failures than baseline thanks to the Phase 3 fixture migration).
