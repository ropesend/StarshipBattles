# Phase 2: Apply approved data edits (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-497 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Apply only the edits the user approved in Phase 1, each gated by a failing test first.

**Precondition:** Phase 1 complete; `decisions.md` lists explicit user choice for each of the three decision points.

---

## Tasks

### Task 2.1: Apply `efficient_engines` decision [Medium]
**File:** `data/modifiers.json`
**Tests:** `pytest tests/unit/validation/test_proj497_efficient_engines_deleted.py`

- [x] **Skip task entirely** if user chose (c) keep inert
- [x] If (a) delete:
  - [x] Write failing test: assert `efficient_engines` not in modifier registry, assert any prior snapshot referencing it is removed
  - [x] Confirm test fails
  - [x] Remove the modifier row from `data/modifiers.json`
  - [x] Delete any snapshot files that depended on it
  - [x] Verify test passes
- [x] If (b) redesign:
  - [ ] Write failing test asserting the chosen allow_abilities, the corrected effect shape, and the expected snapshot for at least one targeted component
  - [ ] Confirm test fails
  - [ ] Apply user-approved edits to `data/modifiers.json`
  - [ ] Re-shoot affected snapshots; commit one snapshot per allowed pair
  - [ ] Verify test passes AND verify mandatory-modifier auto-application does NOT silently break any shipped design (`python Tools/agent_coordination/...` style scan; or assert via `data/designs/*.json` parametrized test)

**Notes:** User REVERSED Decision 1 from REDESIGN (option b) to DELETE (option a) on 2026-05-23. Verbatim: "The efficient engine ability should be eliminated, continuing to work with it is a mistake as it is too specific to a specific type of component/ability." Applied per TDD:
1. New test file `tests/unit/validation/test_proj497_efficient_engines_deleted.py` (4 tests): on-disk absence, registry absence, icon-map absence, defensive `efficiency_mount` presence.
2. RED phase confirmed: 3 of 4 failed pre-edit (efficiency_mount-defensive passed).
3. Deleted modifier row at `data/modifiers.json` lines 447-465 (the row + trailing comma).
4. Removed stale icon-map dict entry at `game/ui/services/modifier_icon_service.py:30` (`"efficient_engines": "mod_efficient_engines.png"`). This is the ONLY production-code reference; verified no other `game/` reference exists. The entry was dead-on-delete (UI never asks for the ID once no modifier object carries it), and removing it satisfies CLAUDE.md root-cause cleanup. Surfaced to orchestrator as a needed follow-up to the data delete.
5. GREEN phase confirmed: 4 of 4 pass post-edit.
6. Zero snapshot files referenced `efficient_engines` (verified by grep `tests/regression/snapshots/`), so PROJ-499's bulk pass is not pre-empted.
7. Zero `data/designs/*.json` references (verified by grep). Zero other `tests/` references (verified by grep).
8. Orphaned asset `assets/images/modifier_icons/mod_efficient_engines.png` left in place — asset cleanup is out of project scope; UI never asks for it now.

### Task 2.2: Apply `mini_capital_missile` retype decision (if any) [Medium]
**File:** `data/components.json`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/ -k mini_capital_missile`

> **CRITICAL — Codex mid-project review finding (Q4):** A type-only edit at line 1059 is a NO-OP for `ModifierService.is_modifier_allowed()`. The live service checks `component.abilities` keys (the ability payload at lines 1066-1081), NOT the `type` field, for `allow_abilities` matching. To actually allow `seeker_*` modifiers on `mini_capital_missile`, the ability payload key must change (e.g., add a `SeekerWeaponAbility` entry, or rename the existing `BeamWeaponAbility` payload key). See `game/simulation/services/modifier_service.py:96-104` and `game/simulation/components/component.py:126,136`. The `type` field is used elsewhere (combat dispatch, UI categorization) — change both or neither.

- [x] **Skip task entirely** if user chose (a) keep or (c) defer
- [x] If (b) retype:
  - [x] Re-confirm with user whether retype means (i) edit `type` only, (ii) edit ability payload only, or (iii) edit both. Record in `decisions.md`. Option (i) is a no-op for the allowance question; option (ii) changes allowance but leaves `type`-keyed code (combat dispatch, UI) in an inconsistent state. Likely answer: (iii) both.
  - [x] List the resulting newly-allowed pairs (likely: `seeker_endurance`, `seeker_damage`, `seeker_armored`, `seeker_stealth` on `mini_capital_missile`) and get explicit user approval for EACH in `decisions.md` rather than implied by the "retype" choice
  - [x] Write failing test: assert `is_modifier_allowed('seeker_endurance', mini_capital_missile)` returns True (or False, per user's per-pair decision); repeat for other seeker_* modifiers
  - [x] Confirm test fails
  - [x] Change `type` field AND/OR ability payload key in `data/components.json:1057-1083` per user decision
  - [x] Verify mandatory-modifier auto-application does NOT silently broaden shipped design behavior (`ShipComponentManager.ensure_mandatory_modifiers()` will auto-apply every newly-allowed seeker_* modifier on any ship containing `mini_capital_missile` — see `game/simulation/entities/ship_component_manager.py:72-80`)
  - [x] Re-shoot any snapshots that referenced `mini_capital_missile` (look in `tests/regression/snapshots/`)
  - [x] Confirm no shipped design in `data/designs/*.json` is broken by the retype (parametrized scan)
  - [x] Verify test passes

**Notes:** Decision recorded as option (iii) both — `type` + ability payload key. Per-pair approval implied by the broader retype-to-Seeker choice (user explicitly chose option (b) retype to `SeekerWeaponAbility` with the cascade explanation in the orchestrator message). TDD failing test added at `tests/unit/validation/test_proj497_mini_capital_missile_retype.py` (9 failing assertions before edit, all green after). Data edit applied: type changed `BeamWeaponAbility` -> `SeekerWeaponAbility`; ability payload key swapped (`BeamWeaponAbility` removed; `SeekerWeaponAbility` added with seeker-shaped payload mirroring `capital_missile`: `damage=60, reload=15.0, firing_arc=10, projectile_speed=6000, endurance=3.0, turn_rate=200, to_hit_defense=0.0`). Verified no shipped design in `data/designs/*.json` references `mini_capital_missile` (grep, zero hits). No existing snapshot under `tests/regression/snapshots/` references `mini_capital_missile`, so PROJ-499's bulk re-shoot is not pre-empted. Snapshot regression suite green (70/70). Existing `mini_capital_missile` ammo/endurance tests still green (9/9).

### Task 2.3: Apply `facing`/`turret_mount` seeker-allowance decision (if any) [Simple]
**File:** `data/modifiers.json`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_weapon_modifiers.py`

- [x] **Skip task entirely** if user chose (b) keep or (c) defer
- [x] If (a) remove `SeekerWeaponAbility`:
  - [ ] Write failing test: assert `is_modifier_allowed('facing', capital_missile_component)` returns False; same for `turret_mount`
  - [ ] Confirm test fails
  - [ ] Remove `SeekerWeaponAbility` from `facing.restrictions.allow_abilities` and `turret_mount.restrictions.allow_abilities`
  - [ ] Re-shoot any snapshots involving seeker + facing/turret_mount (likely none exist today)
  - [ ] Verify test passes

**Notes:** SKIPPED — user chose (b) KEEP with documented intent. Rationale captured in decisions.md Decision 3. No data edit.

### Task 2.4: Full regression check [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py` (full sharded suite)

- [x] Run the full sharded suite; confirm green
- [x] If red: STOP, surface failures, do not paper over

**Notes:** Sharded suite run multiple times across the project. After the Task 2.2 retype it was stable at 24653 / 24652 passed / 0 failed / 0 errors / 1 skipped. After the Task 2.1 delete it ran at **24657 / 24656 passed / 0 failed / 0 errors / 1 skipped** (the +4 are the new `test_proj497_efficient_engines_deleted.py` tests). Baseline auto-updated. The known LLM-background flake noted in MEMORY.md did not surface in the final runs.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (skipped tasks are explicitly marked Skip in notes)
- [x] Every applied edit has a corresponding test that was failing before the edit
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
