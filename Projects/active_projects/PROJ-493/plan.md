# PROJ-493: SuperweaponValidator DI seam introduction

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-493` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-493 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add validator DI seam to SuperweaponOrderProcessor (production change) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate 16 test sites from static patching to constructor injection | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Planning
**Last Action:** Project scaffolded from PROJ-479 deferred Task 3.14 per Codex consult 20260523T125621Z_plan-PROJ-479-followthrough
**Next Action:** Phase 1 Task 1.1 — write the failing test that constructs `SuperweaponOrderProcessor` with a stub validator and asserts the validator is consulted.
**Blockers:** None. This is the ONLY confirmed production DI seam gap from PROJ-479's deferred CAT-6 set per Codex analysis.
**Context:** `SuperweaponOrderProcessor.__init__` accepts `event_bus`, `empire_mutator`, `nav_service` but no validator dep (`game/strategy/engine/superweapon_order_processor.py:62-79`). The processor calls `SuperweaponValidator.find_ship_with_ability(...)` statically at `:275-282`. 16 tests patch this static path (`tests/unit/strategy/engine/test_superweapon_order_processor.py:131,166,201,622,669,708,749,786,854,910,1009,1049,1098,1132,1181,1239`). The fix is to follow the existing constructor-injection pattern used by the other 3 dependencies.

## Overview
Introduce a `validator` constructor parameter to `SuperweaponOrderProcessor` following the existing lazy-default pattern used for `empire_mutator` and `nav_service`. Then migrate all 16 test sites from patching the static method to injecting a stub validator. Resolves PROJ-479 Phase 3 Task 3.14.

## Goals
- Add `validator: Optional[Any] = None` constructor parameter to `SuperweaponOrderProcessor` with lazy default (Phase 1)
- Route all internal `SuperweaponValidator.find_ship_with_ability(...)` calls through the injected/defaulted validator (Phase 1)
- Migrate 16 deferred tests from `patch('SuperweaponValidator.find_ship_with_ability')` to passing a stub validator via constructor (Phase 2)
- Document the new seam in `docs/02_PATTERNS.md` if not already covered (Phase 1)

## Scope
**In:**
- PROJ-479 Phase 3 Task 3.14 (SuperweaponValidator DI introduction)
- Production change: `game/strategy/engine/superweapon_order_processor.py`
- Test migration: `tests/unit/strategy/engine/test_superweapon_order_processor.py` (16 sites)
- Possible incoming task: Phase 3 Task 3.20 second bullet (if PROJ-491 Phase 4 investigation routes it here)

**Out:**
- CAT-6 test-side mechanical rewrites — PROJ-491
- HLP cluster mechanical sweeps — PROJ-492
- ActionExecutionEngine test rewrite (DI seam already exists) — PROJ-491 Phase 3
- Any other "speculative" production seam introduction — only do confirmed seams. Per Codex consult, no other PROJ-479 deferred task is a confirmed seam gap on current evidence.

## Key Files
| Component | File Path |
|-----------|-----------|
| SuperweaponOrderProcessor (production change) | `game/strategy/engine/superweapon_order_processor.py:62-79, 275-282` |
| SuperweaponValidator (read-only — protocol) | `game/strategy/validation/superweapon_validator.py` |
| Test file (16 sites to migrate) | `tests/unit/strategy/engine/test_superweapon_order_processor.py` |
| DI pattern reference | `docs/02_PATTERNS.md:22,88,106,678` |

## Related Documents
- [design.md](design.md) - Approach + DI pattern rationale
- [decisions.md](decisions.md) - Why only this one seam (not speculative others)
- [manifest.md](manifest.md) - File list
- [findings/source_review.md](findings/source_review.md) - Pointer to PROJ-479 + Codex consult

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] No remaining `patch('SuperweaponValidator.find_ship_with_ability')` in test_superweapon_order_processor.py
- [ ] Audit passed
- [ ] User verified
