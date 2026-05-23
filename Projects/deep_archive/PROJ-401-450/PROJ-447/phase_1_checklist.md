# PROJ-447 Phase 1: Docs drift cleanup (text-only, no code risk)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-447 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Stop `docs/` from lying about current behavior. Five maintainer-facing documents name deleted classes (`DesignLibrary`, `_ACTIVATABLE_ABILITIES`) or instruct edits to files that no longer exist. Maintainers following these recipes will hit `ImportError` or reintroduce regressions. Phase 1 = pure text edits; no code change; zero test risk.

**Cross-bucket file-ownership rule:** Only edit `docs/`. No code; no tests. (Other agents may be working in `game/` directories in parallel.)

**Source-of-truth findings:** [`findings/bucket_d_simulation_ai_research_engine_docs_scan.md`](findings/bucket_d_simulation_ai_research_engine_docs_scan.md) — F-D-004 (codex seed), F-D-005, F-D-006, F-D-007, F-D-008.

---

## Tasks

### Task 1.1: F-D-004 — Fix _ACTIVATABLE_ABILITIES recipe (codex seed) [Simple]
**File:** `docs/systems/ability_reference.md:554`

- [x] Read the existing recipe step (lines around 554): "Add persistent energy handling to `_ACTIVATABLE_ABILITIES` in `game/strategy/engine/planet_energy_engine.py`"
- [x] Read the correct phrasing at `docs/guides/adding_abilities.md:416` — that doc has the up-to-date recipe
- [x] Read the dead-list comment confirmation at `game/strategy/engine/planet_energy_engine.py:92` (`_ACTIVATABLE_ABILITIES` is deleted) and `docs/systems/strategy_layer.md:697, :717` (correct replacement path documented)
- [x] **GREEN**: Replace the bullet with: "Register the ability in `game/strategy/services/ability_metadata.py` with an `EnergyFacet(drains_energy=True, ...)`; the PROJ-429 unified registry is the activation-discovery surface and `ability_drains_energy(name)` / `abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)` are the consumer queries." Mirror `docs/guides/adding_abilities.md:416` phrasing exactly.
- [x] No test change.

### Task 1.2: F-D-005 — Fix design_library.py citations in error-handling doc [Simple]
**File:** `docs/05_ERROR_HANDLING.md:17` (cross-reference list) + `:335` (pytest command)

- [x] Line 17: change cross-ref from "`game/strategy/systems/design_library.py`: `DesignLoadResult` result-object pattern" to "`game/strategy/systems/design_repository.py`: `DesignLoadResult` result-object pattern" (the class moved during PROJ-434)
- [x] Line 335: the pytest command `pytest tests/unit/strategy/design_library/test_design_load_result.py` references a directory that doesn't exist. Locate the active test file: `git grep -n "DesignLoadResult\|class DesignLoadResult" tests/` to find the current location. Update the pytest command, or drop the targeted reference if no direct test file remains.
- [x] No test change.

### Task 1.3: F-D-006 — Fix design_library.py row in production_system.md [Simple]
**File:** `docs/systems/production_system.md:553`

- [x] Find the table row: `| Design library | game/strategy/systems/design_library.py |`
- [x] **GREEN**: Replace with two rows (or one combined row):
  - `| Design repository (engine-internal) | game/strategy/systems/design_repository.py |`
  - `| Design catalog (workshop / UI-facing) | game/strategy/systems/design_catalog.py |`

### Task 1.4: F-D-007 — Fix DesignLibrary mention in strategy_layer.md table [Simple]
**File:** `docs/systems/strategy_layer.md:32`

- [x] Find: `facade_state` row mentioning "UI collaborators (`DesignLibrary`, etc.)"
- [x] **GREEN**: Replace `DesignLibrary` with `DesignCatalog` in the parenthetical

### Task 1.5: F-D-008 — Fix PlanetaryFacility constructor example mutable default [Simple]
**File:** `docs/systems/production_system.md:50-61`

- [x] Find the `PlanetaryFacility(...)` constructor example with `consumable_levels: dict[str, float] = {}`
- [x] **GREEN**: Either drop the default value from the example signature (recommended): `consumable_levels: dict[str, float],` — OR change to `field(default_factory=dict)` if the example needs to show a default
- [x] Mutable defaults are a Python anti-pattern; the doc example shouldn't train maintainers to mirror that shape.

---

## Phase Completion Checklist

- [x] All 5 task groups complete (4 unique docs files touched — `production_system.md` carries two findings F-D-006 and F-D-008)
- [x] No occurrence of `DesignLibrary` as a current production surface in `docs/` (run `rg "DesignLibrary" docs/` — PowerShell-friendly; remaining hits should be in historical/changelog context only)
- [x] No occurrence of `_ACTIVATABLE_ABILITIES` as a maintainer recipe target in `docs/` (run `rg "_ACTIVATABLE_ABILITIES" docs/`)
- [x] Run `python Projects/scripts/validate_phase.py PROJ-447 1` — PASSED (no test impact since this is doc-only)
- [x] Update status to `Complete`; plan.md phase table + Current State → Phase 2

## Notes

- Pure text edits; no test risk; no coordination needed with other agents.
- This phase is the natural Stage 1 starting point for PROJ-447 — quick wins, removes maintainer confusion.
- If you find additional doc drift while editing (other deleted-class references, other stale recipes): log via `/claude-di-log` or note in decisions.md; do NOT fix inline (keep Phase 1 narrowly scoped).
