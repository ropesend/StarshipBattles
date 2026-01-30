# PROJ-42: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-28 | Project initialized | Starting point for Backward Compatibility and Legacy Pattern Cleanup |
| 2026-01-28 | Delete FleetMovementSimulator immediately | Swarm analysis confirms 0 usages, 0 test dependencies; all functionality in FleetNavigationService |
| 2026-01-28 | Keep _ValidatorProxy and _ProfilerProxy | These solve real circular import and thread-safety issues; not legacy patterns |
| 2026-01-28 | Keep WIDTH/HEIGHT re-exports in constants.py | 64 files depend on these; refactoring cost too high for minimal benefit |
| 2026-01-28 | Keep ValidationResult dual patterns | Legitimate cross-layer bridge between simulation (error list) and UI (message property) |
| 2026-01-28 | Keep MIGRATABLE_VERSIONS in SaveGameService | Player data protection; removing would break existing saves |
| 2026-01-28 | Complete PROJ-38 before removing IRegistryProvider | 80+ tests depend on IRegistryProvider; must migrate callers first |
| 2026-01-28 | Standardize on instance methods for services | Static method patterns create confusing APIs; instance DI is cleaner |
| 2026-01-28 | Add format version fields to serialization | Enables future format migrations without type sniffing |
| 2026-01-28 | 6-phase approach for safe incremental delivery | Each phase can be committed independently; allows rollback if issues |

---

## Patterns Explicitly KEPT (Not Legacy, Just Different)

The following patterns were analyzed and determined to NOT be legacy issues requiring cleanup:

### _ValidatorProxy (ship.py:29-34)
**Status:** KEEP
**Reason:** Prevents circular imports during module initialization. Validator requires registries that may not exist at import time. This is an intentional architectural pattern, not technical debt.

### _ProfilerProxy (profiling.py:137-140)
**Status:** KEEP
**Reason:** Thread-safe lazy initialization of profiler singleton. Profiling is optional; proxy avoids singleton overhead if unused. Good pattern.

### WIDTH/HEIGHT re-exports (constants.py:29-33)
**Status:** KEEP (Too Many Dependents)
**Reason:** 64 files import these. Refactoring cost exceeds benefit. Re-export is only 3 lines.

### ValidationResult dual patterns (validation.py:25-135)
**Status:** KEEP (Cross-Layer Bridge)
**Reason:** Successfully bridges incompatible validation paradigms:
- Simulation layer: expects error lists for accumulation
- Strategy/UI layer: expects single message for display
This is well-designed DTO, not legacy code.

### MIGRATABLE_VERSIONS (save_game_service.py)
**Status:** KEEP (Player Data Protection)
**Reason:** Removing would break existing player saves. Keep indefinitely or announce deprecation window.

---

## Patterns Deferred for Future Work

### LPH-011: ShipControllableAdapter
**Status:** LOW PRIORITY
**Reason:** Needed for IControllable interface. Works correctly. Refactor only if IControllable protocol changes.

### LPH-012: ShipCombatMixin
**Status:** LOW PRIORITY
**Reason:** Thin facade kept during PROJ-12. Works correctly. Remove when Ship class decomposition completes.

### LPH-014: ComponentRef tuple methods
**Status:** LOW PRIORITY
**Reason:** `from_tuple()` and `to_tuple()` provide backward compatibility for old code. Low impact to keep.

### LPH-017: total_defense_score alias
**Status:** LOW PRIORITY
**Reason:** Aliased as `to_hit_profile` for UI compatibility. Simple alias, works correctly.

### LPH-021: Placeholder Technology System
**Status:** INFO ONLY
**Reason:** Tech tree not yet implemented. This is a known stub, not legacy code.

### LPH-022: Dual Module Import Prevention
**Status:** MEDIUM PRIORITY (Future)
**Reason:** Circular import workaround in `game/ui/__init__.py`. Should resolve properly but works for now.

---

### LPH-020: _ProfilerProxy
**Status:** KEEP
**Reason:** Thread-safe lazy initialization pattern. Already documented above in "Patterns Explicitly KEPT".

---

## Decisions Made During Implementation

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-29 | Phase 1 cleanup complete | Removed FleetMovementSimulator (331 LOC), GameState aliases, dead _migrate_temp_designs method |
| 2026-01-29 | V1 modifier format detection kept | The detection code in modifier_schema.py is validation, not handling - returns False for V1 |
