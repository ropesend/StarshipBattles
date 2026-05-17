# Phase 7: Label 5d/5e shims explicitly (Codex consult follow-up)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-425 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_5 (which left the 5d/5e forwarders intact as protected shims). **Does NOT depend on phase_6** — Phase 6 remains gated by PROJ-431 Phase 1, but Phase 7 is documentation-only and runs immediately.
**Review Mode:** lightweight
**Files (planned):**
- `game/strategy/data/ship_instance.py` (comment-only — add 5d serializer + 5e bridge labels)

**Objective:** Codex's 2026-05-17 consult on the shipped PROJ-425 work noted that the 5d serializer (`to_dict` / `from_dict` / `to_json` / `from_json` / `clone`) and 5e bridge (`to_ship` / `update_from_ship`) forwarder groups in `ship_instance.py` lacked the explicit "retained shim" comment block that the 5b consumable group already had. `decisions.md` claimed all four shim groups were labeled; only 5b actually was. Phase 7 adds matching comment blocks above the 5d and 5e groups so every retained shim group is now self-documenting and consistent.

**Format guarantee:** the new comment blocks mirror the existing 5b block format (3-paragraph structure: why retained, canonical delegate, removal condition).

---

## Tasks

### Task 7.1: Add 5e bridge shim comment block [Simple]
**File:** `game/strategy/data/ship_instance.py`

- [x] Above the `to_ship` / `update_from_ship` forwarders, add a comment block explaining:
  - Why these are intentional shims (not bugs / dead code) — Guardrail #1 + ~10 live production callers.
  - The canonical delegate that owns the real behavior — `ShipInstanceBridge`.
  - The removal condition — once callers migrate to direct `ship._bridge.to_ship(...)` / `.update_from_ship(...)` access.
- [x] Match the format of the existing 5b consumable shim comment block in the same file.

### Task 7.2: Add 5d serializer shim comment block [Simple]
**File:** `game/strategy/data/ship_instance.py`

- [x] Above the `to_dict` / `from_dict` / `to_json` / `from_json` / `clone` forwarders, add a comment block explaining:
  - Why these are intentional shims — Guardrail #1 + ~18 live production + test callers.
  - The canonical delegate that owns the real behavior — `ShipInstanceSerializer`.
  - The removal condition — once callers migrate to direct `ShipInstanceSerializer.to_dict(ship)` / `.from_dict(data)` / `.to_json(ship)` / `.from_json(s)` / `.clone(ship)` access.
- [x] Match the format of the existing 5b consumable shim comment block in the same file.

### Task 7.3: Verify no behavior change [Simple]
**Tests:** `pytest tests/unit/strategy/ship_instance/ -q`

- [x] Run the focused ship-instance suite. All tests must still pass — Phase 7 is comment-only, no behavior change.
  - **Result:** 128 passed.
- [x] Confirm `ship_instance.py` LOC change is exclusively comment lines (`+29` lines after Phase 7; was 561, now 590).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] 5d and 5e comment blocks present in `ship_instance.py`, matching 5b format
- [x] No code behavior changed — focused suite still green (128 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to note Phase 7 ran independently of the still-gated Phase 6
- [x] Decisions row added to `decisions.md` capturing the Codex consult driver
