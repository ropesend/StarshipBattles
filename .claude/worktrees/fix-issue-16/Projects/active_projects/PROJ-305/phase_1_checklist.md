# Phase 1: Expand component ability `allowed_scopes` for strategic projection

**Status:** Complete (2026-04-27)
**Objective:** Audit existing ability classes; identify which can legitimately project at strategic-layer scopes; expand their `allowed_scopes` lists. No fleet adapter yet — this phase only ensures the data model can express strategic-scope ship abilities.

---

## Tasks

### Task 1.1: Audit ability classes [Medium]
**File:** N/A (investigation; output is a written audit)

- [ ] List every Ability subclass in `game/simulation/components/abilities/`. For each, note its current `allowed_scopes`.
- [ ] For each, decide: should ship components be allowed to project this ability at any strategic scope (sector / system / allied_*/etc.)?
  - Yes candidates likely include: `SensorBoost` (if exists), `ShieldProjection` (allied_sector for escort flagship), stealth/emission abilities.
  - No candidates likely include: `WeaponAbility`, `BeamWeaponAbility`, `CombatPropulsion`, `ManeuveringThruster`, anything tick-rate combat-internal.
- [ ] Output the audit as a markdown table in this file's Notes section: `| ability | current allowed_scopes | propose adding | rationale |`.
- [ ] **Surface to user**: present the audit; get explicit go/no-go on each row that's ambiguous.

**Notes:**

### Task 1.2: Apply approved scope expansions [Medium]
**File:** `game/simulation/components/abilities/<various>.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/`

- [ ] Failing tests first:
  - For each ability you intend to expand, write a test asserting the new scope is accepted by the parser without raising `ValidationException`.
  - Symmetric test asserting unaffected abilities still reject strategic scopes.
- [ ] Add the approved scopes to each class's `allowed_scopes` list.
- [ ] Run tests — green.

**Notes:**

### Task 1.3: Verify scope-keyword centralization [Simple]
**File:** `game/simulation/components/abilities/base.py`

- [ ] Confirm `AbilityScope` enum already contains all strategic scopes (it should — these were used by storms/facilities in PROJ-300).
- [ ] No new enum values needed.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] User approval on the audit table
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
