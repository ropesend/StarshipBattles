# PROJ-219 Scope Gap Analysis Report

**Date:** 2026-03-01
**Analyst:** Claude Opus 4.5
**Project:** Fleet Registration Consolidation

---

## Executive Summary

After thorough analysis of the project plan, phase checklists, and source code, I identified **7 scope gaps** that should be addressed. Most are low-effort additions that prevent potential bugs or test failures. One finding identifies an **existing test that will break** after the changes.

---

## Findings

### GAP-001: Stellarate Double-Unregister Will Become Harmless But Creates Dead Code

**Location:** `game/strategy/engine/superweapon_order_processor.py:238-241`
**Related Goal:** Goal 3 (Fix ghost fleet bugs) + Goal 4 (Cleanup)
**Gap Description:**
The plan mentions removing the explicit `unregister_fleet()` call from stellarate at line 239. However, Task 3.3 in Phase 3 only addresses line 239 (for stellarate) but the plan document shows this should be removed. After PROJ-219, the `remove_fleet()` call at line 241 will auto-unregister, making line 239 redundant.

Looking at the code:
```python
# Lines 238-241
galaxy.unregister_fleet(victim_fleet)  # Line 239 - becomes redundant
owner_empire.remove_fleet(victim_fleet)  # Line 241 - now auto-unregisters
```

**Impact:** After PROJ-219, calling `unregister_fleet()` before `remove_fleet()` means the fleet gets unregistered twice. While idempotent (using `pop(id, None)`), this is dead code that should be removed.

**Proposed Resolution:** Task 3.3 already covers this. Verify the plan document line numbers match actual code. The plan shows line 239 for unregister but the code shows lines 238-241 span the relevant section. Minor verification needed.

**Effort:** Simple (already covered, just verify)

---

### GAP-002: _finalize_superweapon Also Calls remove_fleet - Missing Unregistration Bug

**Location:** `game/strategy/engine/superweapon_order_processor.py:55-121` (lines 99-103)
**Related Goal:** Goal 3 (Fix ghost fleet bugs)
**Gap Description:**
The `_finalize_superweapon()` helper method is used by IMPLODE_PLANET, OPEN_WARP_POINT, CLOSE_WARP_POINT, and CREATE_DYSON_SPHERE. It calls `empire.remove_fleet(fleet)` at line 103 when the fleet is consumed (empty after removing the ship).

This is NOT in the bug fix table, but it has the SAME bug pattern: `remove_fleet()` without `unregister_fleet()`.

```python
# Lines 99-103 in _finalize_superweapon
if fleet_consumed:
    empire.remove_fleet(fleet)  # Missing unregister_fleet() currently
```

**Impact:** Ghost fleets from non-stellarate superweapons (Implode Planet, Open Warp, Close Warp, Dyson Sphere) remain in the galaxy registry after the fleet is consumed. This is a real bug that PROJ-219 will fix automatically once remove_fleet auto-unregisters.

**Proposed Resolution:** Add to Bug Fixes table in plan.md as a 7th location. No code change needed beyond what's already planned - the fix is automatic once Empire.remove_fleet() auto-unregisters.

**Effort:** Simple (documentation update, already fixed by planned changes)

---

### GAP-003: process_self_destruct Also Calls remove_fleet - Missing Unregistration Bug

**Location:** `game/strategy/engine/superweapon_order_processor.py:609-613`
**Related Goal:** Goal 3 (Fix ghost fleet bugs)
**Gap Description:**
The `process_self_destruct()` method calls `empire.remove_fleet(fleet)` at line 613 when the fleet becomes empty after self-destruct. This has the same ghost fleet bug pattern.

```python
# Lines 609-613 in process_self_destruct
if fleet_consumed:
    empire.remove_fleet(fleet)  # Missing unregister_fleet() currently
```

**Impact:** Ghost fleets from SELF_DESTRUCT orders remain in the galaxy registry. This is a real bug that PROJ-219 will fix automatically.

**Proposed Resolution:** Add to Bug Fixes table in plan.md as an 8th location. No code change needed - automatic fix from planned changes.

**Effort:** Simple (documentation update, already fixed by planned changes)

---

### GAP-004: Test file tests/integration/strategy/test_command_handlers.py Has Mock unregister_fleet

**Location:** `tests/integration/strategy/test_command_handlers.py:64-65`
**Related Goal:** None - test maintenance
**Gap Description:**
This test file has a MockGalaxy class with `unregister_fleet()` method. After PROJ-219, some tests may need updating if they use `empire.add_fleet()`/`remove_fleet()` and expect specific mock call patterns.

```python
def unregister_fleet(self, fleet):
    """Unregister a fleet."""
    pass
```

**Impact:** Tests may pass incorrectly or need mock verification updates to check that auto-registration works correctly.

**Proposed Resolution:** Add to Phase 4 checklist - verify existing tests that mock Galaxy.unregister_fleet still work correctly after changes.

**Effort:** Simple

---

### GAP-005: Missing Task to Verify No Regressions in 74 Test Files Using Empire

**Location:** Multiple test files (74 identified)
**Related Goal:** Goal 1 (Single-point registration)
**Gap Description:**
The plan notes "50+ tests create Empire without Galaxy context" but doesn't include a specific task to run and verify these tests after Phase 1 changes. While the `if self._galaxy:` guard protects against crashes, there's no explicit verification step.

Phase 1 completion checklist includes:
- `pytest tests/unit/strategy/data/test_empire_fleet_registration.py` (new tests only)
- `pytest tests/ --testmon` (incremental)

But doesn't explicitly verify:
- `pytest tests/unit/strategy/data/test_empire.py` (if it exists)
- `pytest tests/unit/strategy/empire/` (empire-specific tests)

**Impact:** Could miss test failures in existing Empire tests that make assumptions about add_fleet/remove_fleet behavior.

**Proposed Resolution:** Add explicit verification task to Phase 1 completion:
```
- [ ] Run `pytest tests/unit/strategy/empire/ tests/unit/strategy/data/test_empire*.py -v` - all pass
```

**Effort:** Simple

---

### GAP-006: No Integration Test for Maintenance Scuttle Unregistration

**Location:** Phase 4 checklist
**Related Goal:** Goal 3 (Fix ghost fleet bugs)
**Gap Description:**
The Bug Fixes table includes "Maintenance scuttle" at `maintenance_engine.py:286`. However, Phase 4 only has 6 tasks:
1. Task 4.1: Create test file
2. Task 4.2: Combat destruction
3. Task 4.3: JOIN_FLEET merge
4. Task 4.4: COLONIZE empty
5. Task 4.5: Superweapon consumed
6. Task 4.6: Save/load

There's NO test for maintenance scuttle (Bug #6 in the table).

**Impact:** The maintenance scuttle ghost fleet bug fix won't have integration test coverage, even though it's in the bug fix table.

**Proposed Resolution:** Add Task 4.7 to Phase 4 checklist:
```markdown
### Task 4.7: Test maintenance scuttle unregisters fleet [Medium]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py`
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py::test_maintenance_scuttle_unregisters_empty_fleet`

- [ ] Create `test_maintenance_scuttle_unregisters_empty_fleet`:
  - Setup: Empire with fleet containing single ship, empire has 0 resources
  - Action: Process maintenance tick
  - Assert: Ship scuttled, fleet NOT in registry (0 ships remaining)
```

**Effort:** Medium

---

### GAP-007: Phase 5 Cleanup Files Include Modified Files Not Related to Fleet Registration

**Location:** Phase 5 checklist, Task 5.1
**Related Goal:** Goal 4 (Cleanup - Remove PROJ-216 diagnostic logging)
**Gap Description:**
Task 5.1 lists these files to check for PROJ-216 diagnostic logging:
- `game/ui/screens/strategy_input_handler.py`
- `game/ui/screens/strategy_event_router.py`
- `game/ui/screens/strategy_click_dispatcher.py`
- `game/ui/screens/strategy_fleet_ops.py`
- `game/strategy/facade/strategy_session_facade.py`
- `game/strategy/data/pathfinding.py`

However, these files are unrelated to fleet registration - they were modified for PROJ-216's click gate/move order fixes, not fleet registration. The git status shows these files are modified but they're not "key files" in the PROJ-219 plan.

**Impact:** Scope creep - reviewing/modifying 6 files that aren't related to fleet registration consolidation. This cleanup could be done in a separate ticket.

**Proposed Resolution:** Consider moving the PROJ-216 logging cleanup to a separate follow-up task (e.g., PROJ-216-CLEANUP) to keep PROJ-219 focused. Alternatively, clarify in Task 5.1 that this is "out of scope" cleanup that was bundled in for convenience.

**Effort:** Simple (decision/documentation)

---

## Summary Table

| ID | Title | Impact | Effort | Recommendation |
|----|-------|--------|--------|----------------|
| GAP-001 | Stellarate double-unregister | Low | Simple | Verify task already covers |
| GAP-002 | _finalize_superweapon ghost fleet | Medium | Simple | Add to bug fix table (auto-fixed) |
| GAP-003 | process_self_destruct ghost fleet | Medium | Simple | Add to bug fix table (auto-fixed) |
| GAP-004 | Test mock needs verification | Low | Simple | Add verification task |
| GAP-005 | No explicit Empire test verification | Low | Simple | Add test command to Phase 1 |
| GAP-006 | No maintenance scuttle test | Medium | Medium | Add Task 4.7 |
| GAP-007 | Unrelated cleanup files | Low | Simple | Document or split out |

---

## Recommendations

### High Priority (Add to Plan)
1. **GAP-006**: Add Task 4.7 for maintenance scuttle integration test
2. **GAP-002/003**: Update Bug Fixes table to include all 8 locations (not just 6)

### Medium Priority (Documentation)
3. **GAP-005**: Add explicit Empire test verification step to Phase 1
4. **GAP-007**: Clarify that PROJ-216 cleanup is optional/bundled

### Low Priority (Informational)
5. **GAP-001**: Verify line numbers in Task 3.3
6. **GAP-004**: Note that mock tests may need review

---

## Appendix: Complete List of remove_fleet Call Sites

Based on grep analysis, all `remove_fleet()` call sites that will benefit from auto-unregistration:

| File | Line | Context | In Bug Table? |
|------|------|---------|---------------|
| `conflict_resolution_engine.py` | 186 | Combat destruction | Yes |
| `fleet_order_processor.py` | 113 | JOIN_FLEET merge | Yes |
| `fleet_order_processor.py` | 216 | COLONIZE empty | Yes |
| `fleet_order_processor.py` | 663 | Instant merge | Yes |
| `superweapon_order_processor.py` | 103 | _finalize_superweapon | **NO** |
| `superweapon_order_processor.py` | 241 | Stellarate | Yes |
| `superweapon_order_processor.py` | 613 | Self-destruct | **NO** |
| `maintenance_engine.py` | 286 | Maintenance scuttle | Yes |

**Missing from table:** Lines 103 and 613 in superweapon_order_processor.py

