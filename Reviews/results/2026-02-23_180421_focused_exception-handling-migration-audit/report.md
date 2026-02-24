# Review Report: Exception Handling Migration Audit

## Metadata
- **Date:** 2026-02-23
- **Type:** Focused Review — Migration Mapping / Impact Analysis
- **Description:** Comprehensive audit of the gap between PROJ-45 custom exception infrastructure and actual codebase adoption, with actionable migration mapping
- **Agents Used:** 7 (ValueError Mapper, Generic Exception Mapper, Caller Impact Analyzer, Error Code Gap Analyzer, Catch Quality Auditor, Deserialization Auditor, Test Impact Analyzer)

## Executive Summary

The custom exception hierarchy (PROJ-45) provides 10 exception classes, 19 error codes, and comprehensive documentation — but adoption is critically low. This audit maps every change needed for full migration.

### Key Numbers

| Metric | Count |
|--------|-------|
| **Raises to migrate** | **63** (46 ValueError + 17 generic) |
| **Raises to keep as-is** | **6** (3 TypeError protocol, 3 KeyError dict-like) |
| **Except blocks to update** | **36** (game code catches) |
| **Except blocks unchanged** | **49** (34 stdlib + 15 intentional broad) |
| **Tests to update** | **80** (26 ValueError + 3 RuntimeError + 51 TypeError) |
| **Tests unchanged** | **46** (stdlib/protocol behavior) |
| **Deserialization methods needing validation** | **15** of 20 (4 NO_VALIDATION, 11 PARTIAL) |
| **New error codes needed** | **3** (V002, V003, C003) |
| **New exception classes needed** | **0** |
| **Catch quality issues** | **16** (1 Critical, 10 Major, 5 Minor) |

### Overall Assessment
The infrastructure is excellent but adoption is ~5%. Migration is **mechanically straightforward** — 58 of 63 raises are Simple effort (just swap exception class + add error code + add context dict). The major complexity is in the **persistence tier** (save/load) where broad tuple catches need coordinated refactoring.

---

## Migration Breakdown by Exception Type

### ValueError (46 raises → all migrate)
| Module | Count | Simple | Medium | Complex | P1 | P2 | P3 |
|--------|-------|--------|--------|---------|-----|-----|-----|
| Assets | 1 | 1 | 0 | 0 | 0 | 0 | 1 |
| Simulation | 10 | 8 | 2 | 0 | 3 | 6 | 1 |
| Strategy | 18 | 17 | 1 | 0 | 3 | 14 | 1 |
| UI | 17 | 15 | 2 | 0 | 5 | 10 | 2 |
| **Total** | **46** | **41** | **5** | **0** | **11** | **30** | **5** |

### Generic Exceptions (23 found → 17 migrate, 6 keep)
| Type | Total | Migrate | Keep | Target Exception |
|------|-------|---------|------|-----------------|
| RuntimeError | 4 | 4 | 0 | StateException, MissingResourceException, ValidationException |
| TypeError (DI) | 13 | 13 | 0 | ValidationException (NOT_INITIALIZED) |
| TypeError (Protocol) | 3 | 0 | 3 | Keep — Python protocol compliance |
| KeyError | 3 | 0 | 3 | Keep — dict-like protocol |
| Bare Exception | 0 | 0 | 0 | N/A |

---

## Proposed Project Phases

### Phase 1: Infrastructure (error codes + imports) — ~1 hour
1. Add 3 new error codes to `game/core/error_codes.py`:
   - V002: SCHEMA_VALIDATION_ERROR — missing fields, invalid structure
   - V003: MISSING_ENTITY — referenced entity not found
   - C003: MISSING_DEPENDENCY — required DI parameter missing
2. Verify all existing error codes are importable and documented

### Phase 2: Strategy Loaders (18 ValueErrors) — ~2 hours
- `system_blueprints_loader.py` — 15 ValueError → ValidationException
- `astrophysics_loader.py` — 7 ValueError → ValidationException
- `galaxy_layouts_loader.py` — 2 ValueError → ValidationException/ResourceException
- `density_map.py` — 5 ValueError → ValidationException
- **All Simple effort, no callers to update**
- Update 6 tests in `test_density_map.py`, `test_layout_loader.py`, `test_system_blueprints.py`

### Phase 3: Simulation Core (10 ValueError + 4 RuntimeError + 13 TypeError DI) — ~3 hours
**ValueError migrations:**
- `battle_engine.py` — 3 ValueError → ValidationException (NOT_INITIALIZED), P1
- `battle_state_manager.py` — 1 ValueError → ValidationException (INVALID_STATE), P2, BREAKING
- `abilities/base.py` — 2 ValueError → ValidationException (VALIDATION_FAILED), P2, BREAKING
- `stat_keys.py` — 1 ValueError → ValidationException, P2
- `battle_mode_handler.py` — 1 ValueError → ValidationException, P3
- `ship_serialization.py` — 1 ValueError → ValidationException, P2

**RuntimeError migrations:**
- `ai_factory.py` — 1 RuntimeError → StateException (NOT_INITIALIZED), P2
- `battle_state_manager.py` — 1 RuntimeError → StateException (INVALID_STATE), P2
- `ship_loader.py` — 1 RuntimeError → MissingResourceException (RESOURCE_NOT_FOUND), P1

**TypeError DI migrations (13 all to ValidationException NOT_INITIALIZED):**
- `component.py` (3), `ship.py` (1), `ship_serialization.py` (1), `battle_state.py` (1)
- `ship_validator.py` (2), `design_loader.py` (1), `vehicle_design_service.py` (1)
- `modifier_service.py` (1), `resupply_engine.py` (1), `resource_management_engine.py` (1)

**Tests to update:** ~40 tests (DI tests, ability tests, engine tests, loader tests)

### Phase 4: Game Config + UI (17 ValueError + 1 RuntimeError) — ~2 hours
**Config:**
- `game_config.py` — 3 ValueError → ValidationException (OUT_OF_RANGE, VALIDATION_FAILED), P1

**UI:**
- `build_queue_screen.py` — 4 ValueError → ValidationException (NOT_INITIALIZED), P1
- `vehicle_class_service.py` — 1 ValueError → ValidationException (NOT_INITIALIZED), P1
- `workshop_viewmodel.py` — 1 ValueError + 1 RuntimeError → ValidationException, P1/P2
- `new_game_setup_screen.py` — 1 ValueError → ValidationException (OUT_OF_RANGE), P1
- `formation_editor.py` — 1 ValueError → ValidationException (INVALID_FORMAT), P2, BREAKING
- `asset_manager.py` — 1 ValueError → ResourceException (INVALID_FORMAT), P3

**Tests to update:** ~10 tests (game_config, new_game_setup, vehicle_class_service, asset_manager)

### Phase 5: Caller Catch Updates (36 except blocks) — ~3 hours
**Self-contained (safe, do during Phase 3):**
- `abilities/base.py:97` — except ValueError → except ValidationException
- `battle_state_manager.py:78` — except ValueError → except ValidationException
- `density_map.py:207` — except TypeError → except ValidationException

**Persistence tier (coordinate together):**
- `save_game_service.py` — 4 broad catches → specific domain exceptions
- `design_library.py` — 4 broad catches → specific domain exceptions
- `race_library.py` — 2 broad catches → specific domain exceptions
- `ship_io.py` — 2 catches → specific domain exceptions

**Component loading chain:**
- `component.py:525,629` — broad catches → ComponentException
- `design_loader.py:75,122` — broad catches → specific exceptions
- `vehicle_design_service.py:121` — broad catch → specific
- `battle_service.py:88` — broad catch → specific
- `battle_controller.py:172,389,516` — broad catches → specific

**Other:**
- `formation_editor.py:202,227` — update catches
- `new_game_setup_screen.py:508` — update catch
- `abilities/__init__.py:118` — update catch

### Phase 6: Exception Chaining Fixes — ~30 min
Add `from e` to 3 re-raise patterns:
- `battle_state_manager.py:79` — `raise ValidationException(...) from e`
- `abilities/base.py:98` — `raise ValidationException(...) from e`
- `density_map.py:208` — `raise ValidationException(...) from e`

### Phase 7: Catch Quality Cleanup — ~1 hour
- Fix bare except in `scripts/apply_resource_costs.py`
- Add logging to silent fallbacks in `battle_panels.py`, `race_environment_panel.py`
- Review overly broad catches in persistence tier (done in Phase 5)

### Phase 8 (Optional, Separate Project): Deserialization Validation — ~8 hours
High-risk from_dict methods needing validation:
- Galaxy.from_dict() — NO_VALIDATION, High risk
- WarpPoint.from_dict() — NO_VALIDATION, Medium risk
- Spectrum.from_dict() — NO_VALIDATION, Low risk
- RaceConfig.from_dict() — NO_VALIDATION, Medium risk
- ShipSerializer.from_dict() — PARTIAL, High risk
- Fleet.from_dict() — PARTIAL, High risk
- Empire.from_dict() — PARTIAL, High risk
- Planet.from_dict() — PARTIAL, High risk
- Plus 7 more PARTIAL methods

---

## Estimated Total Effort

| Phase | Description | Effort | Files | Tests |
|-------|-------------|--------|-------|-------|
| 1 | Infrastructure (error codes) | 1 hr | 1 | 0 |
| 2 | Strategy loaders | 2 hr | 4 | 6 |
| 3 | Simulation core | 3 hr | 15 | 40 |
| 4 | Game config + UI | 2 hr | 7 | 10 |
| 5 | Caller catch updates | 3 hr | 12 | 0 |
| 6 | Exception chaining | 0.5 hr | 3 | 0 |
| 7 | Catch quality cleanup | 1 hr | 3 | 0 |
| **Total (Core)** | **Phases 1-7** | **~12.5 hr** | **~35 files** | **~56 tests** |
| 8 | Deserialization validation (optional) | 8 hr | 15 | ~20 new |

---

## Breaking Changes Summary

Only **5 locations** have callers that catch ValueError and will break:

| Raise Location | Caller Location | Risk |
|---------------|-----------------|------|
| `abilities/base.py:98` | `abilities/base.py:97` (same file) | Low — self-contained |
| `battle_state_manager.py:79` | `battle_state_manager.py:78` (same file) | Low — self-contained |
| `formation_editor.py:217` | `formation_editor.py:227` (same file) | Low — self-contained |
| `density_map.py:208` | `density_map.py:207` (same file) | Low — self-contained |
| Various DI TypeError | Various integration catches | Low — broad catches still work |

**All breaking changes are self-contained** (raise and catch in same file). No cross-module breaking changes identified.

---

## Error Code Changes

### New Codes (3)
| Code | Name | Description | Replaces |
|------|------|-------------|----------|
| V002 | SCHEMA_VALIDATION_ERROR | Missing fields, invalid data structure | ~18 loader ValueErrors |
| V003 | MISSING_ENTITY | Referenced entity not found by name/ID | ~3 KeyError-style lookups |
| C003 | MISSING_DEPENDENCY | Required DI parameter not provided | ~13 TypeError DI checks |

### Currently Unused Codes (will gain usage during migration)
R001, R002, R003, P001, P002, P004, P005, C001 — these are correctly defined but have no users yet. Migration will activate R001 (ship_loader.py), R002 (asset_manager.py, loader files), and others.

---

## Agent Reports

- [ValueError Migration Mapper](findings/valueerror_mapper_report.md) — 46 findings
- [Generic Exception Mapper](findings/generic_exception_mapper_report.md) — 23 findings
- [Caller Impact Analysis](findings/caller_impact_report.md) — 84 except blocks analyzed
- [Error Code Gap Analysis](findings/error_code_gap_report.md) — 3 new codes proposed
- [Catch Quality Audit](findings/catch_quality_report.md) — 31 quality issues
- [Deserialization Validation Audit](findings/deserialization_report.md) — 20 methods audited
- [Test Impact Analysis](findings/test_impact_report.md) — 126 test assertions analyzed

---
*Report compiled: 2026-02-23*
