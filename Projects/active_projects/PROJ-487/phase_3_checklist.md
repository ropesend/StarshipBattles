# Phase 3: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-487 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address 2 VERIFIED + IN-SCOPE findings from the Codex mid-project audit (F1 doc drift, F5b stale tag). See `findings/audit_verification.md`.

---

## Tasks

### Task 3.1: Update production_system.md to document generic consumable API (F1) [Simple]
**File:** `docs/systems/production_system.md`

- [x] Lines 70-71 currently read:
  > - Fuel helpers are `get_fuel_storage()`, `get_max_fuel_storage(registries)`,
  >   `add_fuel(amount, registries)`, and `withdraw_fuel(amount)`.
- [x] Rewrite to document the generic API as the canonical surface, e.g.:
  > - Consumable storage uses the generic API: `get_consumable_storage(resource_id)`,
  >   `get_max_consumable_storage(resource_id, registries)`,
  >   `add_consumable(resource_id, amount, registries)`,
  >   `withdraw_consumable(resource_id, amount)`. Fuel is one such consumable
  >   (`resource_id="fuel"`); legacy fuel-specific wrappers were removed in PROJ-487.
- [x] Update the doc's H1 timestamp per `docs/03_CONVENTIONS.md` freshness rule (set "Last verified" to today's date).
- [x] Verify: `grep -n "get_fuel_storage\|add_fuel\|withdraw_fuel\|get_max_fuel_storage" docs/` returns no hits.

---

### Task 3.2: Remove stale F-A-012 tag from test class docstring (F5b) [Simple]
**File:** `tests/unit/strategy/data/test_facility_resource_tracking.py`

- [x] Line 208: change `"""F-A-012: generic add/withdraw/get_consumable_* API."""` → `"""Generic add/withdraw/get_consumable_* API."""` (drop the F-A-012 prefix; the tag was removed from production banner per PROJ-487 implementation).
- [x] Verify: `pytest tests/unit/strategy/data/test_facility_resource_tracking.py -k TestGenericConsumableAPI -v` still passes.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row for Phase 3 to `Complete`
- [x] Update plan.md Current State
