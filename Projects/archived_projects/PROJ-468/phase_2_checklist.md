# Phase 2: Major dead refs + missing docs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-468 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the 9 verified MAJOR dead references, add a `Last verified:` stamp to `pre_commit_hooks.md`, and add documentation coverage for 2 undocumented architectural-surface modules, identified by audit `2026-05-20_073330_docs-audit`.

---

## Tasks

### Task 2.1: ability_reference.md major dead refs [Medium]
**File:** `docs/systems/ability_reference.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Update `planetary.py` (line 373) to the `game/simulation/components/abilities/planetary/` package
- [x] Update dead test references `tests/unit/strategy/services/test_effect_ability_metadata.py` (lines 108, 571, 585) to current coverage (e.g. `test_ability_metadata_contracts.py` / `test_ability_metadata_registry.py` / `test_ability_metadata_effects.py`)
- [x] Verify: cited paths resolve to existing package / test files


**Notes:** planetary.py refs (table rows 251-268 mapped to exact package files via class lookup; lines 373/392/405/537) -> planetary/ package; test_effect_ability_metadata.py (108/571/585) -> test_ability_metadata_effects.py + siblings; also fixed in-family EFFECT_ABILITY_METADATA at line 538.

### Task 2.2: strategy_layer.md spectrum path [Simple]
**File:** `docs/systems/strategy_layer.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Update `data/spectrum.py` (line 831) to `game/strategy/data/spectrum.py`
- [x] Verify: `grep -n "data/spectrum.py" docs/systems/strategy_layer.md` shows only the corrected path


**Notes:** data/spectrum.py -> game/strategy/data/spectrum.py (line 831).

### Task 2.3: fighters.md + minefields.md planet_context_menu split [Simple]
**File:** `docs/systems/fighters.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Update `planet_context_menu.py` (fighters.md line 244) to `planet_menu_items.py` + `fms_menu_callbacks.py`


**Notes:** fighters.md: removed dead trailing planet_context_menu link; split files already present in lines 242-243.

### Task 2.4: minefields.md planet_context_menu split [Simple]
**File:** `docs/systems/minefields.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Update `planet_context_menu.py` (minefields.md lines 247, 323) to `planet_menu_items.py` + `fms_menu_callbacks.py`


**Notes:** minefields.md: removed dead planet_context_menu link (247) and File-table row (323); split rows already present.

### Task 2.5: research_system.md research/ui path [Simple] — DROPPED (already correct)
**File:** `docs/systems/research_system.md`
**Verification:** Re-verified against live doc.

- [x] DROPPED: re-verification shows `research_system.md:24` is NOT self-contradictory. It already reads "Do not recreate the old `game/research/ui/` path. It was moved to `game/ui/research/` to remove a layer violation." — a correct historical-corrective warning, exactly the requested outcome. Every other `research/ui` mention (lines 5,16,21,170,197) uses the correct live `game/ui/research/` path. No edit needed; finding no longer holds. See decisions.md.


**Notes:** DROPPED — finding does not hold; doc already correct.

### Task 2.6: adding_abilities.md dead test path [Simple]
**File:** `docs/guides/adding_abilities.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Update dead test references `test_effect_ability_metadata.py` (lines 434, 539) to current coverage files


**Notes:** adding_abilities.md lines 434/539 test_effect_ability_metadata.py -> test_ability_metadata_effects.py.

### Task 2.7: qs_complex_design.md planetary + dead test [Simple]
**File:** `docs/guides/qs_complex_design.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Update `planetary.py` (line 212) to the `planetary/` package
- [x] Update dead test reference `tests/unit/strategy/test_component_inspector.py` (line 319) to current coverage


**Notes:** qs_complex_design.md line 212 planetary.py -> planetary/ package; line 319 test_component_inspector.py -> test_component_abilities.py + test_component_layers.py.

### Task 2.8: component_system.md dead test [Simple]
**File:** `docs/guides/component_system.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Update dead test reference `tests/unit/strategy/test_component_inspector.py` (line 347) to current coverage


**Notes:** component_system.md line 348 test_component_inspector.py -> test_component_abilities.py + test_component_layers.py.

### Task 2.9: testing_infrastructure.md test_damage command [Simple]
**File:** `docs/guides/testing_infrastructure.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Fix the command example `pytest tests/unit/simulation/test_damage.py -n 0` (line 170) — `tests/unit/simulation/test_damage.py` does not exist; replace with an existing damage test path or a generic placeholder
- [x] Verify: any concrete test path in the example resolves to an existing file


**Notes:** testing_infrastructure.md line 170 test_damage.py -> tests/unit/simulation/combat/test_damage_calculator.py (verified exists).

### Task 2.10: pre_commit_hooks.md Last verified [Simple]
**File:** `docs/guides/pre_commit_hooks.md`
**Verification:** Read the doc end-to-end after edits.

- [x] Add the missing `> **Last verified:** YYYY-MM-DD` blockquote below the H1 (the only G3 guide lacking it)


**Notes:** pre_commit_hooks.md: added Last verified blockquote below H1.

### Task 2.11: Document superweapon_order_processor [Medium]
**File:** `docs/systems/strategy_layer.md`
**Verification:** Read the doc end-to-end after edits; confirm the documented surface matches the module.

- [x] Add a documentation section covering `game/strategy/engine/superweapon_order_processor.py` (506 LOC, zero current doc mentions) — host it in `strategy_layer.md` (or a new `docs/systems/` section if it warrants its own file); describe its role in superweapon order processing
- [x] Verify: `grep -rn "superweapon_order_processor" docs/` now returns at least one substantive mention


**Notes:** strategy_layer.md: added Superweapon Order Processing subsection (process_* table, execute_superweapon prologue, mutator seams, self-destruct exclusion) verified against superweapon_order_processor.py.

### Task 2.12: Document game_initializer [Medium]
**File:** `docs/01_ARCHITECTURE.md`
**Verification:** Read the doc end-to-end after edits; confirm the documented surface matches the module.

- [x] Add documentation coverage for `game/strategy/engine/game_initializer.py` (446 LOC bootstrap path, zero current doc mentions) — host in `01_ARCHITECTURE.md` bootstrap/strategy section; describe its role in the game-initialization flow
- [x] Verify: `grep -rn "game_initializer" docs/` now returns at least one substantive mention


**Notes:** 01_ARCHITECTURE.md: added New-Game Initialization (GameInitializer) subsection after GameSession Lifecycle; FEAT-27 retry loop, placement strategies, PROJ-370 mutator seams, load-path exclusion. Verified against game_initializer.py.

### Task 2.13: Phase-wide verification [Simple]
**File:** (multiple — verification only)

- [x] Verify: `Last verified:` stamps updated on all docs touched this phase; deterministic scan re-run shows zero dead refs in modified files


**Notes:** Deterministic scan across all 12 touched docs shows zero live dead refs; all newly-cited paths/symbols positively verified to exist. All Last verified stamps bumped to 2026-05-20.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_073330_docs-audit/`. See `findings/source_audit.md` for the link._
