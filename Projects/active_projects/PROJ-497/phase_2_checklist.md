# Phase 2: Apply approved data edits (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-497 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Apply only the edits the user approved in Phase 1, each gated by a failing test first.

**Precondition:** Phase 1 complete; `decisions.md` lists explicit user choice for each of the three decision points.

---

## Tasks

### Task 2.1: Apply `efficient_engines` decision [Medium]
**File:** `data/modifiers.json`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_utility_modifiers.py -k efficient_engines`

- [ ] **Skip task entirely** if user chose (c) keep inert
- [ ] If (a) delete:
  - [ ] Write failing test: assert `efficient_engines` not in modifier registry, assert any prior snapshot referencing it is removed
  - [ ] Confirm test fails
  - [ ] Remove the modifier row from `data/modifiers.json`
  - [ ] Delete any snapshot files that depended on it
  - [ ] Verify test passes
- [ ] If (b) redesign:
  - [ ] Write failing test asserting the chosen allow_abilities, the corrected effect shape, and the expected snapshot for at least one targeted component
  - [ ] Confirm test fails
  - [ ] Apply user-approved edits to `data/modifiers.json`
  - [ ] Re-shoot affected snapshots; commit one snapshot per allowed pair
  - [ ] Verify test passes AND verify mandatory-modifier auto-application does NOT silently break any shipped design (`python Tools/agent_coordination/...` style scan; or assert via `data/designs/*.json` parametrized test)

**Notes:** [Filled during implementation]

### Task 2.2: Apply `mini_capital_missile` retype decision (if any) [Medium]
**File:** `data/components.json`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/ -k mini_capital_missile`

> **CRITICAL — Codex mid-project review finding (Q4):** A type-only edit at line 1059 is a NO-OP for `ModifierService.is_modifier_allowed()`. The live service checks `component.abilities` keys (the ability payload at lines 1066-1081), NOT the `type` field, for `allow_abilities` matching. To actually allow `seeker_*` modifiers on `mini_capital_missile`, the ability payload key must change (e.g., add a `SeekerWeaponAbility` entry, or rename the existing `BeamWeaponAbility` payload key). See `game/simulation/services/modifier_service.py:96-104` and `game/simulation/components/component.py:126,136`. The `type` field is used elsewhere (combat dispatch, UI categorization) — change both or neither.

- [ ] **Skip task entirely** if user chose (a) keep or (c) defer
- [ ] If (b) retype:
  - [ ] Re-confirm with user whether retype means (i) edit `type` only, (ii) edit ability payload only, or (iii) edit both. Record in `decisions.md`. Option (i) is a no-op for the allowance question; option (ii) changes allowance but leaves `type`-keyed code (combat dispatch, UI) in an inconsistent state. Likely answer: (iii) both.
  - [ ] List the resulting newly-allowed pairs (likely: `seeker_endurance`, `seeker_damage`, `seeker_armored`, `seeker_stealth` on `mini_capital_missile`) and get explicit user approval for EACH in `decisions.md` rather than implied by the "retype" choice
  - [ ] Write failing test: assert `is_modifier_allowed('seeker_endurance', mini_capital_missile)` returns True (or False, per user's per-pair decision); repeat for other seeker_* modifiers
  - [ ] Confirm test fails
  - [ ] Change `type` field AND/OR ability payload key in `data/components.json:1057-1083` per user decision
  - [ ] Verify mandatory-modifier auto-application does NOT silently broaden shipped design behavior (`ShipComponentManager.ensure_mandatory_modifiers()` will auto-apply every newly-allowed seeker_* modifier on any ship containing `mini_capital_missile` — see `game/simulation/entities/ship_component_manager.py:72-80`)
  - [ ] Re-shoot any snapshots that referenced `mini_capital_missile` (look in `tests/regression/snapshots/`)
  - [ ] Confirm no shipped design in `data/designs/*.json` is broken by the retype (parametrized scan)
  - [ ] Verify test passes

**Notes:** [Filled during implementation]

### Task 2.3: Apply `facing`/`turret_mount` seeker-allowance decision (if any) [Simple]
**File:** `data/modifiers.json`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_weapon_modifiers.py`

- [ ] **Skip task entirely** if user chose (b) keep or (c) defer
- [ ] If (a) remove `SeekerWeaponAbility`:
  - [ ] Write failing test: assert `is_modifier_allowed('facing', capital_missile_component)` returns False; same for `turret_mount`
  - [ ] Confirm test fails
  - [ ] Remove `SeekerWeaponAbility` from `facing.restrictions.allow_abilities` and `turret_mount.restrictions.allow_abilities`
  - [ ] Re-shoot any snapshots involving seeker + facing/turret_mount (likely none exist today)
  - [ ] Verify test passes

**Notes:** [Filled during implementation]

### Task 2.4: Full regression check [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py` (full sharded suite)

- [ ] Run the full sharded suite; confirm green
- [ ] If red: STOP, surface failures, do not paper over

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked (skipped tasks are explicitly marked Skip in notes)
- [ ] Every applied edit has a corresponding test that was failing before the edit
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
