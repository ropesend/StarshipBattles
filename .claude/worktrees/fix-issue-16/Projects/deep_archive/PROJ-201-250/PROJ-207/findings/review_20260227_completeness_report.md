# PROJ-207 Completeness Audit Report

**Date:** 2026-02-27
**Auditor:** Claude Opus 4.6 (Completeness Review Agent -- Independent Re-Audit)
**Project:** Fleet Order System Unification
**Method:** Systematic trace of all goals to tasks, all tasks to goals, phase dependency verification, scope cross-reference, and integration with findings from three prior review reports (Design Pattern, Scope Gap, Plan-Code Alignment).

**Verdict:** CONSISTENT with 8 findings (0 blockers, 3 recommendations, 5 observations)

---

## Executive Summary

The PROJ-207 plan is internally consistent and well-structured. All 5 stated goals map to
concrete tasks with full coverage. All 15 tasks trace back to stated goals with no orphans.
Phase ordering respects declared dependencies. Complexity tags are accurate upon code
inspection. Eight findings are documented below, including two that synthesize issues raised
by the three prior review agents into actionable plan amendments. None are blocking.

**Task count note:** The plan states "15 validated findings" mapped to tasks. The prompt
describing this audit says "14 total" tasks but then lists 15. The actual checklists contain
15 tasks (2 + 3 + 2 + 3 + 5 = 15). The discrepancy arises because CP-005 was merged with
VC-002 into a single task (Task 2.2), reducing 15 findings to 14 unique finding IDs but
still producing 15 tasks. The correct count is **15 tasks covering 15 findings (14 unique
finding IDs since VC-002 and CP-005 are duplicates)**.

---

## 1. Goal-to-Task Mapping

### G1: Fix save/load data loss bugs (ODM-001, ODM-003)
| Finding ID | Task | Phase | Status |
|------------|------|-------|--------|
| ODM-001 | 1.1 | Phase 1 | Covered |
| ODM-003 | 1.2 | Phase 1 | Covered |

**Coverage: COMPLETE.** Both critical serialization bugs have dedicated tasks with detailed
subtask checklists. Task 1.1 creates the resolver; Task 1.2 fixes the serialization format.
The two tasks are correctly sequenced (1.2's `_planet_ref` output feeds into 1.1's resolver).

### G2: Close superweapon validation gaps (VC-001, VC-002, VC-007)
| Finding ID | Task | Phase | Status |
|------------|------|-------|--------|
| VC-001 | 2.1 | Phase 2 | Covered |
| VC-002 | 2.2 | Phase 2 | Covered (merged with CP-005) |
| VC-007 | 2.3 | Phase 2 | Covered |

**Coverage: COMPLETE.** All three validation gaps are addressed. Task 2.3 is correctly
identified as "belt-and-suspenders" defensive hardening after Tasks 2.1/2.2 close the
primary gaps. CP-005 (duplicate of VC-002 from a different review agent) is correctly
merged into Task 2.2.

### G3: Eliminate dual execution paths and inconsistent error handling (EP-001, EP-005)
| Finding ID | Task | Phase | Status |
|------------|------|-------|--------|
| EP-001 | 3.1 | Phase 3 | Covered |
| EP-005 | 3.2 | Phase 3 | Covered |

**Coverage: COMPLETE.** Both execution path issues have dedicated tasks. Design decisions
are documented (instant path authoritative for JOIN_FLEET; pop_order on movement failure).

### G4: Bring BUILD orders and FleetOrdersWindow into the command pipeline (CP-001, CP-002)
| Finding ID | Task | Phase | Status |
|------------|------|-------|--------|
| CP-001 | 4.2 | Phase 4 | Covered |
| CP-002 | 4.1 | Phase 4 | Covered |

**Coverage: COMPLETE.** Both pipeline bypass findings have dedicated tasks. Note: CP-003 is
also listed under G5 but its task (4.3) lives in Phase 4. See Finding F-01.

### G5: Remove duplicated code and dead lifecycle methods (CP-003, EP-002, EP-004, AU-002, AU-004, AU-005)
| Finding ID | Task | Phase | Status |
|------------|------|-------|--------|
| CP-003 | 4.3 | Phase 4 | Covered |
| EP-002 | 5.1 | Phase 5 | Covered |
| EP-004 | 5.2 | Phase 5 | Covered |
| AU-002 | 5.4 | Phase 5 | Covered |
| AU-004 | 5.5 | Phase 5 | Covered |
| AU-005 | 5.3 | Phase 5 | Covered |

**Coverage: COMPLETE.** All six finding IDs under this goal are addressed. CP-003 is in
Phase 4 rather than Phase 5, which is acceptable -- it is both a pipeline consistency fix
and a duplication removal.

**Summary: 0 unaddressed goals. All 15 findings map to concrete tasks.**

---

## 2. Task-to-Goal Mapping (Orphaned Task Check)

| Task | Finding ID(s) | Primary Goal | Traced? |
|------|---------------|--------------|---------|
| 1.1 | ODM-001 | G1 | Yes |
| 1.2 | ODM-003 | G1 | Yes |
| 2.1 | VC-001 | G2 | Yes |
| 2.2 | VC-002/CP-005 | G2 | Yes |
| 2.3 | VC-007 | G2 | Yes |
| 3.1 | EP-001 | G3 | Yes |
| 3.2 | EP-005 | G3 | Yes |
| 4.1 | CP-002 | G4 | Yes |
| 4.2 | CP-001 | G4 | Yes |
| 4.3 | CP-003 | G4/G5 (dual) | Yes |
| 5.1 | EP-002 | G5 | Yes |
| 5.2 | EP-004 | G5 | Yes |
| 5.3 | AU-005 | G5 | Yes |
| 5.4 | AU-002 | G5 | Yes |
| 5.5 | AU-004 | G5 | Yes |

**Result: 0 orphaned tasks.** Every task traces to at least one stated goal. No task
introduces work outside the project's stated objectives.

---

## 3. Phase Coherence Analysis

### 3.1 Phase Ordering and Dependencies

| Phase | Depends On | Declared? | Verified? |
|-------|-----------|-----------|-----------|
| Phase 1 (Save/Load) | None | N/A | Correct -- standalone serialization fixes |
| Phase 2 (Superweapon Validation) | None | N/A | Correct -- standalone validation additions |
| Phase 3 (Execution Path) | None | N/A | Correct -- standalone path cleanup |
| Phase 4 (Command Pipeline) | None | N/A | Correct -- standalone pipeline routing |
| Phase 5 (Code Hygiene) | Phase 3 | Yes (plan.md, design.md) | Correct -- see below |

**Phase 5 -> Phase 3 dependency verification:**
- Task 5.4 (replace dispatch god-method) explicitly notes: "After Task 5.2, BUILD branch is
  already removed" and "After Task 3.1, JOIN_FLEET branch is already removed."
- Task 5.2 is internal to Phase 5 (no cross-phase dependency issue).
- Task 3.1 (Phase 3) must complete before Task 5.4 (Phase 5) begins. This is satisfied by
  the phase ordering (Phase 3 before Phase 5).

**Intra-Phase 5 dependency:** Task 5.4 depends on Task 5.2 (within the same phase). The
checklist is ordered so 5.2 comes before 5.4. This is correct.

**Intra-Phase 2 dependency:** Task 2.3 is "belt-and-suspenders" after Tasks 2.1/2.2. The
checklist orders them 2.1 -> 2.2 -> 2.3. This is correct.

### 3.2 Task Placement Within Phases

All tasks are in functionally coherent phases:
- Phase 1: Both tasks address serialization/deserialization.
- Phase 2: All three tasks address superweapon validation/execution safety.
- Phase 3: Both tasks address execution path semantics.
- Phase 4: All three tasks address command pipeline routing.
- Phase 5: All five tasks address code hygiene (dead code, duplication, refactoring).

**One cross-concern task:** Task 4.3 (CP-003, auto-load helper extraction) serves both G4
(pipeline consistency) and G5 (code duplication). Its placement in Phase 4 is reasonable
since the auto-load logic lives in command handlers.

### 3.3 Complexity Tag Verification

| Task | Tagged | Rationale | Accurate? |
|------|--------|-----------|-----------|
| 1.1 | Medium | New `resolve_order_references()` method + integration with load path + tests | Yes |
| 1.2 | Simple | Single serialization format change in `to_dict()` | Yes |
| 2.1 | Simple | Add 1 keyword argument to 5 existing call sites | Yes |
| 2.2 | Simple | Add validator call to 5 mission handlers (copy from direct handler pattern) | Yes |
| 2.3 | Simple | Replace 4 `fleet.ships[0]` fallbacks with error handling | Yes |
| 3.1 | Simple | Remove from set constant + delete dead branch (6 lines) | Yes |
| 3.2 | Medium | 3 behavior changes + potential test assertion updates | Yes |
| 4.1 | Medium | New Command class + new Handler + registry registration + UI update | Yes |
| 4.2 | Simple | Route existing call through existing command (ClearFleetOrdersCommand exists) | Yes |
| 4.3 | Simple | Extract identical code blocks into shared helper | Yes |
| 5.1 | Medium | Delete 3 methods + verify no production callers + delete/update ~9 tests | Yes |
| 5.2 | Simple | Delete unreachable code block | Yes |
| 5.3 | Medium | Template method extraction from 6 methods (realistically 4-5, see F-04) | Yes |
| 5.4 | Medium | Registry pattern + method rename + interface update + 8+ test file updates | Yes |
| 5.5 | Simple | Replace inline path logic with existing helper | Yes |

**Result: All 15 complexity tags are accurate.** No task is significantly under- or
over-estimated.

### 3.4 Test Commands

Each phase checklist specifies targeted test commands for individual tasks and a full-suite
command (`pytest tests/ -n 12`) for phase completion. The targeted commands use appropriate
`-k` filters to scope test runs to relevant areas. This is consistent with the project's
TDD approach.

---

## 4. Scope Consistency

### 4.1 In-Scope Files vs. Task References

| Scope File | Referenced By Task(s) | In Scope List? | In Key Files Table? |
|------------|----------------------|----------------|---------------------|
| `fleet.py` | 1.1, 1.2, 3.1 | Yes | Yes |
| `command_handlers.py` | 2.1 (indirect), 4.1, 4.3, 5.5 | Yes | Yes |
| `fleet_order_processor.py` | 3.1, 5.1, 5.2, 5.4 | Yes | Yes |
| `fleet_movement_engine.py` | 3.2 | Yes | Yes |
| `action_execution_engine.py` | 5.2 | Yes | Yes |
| `superweapon_order_processor.py` | 2.3, 5.3 | Yes | Yes |
| `superweapon_command_handlers.py` | 2.1, 2.2 | Yes | Yes |
| `superweapon_validator.py` | 2.1 (indirect) | Yes | Yes |
| `fleet_orders_window.py` | 4.2 | Yes | Yes |
| `strategy_build_queue_manager.py` | 4.1 | Yes | Yes |
| **`commands.py`** | **4.1** | **Not listed** | **Not listed** |
| **`engines.py` (interfaces)** | **5.4** | **Not listed** | **Not listed** |

**Result: 2 files are modified by tasks but not listed in scope.** See Finding F-02.

### 4.2 Unused Scope Entries

Every file listed in the Scope "In" section and Key Files table is referenced by at least
one task. No scope entries are orphaned.

### 4.3 Out-of-Scope Boundaries

No task conflicts with the Out-of-Scope boundaries:
- No new order types or features are added (BUILD routing uses existing OrderType.BUILD)
- No combat AI changes
- No UI rendering/drawing code changes (fleet_orders_window.py change is event handling, not rendering)
- No galaxy generation changes
- No ship component definition changes

---

## 5. Cross-Reference with Prior Review Reports

Three prior review reports have been filed for PROJ-207:

1. **Design Pattern Report** (7 findings: F-001 through F-007)
2. **Scope Gap Report** (10 findings: SG-001 through SG-010)
3. **Plan-Code Alignment Report** (7 findings: F-001 through F-007)

### Integration Assessment

The prior reports collectively identified:
- **2 bugs** not in the plan (SG-001: enemy colony cleanup, SG-002: empty fleet after superweapon)
- **1 incorrect API reference** in Task 4.2 (Design F-001: `session.registries.components` does not exist; SG-005: `dispatch_command()` should be `handle_command()`)
- **1 chain-awareness issue** in Task 5.5 (Design F-004: `add_move_order_if_needed()` is not chain-aware)
- **1 template method scope clarification** (Design F-006: `process_self_destruct` diverges from pattern)
- **1 backward-compat language conflict** with CLAUDE.md policy (SG/Design overlap)
- **Multiple line number drift notes** (Alignment report: minor, non-blocking)

**These findings do not affect the completeness audit's core conclusion** -- all goals have
tasks and all tasks trace to goals. However, they identify implementation-time risks that
should be noted in the relevant checklists. See Findings F-05 through F-08 below.

---

## 6. Findings

### F-01: CP-003 Dual Goal Attribution Creates Minor Ambiguity
**Category:** Documentation Clarity
**Details:** Finding CP-003 (auto-load helper extraction) appears in Goal 5's parenthetical
list but its task (4.3) lives in Phase 4 ("Command Pipeline Consistency"). This dual
attribution is not incorrect -- CP-003 is both a pipeline consistency fix and a duplication
removal -- but a reader scanning only the Goal 4 line would not see CP-003 listed there.
**Impact:** Low. An implementer might wonder whether Task 4.3 belongs in Phase 5. The
current placement is correct.
**Proposed Resolution:** Optionally add "CP-003" to Goal 4's parenthetical list:
`Bring BUILD orders and FleetOrdersWindow into the command pipeline (CP-001, CP-002, CP-003)`
and note in Goal 5 that CP-003 is shared.

---

### F-02: Two Files Modified by Tasks But Not Listed in Scope or Key Files
**Category:** Scope Mismatch (Minor)
**Details:** Task 4.1 creates `IssueBuildOrderCommand` in `game/strategy/engine/commands.py`.
Task 5.4 renames `process_end_turn_orders()` to `execute_action_order()` which requires
updating the `IOrderProcessor` interface in `game/strategy/interfaces/engines.py`. Neither
file appears in the Scope "In" list or the Key Files table.
**Impact:** Low. Both files are discoverable during implementation. But the Scope section is
meant to be a complete inventory of modified files.
**Proposed Resolution:** Add to Scope "In" list and Key Files table:
- `game/strategy/engine/commands.py` -- IssueBuildOrderCommand (Task 4.1)
- `game/strategy/interfaces/engines.py` -- IOrderProcessor interface rename (Task 5.4)

---

### F-03: Task 2.1 Does Not Explain Why SelfDestructCommandHandler Is Excluded
**Category:** Documentation Gap (Observation)
**Details:** Task 2.1 lists 5 of 6 direct superweapon handlers needing `component_registry`
passed to their validator calls. `SelfDestructCommandHandler` is correctly excluded because
`validate_self_destruct()` validates ship IDs rather than abilities and does not accept a
`component_registry` parameter. However, the task does not explain the exclusion, which
could confuse an implementer who sees 6 handlers in the file but only 5 in the checklist.
**Impact:** Negligible. The implementer would check the validator signature and understand.
**Proposed Resolution:** Optionally add a note to Task 2.1: "Note: SelfDestructCommandHandler
is excluded because `validate_self_destruct()` validates ship IDs, not abilities, and does
not take a `component_registry` parameter."

---

### F-04: Task 5.3 Template Method Scope Is Overstated (6 methods claimed, 4-5 fit pattern)
**Category:** Complexity/Scope Accuracy
**Details:** Task 5.3 states "All 6 `process_*` methods repeat an identical skeleton." In
reality:
- **4 methods fit the full template:** `process_implode_planet`, `process_open_warp_point`,
  `process_close_warp_point`, `process_create_dyson_sphere`
- **`process_stellerate_star`** partially fits (suicide weapon with different ship lookup
  and multi-fleet destruction pattern)
- **`process_self_destruct`** diverges significantly (takes ship ID list, removes multiple
  ships, no ability lookup via `find_ship_with_ability()`)

This was also identified by the Design Pattern report (F-006) and the prior completeness
report (F-04).
**Impact:** Medium. An implementer attempting a single template for all 6 methods will
struggle when `stellerate_star` and `self_destruct` don't fit. The line-reduction estimate
("~530 lines to ~200") is also overstated if only 4 methods are covered.
**Proposed Resolution:** Update Task 5.3 to clarify:
- Template applies to 4 methods (implode, open_warp, close_warp, dyson_sphere) -- ~350 lines
- `process_stellerate_star` may partially benefit (optional template steps)
- `process_self_destruct` remains standalone (fundamentally different ship selection pattern)
- Adjust reduction estimate: "~350 lines of logic to ~120" for the 4 conforming methods

---

### F-05: Prior Reports Identified 2 Bugs Not Captured in Plan Tasks (SG-001, SG-002)
**Category:** Cross-Review Integration
**Details:** The Scope Gap report identified two bugs in superweapon execution that are
adjacent to Phase 2 and Phase 5 tasks but are not captured as explicit checklist items:

1. **SG-001 (enemy colony cleanup):** `process_implode_planet()` and
   `process_create_dyson_sphere()` only remove the planet from the attacking empire's
   colonies, not the victim empire's. `process_stellerate_star()` correctly iterates all
   empires. This is a data corruption risk.

2. **SG-002 (empty fleet after superweapon):** When a superweapon consumes the only ship in
   a fleet, the empty fleet is not removed from the empire. Unlike `process_colonize()` and
   `process_join_fleet()` which call `empire.remove_fleet(fleet)`, the 4 superweapon
   processors leave ghost fleets.

**Impact:** These are real bugs that could naturally be addressed during Phase 2 (SG-001 in
Task 2.3's error handling work) and Phase 5 (SG-002 in Task 5.3's template extraction). But
without explicit checklist items, they may be missed.
**Proposed Resolution:**
- Add a checklist item to Task 2.3 or create a new Task 2.4: "Pass `empires` to
  `process_implode_planet()` and `process_create_dyson_sphere()` to clean up victim empire
  colonies (matching `process_stellerate_star()` pattern)."
- Add a checklist item to Task 5.3: "In the template method, add fleet cleanup: if
  `len(fleet.ships) == 0` after ship removal, call `empire.remove_fleet(fleet)`."

---

### F-06: Task 4.2 References Incorrect API Names (Two Distinct Errors)
**Category:** Implementation Accuracy
**Details:** The Design Pattern report (F-001) and Scope Gap report (SG-005) together
identified two incorrect API references in Task 4.2:

1. `session.registries.components` does not exist. The correct accessor is
   `session.turn_engine._registries.components` (pattern used by
   `ColonizeMissionCommandHandler`).
2. `session.dispatch_command(cmd)` does not exist. The correct method is
   `session.handle_command(command)` (at `game_session.py` line 194).

Additionally, the Design Pattern report (F-002) notes that threading the session reference
to `FleetOrdersWindow` requires changes at three levels: `StrategyScreen` ->
`StrategyWindowManager` -> `FleetOrdersWindow`, which is slightly more effort than the
"Simple" tag implies for the threading portion (though the command infrastructure already
exists, per F-007).

**Impact:** Medium. An implementer following the checklist literally would encounter
`AttributeError` twice. The threading depth is also understated.
**Proposed Resolution:** Update Task 4.2 to:
- Reference `session.handle_command()` instead of `session.dispatch_command()`
- Note the three-file threading path for session reference
- Consider passing a callback closure from `StrategyScreen` instead of a full session reference (cleaner architectural boundary)

---

### F-07: Task 4.2 Is Simpler Than Described (ClearFleetOrdersCommand Already Exists)
**Category:** Documentation Gap (Positive)
**Details:** Task 4.2 shows sample code implying `ClearFleetOrdersCommand` needs to be
created, but the command class already exists in `commands.py` (line 104) and
`ClearOrdersCommandHandler` is already registered in `create_default_registry()` (line 628).
The Design Pattern report (F-007) confirmed this. No new Command or Handler class is needed.
**Impact:** Positive -- the task is easier than it appears. Only the call site change and
session threading are required.
**Proposed Resolution:** Add a note to Task 4.2: "`ClearFleetOrdersCommand` and
`ClearOrdersCommandHandler` already exist and are registered. Only the call site in
`fleet_orders_window.py` and session threading are needed."

---

### F-08: Design.md Backward-Compat Language Conflicts with CLAUDE.md Save Policy
**Category:** Policy Tension
**Details:** Design.md Dependencies & Risks item 4 states: "Old saves with the old format
need handling in from_dict (backward compat during transition is acceptable here since it's
a bug fix)." CLAUDE.md's System Migration Policy states: "Save files are disposable. Old
saves are not migrated -- they are discarded. Do not write compatibility shims or migration
code for save data."

The Task 1.2 checklist itself is clear and correct: change `to_dict()` to `_planet_ref`
format and rely on Task 1.1's resolver. No backward-compat code is specified. But the
design.md note could mislead an implementer into adding a shim.
**Impact:** Low. The checklist is authoritative over design.md for implementation instructions.
**Proposed Resolution:** Update design.md item 4 to: "Phase 1 changes Planet serialization
from full dict to `_planet_ref`. Per project policy, old saves are disposable -- no backward
compatibility shim is needed. The old format was broken (produced `None` targets), so there
are no valid saves to preserve."

---

## 7. Summary Table

| Category | Count | Severity |
|----------|-------|----------|
| Unaddressed Goals | 0 | -- |
| Orphaned Tasks | 0 | -- |
| Phase Ordering Issues | 0 | -- |
| Scope Mismatches | 1 (F-02) | Minor |
| Complexity Tag Issues | 0 | -- |
| Documentation Gaps | 3 (F-01, F-03, F-07) | Low |
| Scope/Accuracy Issues | 1 (F-04) | Medium |
| Cross-Review Bugs Not in Plan | 1 (F-05, covers 2 bugs) | Medium |
| Incorrect API References | 1 (F-06) | Medium |
| Policy Tensions | 1 (F-08) | Low |

---

## 8. Recommendations

### Priority 1: Should address before implementation begins
1. **F-02:** Add `commands.py` and `engines.py` to the Scope and Key Files sections.
2. **F-05:** Add explicit checklist items for the two bugs identified by the Scope Gap report
   (enemy colony cleanup, empty fleet removal) -- these are real data corruption risks.
3. **F-06:** Correct the two incorrect API references in Task 4.2 (`handle_command` not
   `dispatch_command`; `session.turn_engine._registries.components` not
   `session.registries.components`).

### Priority 2: Recommended improvements
4. **F-04:** Clarify Task 5.3 template method scope (4 of 6 methods, not all 6). Adjust
   line-reduction estimates.

### Priority 3: Nice-to-have (non-blocking observations)
5. **F-01:** Annotate CP-003's dual-goal attribution.
6. **F-03:** Note why SelfDestructCommandHandler is excluded from Task 2.1.
7. **F-07:** Note that ClearFleetOrdersCommand already exists (simplifies Task 4.2).
8. **F-08:** Align design.md backward-compat language with CLAUDE.md save policy.

---

## 9. Overall Assessment

The PROJ-207 plan is **thorough, well-organized, and ready for implementation** with the
three Priority 1 amendments above. The core structure is sound:

- **Goal coverage:** 100%. All 5 goals map to tasks; all 15 tasks trace to goals.
- **Phase structure:** Logically ordered by functional area with correctly declared dependencies.
- **Complexity accuracy:** All 15 tags are accurate upon code inspection.
- **Scope completeness:** 10 of 12 modified files are listed (2 minor omissions).
- **Cross-review integration:** 2 bugs from the Scope Gap report should be added as explicit
  checklist items to prevent them being overlooked during implementation.

The plan demonstrates strong internal consistency with no structural defects. The findings
above are refinements to improve implementation success, not corrections to fundamental
design or scoping errors.
