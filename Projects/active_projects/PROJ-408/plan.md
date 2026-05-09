# PROJ-408: Tier 4 — Coverage gaps from PROJ-380..399 review (C-01..C-06)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add direct unit coverage for the gaps PROJ-380..399 reviews flagged | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09
**Active Phase:** Phase 1
**Last Action:** Project skeleton created from REMEDIATION_PLAN Tier 4 (C-01..C-06)
**Next Action:** Add the 3 missing direct unit tests (C-01, C-02, C-04). C-03 → Wave 5; C-05/C-06 already shipped in Wave 1.
**Blockers:** None

## Overview
The PROJ-380..399 review flagged 6 coverage gaps (C-01..C-06). Two of them (C-05, C-06) were folded into Wave 1 work (PROJ-404 added the negative save-shape tests; PROJ-401 added the missing-species_id regression). C-03 is an architectural decision (the raw `EnginePhaseError` defensive catch in the UI) that belongs to Wave 5 PROJ-409 — not a coverage task. **This project lands the remaining 3: C-01, C-02, C-04.**

## Goals (effective scope: C-01, C-02, C-04)

- **C-01 (PROJ-397)**: `EmpireBuildQueueWindow` constructor test currently verifies signature only via introspection. Add a real-construction test that exercises a code path through the class.
- **C-02 (PROJ-381)**: Facade conversion `EnginePhaseError` → `TurnFailedError` (`game/strategy/facade/strategy_session_facade.py:194-201`) has no direct unit test. The UI test exercises the boundary, not the facade. Add a focused facade unit test.
- **C-04 (PROJ-397)**: `PlanetSelectionWindow` facade threading lacks direct unit coverage. Add a unit test that constructs the window with a real (or close-to-real) facade and asserts the threading.

## Already-shipped (do not reopen)

- **C-05** — Wave 1 PROJ-404 added negative tests asserting legacy save shapes raise (`test_missing_components_raises_persistence_exception`, `test_legacy_resource_levels_field_is_not_accepted`, `test_from_dict_rejects_missing_*_complex_toggles`).
- **C-06** — Wave 1 PROJ-401 added `test_validate_rejects_passenger_load_with_missing_species_id`.

## Deferred to Wave 5 PROJ-409

- **C-03** — UI still imports + catches raw `EnginePhaseError` at `game/ui/screens/strategy_game_state_manager.py:19, 149-158`. This is the same item as MAJ-014. PROJ-409 ratifies or actively closes it.

## Scope
**In:**
- 3 new test functions (C-01, C-02, C-04). Possibly small refactors to existing tests if the new tests share a fixture.
- The new tests must exercise actual production code paths, not introspect type signatures.

**Out:**
- Any production change. If a coverage test reveals a real bug, surface it as a new blocker — don't try to fix the bug in this project.
- C-03 (deferred to PROJ-409).
- C-05, C-06 (already shipped).

## Key Files
| Component | File Path |
|-----------|-----------|
| C-01 production | `game/ui/screens/empire_build_queue_window.py` |
| C-01 test | `tests/unit/ui/screens/test_empire_build_queue_window.py` (extend) |
| C-02 production | `game/strategy/facade/strategy_session_facade.py:194-201` |
| C-02 test | `tests/unit/strategy/facade/test_strategy_session_facade.py` (or wherever — confirm) |
| C-04 production | `game/ui/screens/planet_selection_window.py` (confirm path) |
| C-04 test | corresponding test module |

## Source Evidence
- C-01: PROJ-397 review (reviewer noted introspection-only test).
- C-02: PROJ-381 review (`game/strategy/facade/strategy_session_facade.py:194-201`).
- C-04: PROJ-397 review.

## Verification
- [ ] Phase 1 checklist complete
- [ ] All 3 new tests pass (and confirm RED before fix-equivalent — for coverage tests, that's "exercise the code path and assert behavior").
- [ ] Focused suites for affected modules pass
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-408` passes
- [ ] User verified
