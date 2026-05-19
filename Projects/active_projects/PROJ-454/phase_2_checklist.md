# PROJ-454 Phase 2: Retire `component_inspector.py` (F-B-005)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-454 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Close F-B-005 by migrating **~68 caller sites across ~31 distinct files** (52 `from ... import` + 16 `patch(...)` targets — codex audit 2026-05-19 corrected from the original `~45 sites` estimate) of `component_inspector.py` to the canonical destination modules (`component_abilities.py` or `component_layers.py`), then deleting the shim. **The largest mechanical sweep in this project.**

**Cross-bucket file-ownership rule:** This phase touches the `component_inspector.py` callers across `game/strategy/data/`, `game/strategy/engine/`, `game/strategy/services/`, `game/strategy/validation/`, `game/ui/screens/`, and the matching test files. **Per the project brief:** edit only the import statement in `game/ui/` files; do NOT refactor UI behaviour.

**Source-of-truth findings:** [`findings/PROJ-454_findings.md`](findings/PROJ-454_findings.md) — read F-B-005's full text, the symbol map, **both caller lists** (production + tests), and the "UI behaviour preservation" section at the bottom.

---

## Tasks

### Task 2.1: Re-run the canonical caller-list discovery commands [Simple]
**Tests:** N/A — this is a discovery task

- [x] Run the canonical discovery commands from the findings file:
  ```bash
  git grep -nE "from game\.strategy\.services\.component_inspector import|game\.strategy\.services\.component_inspector\." game/ tests/
  git grep -n "game.strategy.services.component_inspector\." tests/
  ```
- [x] Diff the 2026-05-19 caller list in `findings/PROJ-454_findings.md` against the current output. Note any callers added since the audit. If the diff is non-zero, update `findings/PROJ-454_findings.md` "F-B-005 caller list" sections in place.
- [x] **Sanity check the symbol map**: for each of the 16 symbols listed in `findings/PROJ-454_findings.md` "F-B-005 symbol map (canonical)", verify the destination module per `component_inspector.py:28-47`. If a symbol has moved or been renamed, document in `decisions.md`.

**Notes:**

---

### Task 2.2: Migrate `game/strategy/data/` callers (5 files) [Simple]
**Files (5):**
- `game/strategy/data/build_queue_source.py:147, 224`
- `game/strategy/data/fleet_capability_calculator.py:65, 111, 188, 208, 237, 256`
- `game/strategy/data/planetary_facility.py:12`
- `game/strategy/data/ship_instance.py:635, 654, 663`

**Tests:** `pytest tests/unit/strategy/data/ -q`

- [x] For each file, replace the import path on the affected lines. Per-line edits:
  - `build_queue_source.py:147,224` — `get_component_abilities` → `from game.strategy.services.component_abilities import get_component_abilities`
  - `fleet_capability_calculator.py:65` — `ship_has_ability` → `component_abilities`
  - `fleet_capability_calculator.py:111` — `count_ability` → `component_abilities`
  - `fleet_capability_calculator.py:188,208` — `has_warp_capability` → `component_abilities`
  - `fleet_capability_calculator.py:237` — `ship_has_ability as check_ability` → `component_abilities`
  - `fleet_capability_calculator.py:256` — `list_ship_abilities` → `component_abilities`
  - `planetary_facility.py:12` — `get_component_abilities` → `component_abilities`
  - `ship_instance.py:635` — `count_damaged_components` → `component_layers`
  - `ship_instance.py:654` — `iter_components_by_layer` → `component_layers`
  - `ship_instance.py:663` — `damaged_components_by_layer` → `component_layers`
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 2.3: Migrate `game/strategy/engine/` callers (8 files) [Simple]
**Files (8):**
- `atmosphere_engine.py:15`
- `consumable_management_engine.py:21, 24`
- `harvesting_engine.py:27`
- `planet_action_engine.py:311, 325, 339, 388`
- `planet_energy_engine.py:28, 88`
- `quality_engine.py:14`
- `resupply_engine.py:23, 27`
- `water_engine.py:14`

**Tests:** `pytest tests/unit/strategy/engine/ -q`

- [x] For each file, repoint the import to `component_abilities` (all engine callers consume Surface A symbols per the 2026-05-19 audit — verify against the caller list before editing).
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 2.4: Migrate `game/strategy/services/` + `game/strategy/validation/` callers (6 files) [Simple]
**Files (6):**
- `game/strategy/services/ability_sources/facility.py:14`
- `game/strategy/services/ability_sources/fleet.py:137`
- `game/strategy/services/action_time_resolver.py:34, 242`
- `game/strategy/services/strategic_ability_scanner.py:14`
- `game/strategy/validation/planet_order_validator.py:13`
- `game/strategy/validation/superweapon_validator.py:8`

**Tests:** `pytest tests/unit/strategy/services/ tests/unit/strategy/validation/ -q`

- [x] Repoint each import to `component_abilities` (Surface A).
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 2.5: Migrate `game/ui/screens/` callers — **import lines only, no UI behaviour changes** (6 files) [Simple]
**Files (6):**
- `fleet_data_source.py:234, 266`
- `fleet_report_filters.py:12, 186, 313`
- `planet_abilities_controller.py:112, 142`
- `strategy_detail_fmt.py:405`
- `strategy_detail_formatter.py:305`
- `strategy_fleet_command_router.py:263`

**Tests:** `pytest tests/unit/ui/screens/ -q`

- [x] **DISCIPLINE GATE**: re-read the "UI behaviour preservation" section in `findings/PROJ-454_findings.md` before starting. Edit only the import statement. If you notice UI residue while doing the touch, log it via `/claude-di-log` — do NOT fix inline.
- [x] For each file, repoint the import to `component_abilities` (all 6 UI callers consume Surface A symbols).
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 2.6: Migrate test-side direct imports (3 files) [Simple]
**Files (3):**
- `tests/integration/test_design_load_warp_capability.py:30` (`has_warp_capability`)
- `tests/unit/strategy/test_component_inspector.py:9` (multi-symbol)
- `tests/unit/strategy/services/test_component_inspector_layers.py` (Surface B tests)

**Tests:** `pytest tests/integration/test_design_load_warp_capability.py tests/unit/strategy/test_component_inspector.py tests/unit/strategy/services/test_component_inspector_layers.py -v`

- [x] Repoint imports per the symbol map.
- [x] **Decide file renames**:
  - `tests/unit/strategy/test_component_inspector.py` — if all its tests target Surface A symbols, rename to `test_component_abilities.py` and move to `tests/unit/strategy/services/`. Update the import path. If it has mixed-surface tests, split.
  - `tests/unit/strategy/services/test_component_inspector_layers.py` — already names the canonical Surface; rename to `test_component_layers.py` (drop the `_inspector_` infix).
- [x] Run the renamed tests; confirm green.

**Notes:** Decisions go in `decisions.md`. Test file renames are explicitly in-scope for Phase 2; the project brief allows file renames when they reflect the canonical surface.

---

### Task 2.7: Repoint `patch(...)` targets in unit tests (3 files, ~18 sites) [Medium]
**Files (3):**
- `tests/unit/strategy/test_fleet_capability_calculator.py:257, 279, 296, 318` (4 sites)
- `tests/unit/ui/screens/test_fleet_data_source.py:296, 301, 456, 469, 486` (5 sites)
- `tests/unit/ui/screens/test_strategy_fleet_command_router.py:415, 458` (2 sites)

**Tests:** `pytest tests/unit/strategy/test_fleet_capability_calculator.py tests/unit/ui/screens/test_fleet_data_source.py tests/unit/ui/screens/test_strategy_fleet_command_router.py -v`

- [x] For each `patch('game.strategy.services.component_inspector.X', ...)` site, repoint to the canonical module path:
  - `has_warp_capability` → `patch('game.strategy.services.component_abilities.has_warp_capability', ...)`
  - `ship_has_ability` → `patch('game.strategy.services.component_abilities.ship_has_ability', ...)`
  - `extract_abilities_from_component` → `patch('game.strategy.services.component_abilities.extract_abilities_from_component', ...)`
- [x] **Critical**: a `patch()` target is path-based, not symbol-based. Once `component_inspector.py` is deleted, any surviving `patch('game.strategy.services.component_inspector.X')` will raise `AttributeError` at test setup. This is the bug class Task 2.7 prevents.
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 2.8: Repoint `patch(...)` targets in `test_fleet_report_filters.py` (11 sites) [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py:345, 352, 359, 366, 373, 380, 863, 1079, 1105, 1155, 1178`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [x] Same recipe as Task 2.7, but for **11 sites in a single file** — the largest single-file test migration in PROJ-454.
- [x] Walk through each site; identify the symbol being patched; repoint to `component_abilities` (all 11 are Surface A per the 2026-05-19 audit).
- [x] Lines 345-380 (6 sites) — `has_warp_capability` patches; lines 863, 1079, 1105, 1155, 1178 (5 sites) — `ship_has_ability` patches.
- [x] Run targeted tests; confirm green.

**Notes:** This file is the largest sink for the test-side migration. Don't rush; verify each line before saving.

---

### Task 2.9: Decide the fate of `test_component_inspector_surface.py` [Simple]
**File:** `tests/unit/strategy/services/test_component_inspector_surface.py:43, 56, 68`

- [x] Read the full file. It's a static drift gate against the shim's export surface.
- [x] **Decision**:
  - **Delete** if the test's purpose was gating the shim. With the shim gone, the gate is meaningless.
  - **Refactor** into a static guard against re-emergence of `component_inspector.py` as a module (mirror `tests/static_guards/test_no_design_library_class.py` or `tests/static_guards/test_no_resource_types_constant.py`). The guard would `assert not pkgutil.find_loader('game.strategy.services.component_inspector')` or similar.
- [x] Apply the decision; document in `decisions.md`.

**Notes:** Codex r4 redesign job #6 mentions the established static-guard pattern for retired surfaces. Adding a re-emergence guard is the preferred path; it costs nothing and prevents accidental re-creation.

---

### Task 2.10: Delete `component_inspector.py` [Simple]
**File:** `game/strategy/services/component_inspector.py` (delete)
**Tests:** Full sharded suite

- [x] **Pre-delete sanity check**: `git grep -n "component_inspector" game/ tests/` should return only `Projects/archived_projects/` matches (historical narration) and the `component_abilities.py:11` / `component_layers.py:14` docstring references (which describe the retired shim).
- [x] If the sanity check passes, delete: `git rm game/strategy/services/component_inspector.py`.
- [x] **Post-delete sanity check**: `python -c "from game.strategy.services import component_inspector"` should fail with `ModuleNotFoundError`.
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.

**Notes:** If the sharded run fails because of a missed caller (e.g., a lazy import inside a function body that the static grep didn't catch), restore the file (`git restore`), find the caller, migrate it, and try again.

---

### Task 2.11: Verify F-B-005 closure [Simple]

- [x] `git grep -n "component_inspector" game/ tests/` returns zero matches (excluding archived projects + the canonical-module docstring references documenting the shim's historical existence).
- [x] `game/strategy/services/component_inspector.py` no longer exists.
- [x] Document closure in `decisions.md`: `2026-XX-XX | F-B-005 closed | Migrated ~68 caller sites (52 imports + 16 patch targets, codex audit 2026-05-19 corrected from the original ~45 estimate) across game/strategy/{data,engine,services,validation}/ + game/ui/screens/ + tests/. Deleted shim (67 LOC) and static-guard test file. Static re-emergence guard added at <path> per Task 2.9 decision. | PROJ-454 Phase 2.`

**Notes:**

---

## Phase Completion Checklist

When all tasks above are checked off:

- [x] F-B-005 closed (documented in `decisions.md`)
- [x] `component_inspector.py` deleted
- [x] All ~68 caller migrations landed green (52 `import` + 16 `patch` — count corrected by codex audit 2026-05-19)
- [x] All `patch(...)` targets repointed
- [x] Static drift-gate test deleted or refactored into a re-emergence guard
- [x] `pytest tests/unit/ tests/integration/ -q` green
- [x] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [x] Run `python Projects/scripts/validate_phase.py PROJ-454 2` — PASSED
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3

## Notes / Deferrals

- **UI behaviour preservation** — strict throughout the phase. The 6 UI files in Task 2.5 are import-line edits only. Anything beyond that is out-of-scope.
- **`patch()` target hazard** — the most common foot-gun in this phase. `patch()` resolves the target path at test-setup time; a stale `component_inspector` path fails the test only when the test runs. Verify by running the affected test files at each step.
- **File renames** — `test_component_inspector.py` and `test_component_inspector_layers.py` should be renamed to match the destination modules. Renames are in-scope.
- **`component_abilities.py:11` + `component_layers.py:14`** — these docstring references to the retired shim should be refreshed in Phase 2 wrap-up (decision in `decisions.md` whether to drop them outright or keep as historical narration).
