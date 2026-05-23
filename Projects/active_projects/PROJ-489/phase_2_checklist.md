# Phase 2: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-489 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address Codex audit finding F7 (doc drift across 3 docs describing pre-consolidation behavior). See `findings/audit_verification.md`.

---

## Tasks

### Task 2.1: Update docs/04_SERVICES.md ModifierLogicService section (F7) [Simple]
**File:** `docs/04_SERVICES.md`

- [x] At lines 269-273, rewrite the ModifierLogicService section to reflect the post-PROJ-489 reality: ModifierLogicService is now a thin facade over `ModifierService`, exposing `calculate_snap_value` as its only non-delegated method. It takes a `ModifierService` instance (not an `IRegistryProvider`), and no longer constructs `ComponentService` internally.
- [x] Bump the doc's "Last verified" timestamp to today.
- [x] Verify: `grep -n "IRegistryProvider\|ModifierLogicService" docs/04_SERVICES.md` returns descriptions consistent with the current code.

---

### Task 2.2: Update docs/guides/modifier_system.md (F7) [Simple]
**File:** `docs/guides/modifier_system.md`

- [x] Lines 98 and 285 currently state `ModifierManager.add_modifier()` enforces only type restrictions. That's no longer true after PROJ-489 — it now also enforces `allow_abilities` via delegation to canonical `ModifierService.is_modifier_allowed`.
- [x] Rewrite both lines to say: enforces `allow_types`, `deny_types`, AND `allow_abilities` (delegates to `ModifierService`).
- [x] Bump "Last verified" timestamp.

---

### Task 2.3: Update docs/guides/adding_modifiers.md (F7) [Simple]
**File:** `docs/guides/adding_modifiers.md`

- [x] Lines 128 and 162 — same issue as Task 2.2. Update to reflect `allow_abilities` is now enforced at add_modifier time.
- [x] Bump "Last verified" timestamp.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row for Phase 2 to `Complete`
- [x] Update plan.md Current State
- [x] Note in plan.md Current State: DI-2026-05-23-004 logged for pre-existing `efficient_engines` data bug surfaced by audit (out of scope)
