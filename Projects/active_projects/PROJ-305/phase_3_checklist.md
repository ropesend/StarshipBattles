# Phase 3: Sample component (Flagship Shield Projector) + integration

**Status:** Not Started
**Objective:** Add a real, gameplay-meaningful component that exercises the fleet-projection path end-to-end. Validates the framework with actual data, not just synthetic tests.

> **2026-04-27 update (decisions.md D10):** Original plan referenced `SensorBoost scope: allied_sector` on a "Flagship Sensor Array". `SensorBoost` does not exist in the codebase, and inventing it is a separate design item (range? detection? fog-of-war?). PROJ-305 is plumbing, not new ability semantics. The sample is now a **Flagship Shield Projector** using `ShieldModifier`, which already supports `allied_sector` ([planetary.py:443](../../../game/simulation/components/abilities/planetary.py#L443)). Zero new ability work.

---

## Tasks

### Task 3.1: Confirm `ShieldModifier` accepts `scope: allied_sector` end-to-end [Trivial]
**File:** read-only verification in `game/simulation/components/abilities/planetary.py`

- [ ] Confirm `ShieldModifierAbility.allowed_scopes` includes `ALLIED_SECTOR` (it does as of 2026-04-27 — line 443).
- [ ] Confirm `_STRATEGIC_SCOPES` in PROJ-305's adapter includes `allied_sector`.
- [ ] No code change unless the precondition has drifted.

**Notes:** This task replaces the original "introduce SensorBoost" work — see D10.

### Task 3.2: Add Flagship Shield Projector component [Medium]
**File:** `data/components.json`
**Tests:** `tests/unit/data/test_components_registry.py` (or whichever validates components.json)

- [ ] Add a new component:
  ```json
  {
    "id": "flagship_shield_projector",
    "name": "Flagship Shield Projector",
    "type": "Defensive",
    "mass": "= ...",
    "hp": "= ...",
    "allowed_vehicle_types": ["Ship"],
    "description": "Projects a coordinated shield-bonus aura to allied ships sharing this fleet's hex on the strategy map.",
    "abilities": {
      "ShieldModifier": {"multiplier": 1.25, "scope": "allied_sector"}
    },
    ...
  }
  ```
- [ ] Confirm registry validation passes (`ShieldModifier` already supports `allied_sector`).
- [ ] Confirm the component appears in the existing `system_effects_collector` test paths since `ShieldModifier` is already a known sector-effect ability.

**Notes:** Multiplier 1.25 is illustrative — Phase 3 is plumbing demonstration, not balance. Final tuning is a separate gameplay-balance pass.

### Task 3.3: Add an existing test ship design that mounts the new component [Simple]
**File:** Either an existing `data/designs/qs_*.json` or a new test-ship design.

- [ ] Add the Flagship Shield Projector to (e.g.) `qs_battleship.json` so the QS battleship is a "flagship" with strategic shield projection.
- [ ] Update tests in `tests/unit/quickstart/test_quickstart_designs.py` if the addition triggers validation.

**Notes:**

### Task 3.4: End-to-end integration test [Complex]
**File:** `tests/integration/strategy/test_fleet_sector_effects_end_to_end.py` (NEW)

- [ ] Build fixture: a galaxy with Player 1's fleet (containing a flagship with the new component) at hex H, and Player 1 also having an "observer" fleet at H.
- [ ] **Test:** When the UI queries Sector Effects at H from Player 1's perspective, the `ShieldModifier 1.25× (allied_sector)` effect appears with `source_label = "Flagship 'Indomitable' (Player 1)"` (or fleet label per D5).
- [ ] **Test:** When combat resolves at H with allied ships present, the `_entries_from_sector_effects` path emits a `ShieldModifier` entry per provider — combat ships gain the projected bonus alongside any storm/facility entries.
- [ ] **Test:** Move the fleet to a different hex H' — the effect now appears at H', not H. Confirms per-instance `get_abilities()` memoization (D12) does not leak across hexes.
- [ ] **Test:** Have an enemy fleet sit at H — the enemy's empire-scoped query does NOT see the ShieldModifier (allied_sector scope + owner filtering).
- [ ] **Test:** Combat in H — confirm `scope: fleet` aura abilities (from existing components) still flow through the FleetAuraManager combat path correctly (they were not consumed by FleetAbilitySource — D2 scope dichotomy).
- [ ] **Test (D11 cloak default):** With a hand-toggled `_is_hidden=True` on the adapter, `affects_hex(H)` returns False and the effect disappears from Sector Effects. Locks in the safe default for future stealth design.

**Notes:** This is the canonical "fleet projects to ally hex" smoke test for the framework. Reuse fixtures wherever possible; the integration is end-to-end (fleet → adapter → iterator → collector → UI render path → combat spec compiler).

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] D10 sample swap verified — no `SensorBoost` references in PROJ-305 code or tests.
- [ ] D11 cloak-default test green.
- [ ] Update status to `Complete`
- [ ] Update plan.md
