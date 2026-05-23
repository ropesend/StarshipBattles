# Phase 3: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-493 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Resolve the one VERIFIED + IN-SCOPE finding from the Codex mid-project-review audit (response.md in `AgentCoordination/Scratchpad/Consult/20260523T152717Z_audit-PROJ-493/`). Verification table at `findings/audit_verification.md`.

---

## Tasks

### Task 3.1: Tighten `StubValidator.find_ship_with_ability` signature [Simple]
**File:** `tests/unit/strategy/engine/test_superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py -v`

- [x] The current stub signature is `find_ship_with_ability(self, *args, **kwargs)` at lines 115-117. Production code calls it as `find_ship_with_ability(fleet, ability_name, component_registry)` (per the real `SuperweaponValidator` at `game/strategy/validation/superweapon_validator.py:17-33`). Replace `*args, **kwargs` with the explicit parameter list `(self, fleet, ability_name, component_registry)` so the stub catches signature drift.
- [x] Update the recorded-calls structure if needed (existing tests assert `args[0]`, `args[1]`, `args[2]` — preserve that contract by recording positional args as a tuple).
- [x] Verify: `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py -v` passes all 28 tests.

**Notes:** Tightened the signature inline (orchestrator did this directly rather than spawning a subagent; the edit was 3 lines). Existing assertions on `args[0,1,2]` preserved by packing the three positional args as `(fleet, ability_name, component_registry)` into the `calls` list's args slot. Test result: 28 passed in 1.55s.

---

### Task 3.2: Log the 13 out-of-scope leftover patch sites as a discovered issue [Simple]
**File:** `AgentCoordination/discovered_issues/log.jsonl` (via `/claude-di-log`)
**Tests:** N/A (logging only)

- [x] Log via `/claude-di-log` (or directly invoke `python Tools/agent_coordination/log_discovered_issue.py` if that's the canonical path) a single discovered-issue entry covering the 13 leftover `patch(...SuperweaponValidator.find_ship_with_ability)` sites Codex identified outside PROJ-493's manifest:
  - `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py:320,352,406,609`
  - `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py:140,184,329,418,455,502`
  - `tests/unit/strategy/engine/test_superweapon_event_payloads.py:273`
  - `tests/unit/strategy/engine/test_superweapon_edge_cases.py:580,624`
- [x] In the entry, link back to PROJ-493 as the canonical seam these sites should migrate to (constructor injection of a stub validator via the new `validator=` parameter).
- [x] Verify: entry is appended to `AgentCoordination/discovered_issues/log.jsonl`.

**Notes:** Logged as DI-2026-05-23-007. Category: test-gap. Severity: medium. Canonical location set to the first site (`test_superweapon_order_processor_gaps.py:320`); description and suggested_action enumerate all 13 sites and point to the PROJ-493 Phase 2 StubValidator pattern (`tests/unit/strategy/engine/test_superweapon_order_processor.py:102-160`).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
