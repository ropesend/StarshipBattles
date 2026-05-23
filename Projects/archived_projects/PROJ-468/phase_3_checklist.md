# Phase 3: Codex-audit verified additional dead refs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-468 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the 5 additional dead references the Codex audit (advisory) surfaced in two files already in this project's scope (`docs/guides/adding_abilities.md`, `docs/systems/strategy_layer.md`). All 5 VERIFIED against live code: the same component_inspector/effect_ability_metadata/planetary-package fix family the project owns, missed by the original audit's line list. The Codex audit also confirmed (b) no cited symbol/path is wrong and (d) no introduced replacement path is wrong.

---

## Tasks

### Task 3.1: adding_abilities.md residual planetary.py + EFFECT_ABILITY_METADATA [Simple]
**File:** `docs/guides/adding_abilities.md`
**Verification:** Re-grep after edits; confirm replacements resolve.

- [x] Line 511 ability-category list: `planetary.py` → `planetary/` package (the file was split; sibling list entries `weapons.py`, `defense.py`, etc. remain real files)
- [x] Line 582 troubleshooting: replace "add `EFFECT_ABILITY_METADATA`" with the live path — add an `AbilityMetadata` entry with an `EffectFacet` in `ability_metadata.py` (no live `EFFECT_ABILITY_METADATA` symbol; only a code comment references the retired name)
- [x] Verify: `grep -n "EFFECT_ABILITY_METADATA\|abilities/planetary\.py" docs/guides/adding_abilities.md` shows no live action-teaching path

**Notes:** Line 511 `- planetary.py` → `- planetary/` (package). Line 582 rewritten to instruct adding an AbilityMetadata/EffectFacet entry in ability_metadata.py; kept the "do not add stale SYSTEM_EFFECT_ABILITIES" warning as a correct anti-pattern note.

### Task 3.2: strategy_layer.md residual EFFECT_ABILITY_METADATA + planetary.py + SYSTEM_EFFECT_ABILITIES [Simple]
**File:** `docs/systems/strategy_layer.md`
**Verification:** Re-grep after edits; confirm replacements resolve; confirm line 706 no longer contradicts the corrected shim text.

- [x] Line 706: remove "Drives the legacy `EFFECT_ABILITY_METADATA` shim" (the shim/module is gone — contradicts the corrected line ~723); state `EffectFacet` is consumed directly from the unified registry
- [x] Line 746 (Activatable Ability Extension Checklist): `planetary.py` → appropriate `planetary/` package module
- [x] Line 752: replace "add to `SYSTEM_EFFECT_ABILITIES`" (no live symbol) with adding an `AbilityMetadata` entry with an `EffectFacet` in `ability_metadata.py`
- [x] Verify: `grep -n "EFFECT_ABILITY_METADATA\|SYSTEM_EFFECT_ABILITIES\|planetary\.py" docs/systems/strategy_layer.md` shows no live dead symbol/path

**Notes:** Three residual dead refs fixed; line 706 contradiction resolved. SYSTEM_EFFECT_ABILITIES confirmed absent in game/ (grep empty); EFFECT_ABILITY_METADATA exists only as a code comment in ability_metadata.py.

### Task 3.3: Phase-wide re-verification [Simple]
**File:** (multiple — verification only)

- [x] Verify: full dead-ref scan across both files clean; all replacement paths/symbols resolve

**Notes:** Re-ran scan; only verification-stamp/anti-pattern mentions remain. All replacements (`planetary/` package, `ability_metadata.py`, `EffectFacet`/`AbilityMetadata`) verified present.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source: Codex advisory audit at `AgentCoordination/Scratchpad/Consult/proj468_audit/audit.md.invalid-output-*.txt`; all findings independently re-verified against live code/docs._
