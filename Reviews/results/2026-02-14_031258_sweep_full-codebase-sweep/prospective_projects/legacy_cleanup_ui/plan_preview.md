# Plan: Legacy Cleanup - UI and Services

## Project Information
- **Project ID:** TBD (will be assigned on creation)
- **Created:** 2026-02-14
- **Source:** Sweep 2026-02-14_031258

## Objective

Remove dead code, clean up migration artifacts, and eliminate defensive patterns that mask bugs.

## Current State

- BattleOrchestrator is completely unused (99 lines dead code)
- Defensive getattr patterns mask missing attributes
- Various unused methods and fields exist
- Inconsistent DI patterns in services
- Legacy fallback patterns from incomplete migrations

## Target State

- No dead code modules
- Type-safe attribute access (no defensive getattr)
- Consistent DI patterns in UI services
- Legacy fallback patterns removed or documented

## Phases

### Phase 1: Critical Dead Code Removal
**Files to delete:**
- `game/ui/orchestration/battle_orchestrator.py`
- `game/ui/orchestration/__init__.py` (if empty after)

**Verification:**
- Grep for BattleOrchestrator imports (should find none)
- Run tests to verify no breakage

### Phase 2: Unused Methods and Fields
**Files to modify:**
- `game/ui/services/vehicle_class_service.py` - remove get_max_mass(), get_type_for_class()
- `game/simulation/battle_config.py` - remove isolated field
- `game/simulation/managers/battle_state.py` - remove validate_state()
- `game/core/error_codes.py` - remove unused error codes
- `game/core/protocols.py` - remove is_camera TypeGuard

### Phase 3: Defensive Pattern Audit
**Files to audit:**
- `game/ui/services/battle_ui_service.py` - audit all getattr usages
- `game/ai/controller.py` - audit getattr fallbacks

**For each getattr:**
- If attribute guaranteed: replace with direct access
- If attribute optional: document why and keep
- If masking bug: fix the bug

### Phase 4: DI Pattern Alignment
**Files to modify:**
- `game/ui/services/component_service.py` - require registry_provider
- Update all callers to provide registry_provider
- Have is_modifier_allowed delegate to ModifierService

### Phase 5: Minor Cleanup
**Files to modify:**
- Remove unused imports (multiple files)
- Remove empty __init__ methods
- Remove disabled features (pass statements)
- Remove legacy pattern comments without code
- Update documentation comments

## Checklist

### Phase 1: Critical
- [ ] Verify BattleOrchestrator not imported
- [ ] Delete battle_orchestrator.py
- [ ] Delete orchestration/ if empty
- [ ] Run tests

### Phase 2: Unused Code
- [ ] Remove VehicleClassService unused methods
- [ ] Remove BattleConfig.isolated
- [ ] Remove validate_state()
- [ ] Remove unused error codes
- [ ] Remove is_camera TypeGuard

### Phase 3: Defensive Patterns
- [ ] Audit battle_ui_service.py getattr
- [ ] Audit controller.py getattr
- [ ] Fix or document each case

### Phase 4: DI Alignment
- [ ] Update ComponentService constructor
- [ ] Update callers
- [ ] Delegate is_modifier_allowed

### Phase 5: Minor
- [ ] Remove unused imports
- [ ] Clean empty methods
- [ ] Remove dead pass statements
- [ ] Remove stale comments

## Dependencies

- None - can run independently

## Risks

- Some "unused" code may have callers discovered later
- Defensive patterns may be hiding real bugs (good to find)
