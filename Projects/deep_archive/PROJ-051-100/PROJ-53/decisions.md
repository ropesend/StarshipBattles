# PROJ-52: Decision Log

## DEC-001: No Backwards Compatibility
**Date:** 2026-01-31
**Decision:** Remove all legacy patterns with NO backwards compatibility layer
**Rationale:** User explicitly requested breakage to force fixing all dependencies
**Impact:** High - will cause immediate test failures and potentially runtime errors until all code is migrated

## DEC-002: AmmoGeneration Uses ResourceGeneration
**Date:** 2026-01-31
**Decision:** Do not create a special `AmmoGeneration` ability class. Use `ResourceGeneration` with `resource: "ammo"` instead.
**Rationale:** Consistent with the generic resource system design. No special behavior needed for ammo vs energy generation.
**Impact:** Low - just need to update JSON configs

## DEC-003: Shields Remain Separate
**Date:** 2026-01-31
**Decision:** Shield system (`max_shields`, `current_shields`, `shield_regen_rate`) remains outside ResourceRegistry for this project
**Rationale:** Shield migration is a larger architectural change. Focus on fuel/energy/ammo first.
**Impact:** None - shields already work, just not unified

## DEC-004: Phase Order - Remove Compatibility First
**Date:** 2026-01-31
**Decision:** Remove compatibility layer in Phase 1 BEFORE migrating JSON/code
**Rationale:** This will cause immediate breakage that guides us to all locations needing fixes. Breakage is the goal.
**Impact:** High - tests will fail immediately after Phase 1, guiding Phase 2-5 work

## DEC-005: Validation Warning Text
**Date:** 2026-01-31
**Decision:** Keep "Needs Fuel Storage" / "Needs Energy Storage" warning text for now
**Rationale:** These are user-facing messages that are clear. Can be made generic in future project.
**Impact:** None - cosmetic only
