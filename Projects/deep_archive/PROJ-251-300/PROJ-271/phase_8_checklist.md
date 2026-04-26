# Phase 8: Modifier Visibility in UI (audit follow-up)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** MEDIUM (UI additions; no engine changes)
**Depends On:** None — pure UI work
**Objective:** Surface PROJ-270/271 modifier effects in the UI so users can actually OBSERVE them. The results screen currently shows HP% + accuracy but hides `max_shields`/`current_shields`. Battle Screen has no indication of active fleet/environmental modifiers.

## Context

E2E goals skeptic findings H-1 and H-2 (2026-04-13):

**H-1:** `game/ui/screens/battle_results_screen.py::_draw_ship_card` (lines 212-258) renders `hp_percent` + weapon accuracy. `ShipResult.max_shields` / `current_shields` are populated by `extract_battle_results` but never drawn. A flat shield bonus of +50 is invisible to the user.

**H-2:** `FleetAuraManager.get_active_bonuses(team_id)` exists (line ~364) returning a list of active team bonuses with source names. Zero UI consumers.

## Tasks

### Task 8.1: Results screen renders shields [Medium]
**File:** `game/ui/screens/battle_results_screen.py` (+ `tests/unit/ui/screens/test_battle_results_screen.py`)

- [ ] Write failing test: given a `BattleOutcome` with a surviving ship that has `max_shields=575` and `current_shields=300`, the rendered ship card text includes "Shields: 300/575".
- [ ] Run — fails (current card doesn't draw shield line).
- [ ] Add a "Shields" row to `_draw_ship_card`: `"Shields: {current_shields:.0f}/{max_shields:.0f}"` between HP and weapon accuracy.
- [ ] Run — passes.
- [ ] Verify visual consistency with existing HP bar rendering.

### Task 8.2: Battle Screen active-modifier indicator [Complex]
**File:** `game/ui/screens/battle_screen.py` (+ tests)

- [ ] Audit `BattleScreen` for a sidebar/overlay location to place a "Active Modifiers" panel.
- [ ] Pull team bonuses via `self.battle_controller.service.aura_manager.get_active_bonuses(team_id)` (or equivalent).
- [ ] Render as a small list: "Storm Shield x0.50", "Shield +75", "Damage x0.80", etc.
- [ ] Only visible when any modifiers are active (no empty panel).
- [ ] Write a unit test that given a controller with known active_bonuses, the panel renders the expected labels.

### Task 8.3: Documentation [Simple]
**File:** `docs/systems/combat_simulation.md` (or a new doc)

- [ ] Document the new Shields row on results card.
- [ ] Document the active-modifiers panel.

### Task 8.4: Manual smoke alongside user's existing PROJ-271 Phase 4.4 smoke [Simple]

- [ ] User verifies a storm-hex battle shows storm multiplier in the active-modifiers panel.
- [ ] User verifies the flat-bonus from a shield projector shows in both the panel AND the results screen shields value.

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] Shield numbers visible on results screen
- [ ] Active-modifier panel functional on battle screen
- [ ] Docs updated
- [ ] Manual smoke confirms user-observable effects
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`

## Note on scope

This phase makes the PROJ-270/271 backend work OBSERVABLE. Without it, the effects exist in the engine but users cannot verify them. That's why both skeptic agents independently flagged this as High — the engine work is correct, but the contract "user can observe the effect" is the actual success criterion.
