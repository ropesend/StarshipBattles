# PROJ-498 File Manifest

> Used by `/proj-parallel` for conflict detection. Updated if implementation
> discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/services/modifier_service.py | Production | Add reason-bearing `check_allowance()` method; keep `is_modifier_allowed()` as bool convenience |
| game/simulation/components/modifier_manager.py | Production (read-only check) | `is_modifier_allowed()` caller at line 124-128 — Phase 1 must not break this |
| game/ui/services/component_service.py | Production (read-only check) | `is_modifier_allowed()` caller at line 104-109 — Phase 1 must not break this |
| game/ui/screens/builder/modifier_logic.py | Production (read-only check) | `is_modifier_allowed()` caller at line 54-56 — Phase 1 must not break this |
| game/simulation/battle_state.py | Production | Add `logger.warning` on rejection at line ~279 |
| game/simulation/entities/ship_serialization.py | Production | Add `logger.warning` on rejection at line ~226 (separate from existing unknown-id warning) |
| tests/regression/modifier_ability_snapshots/test_allowance_matrix.py | Test (new) | Data-driven parametrized matrix. Live rule only (no deny_abilities). |
| tests/unit/simulation/services/test_modifier_service.py | Test | Add tests for new reason-bearing API + bool-semantics regression guard |
| tests/unit/simulation/test_battle_state.py | Test | Add test asserting rejection log is emitted |
| tests/unit/simulation/entities/test_ship_serialization.py | Test | Add test asserting rejection log is emitted |
| docs/05_ERROR_HANDLING.md | Doc | Cite save-restore log behavior |
| docs/04_SERVICES.md | Doc | Document `check_allowance()` API surface (if not already covered by PROJ-489 phase 2) |
| docs/guides/modifier_system.md | Doc | Phase 4 Task 4.3: add "Diagnosing rejections" section |

## Conflicts with PROJ-497
PROJ-497 (sibling data-intent project) touches `data/modifiers.json`, `data/components.json`, and snapshot fixtures. PROJ-498 must run AFTER PROJ-497 closes so the matrix test in Phase 3 encodes the final intended data surface, not today's accidental surface.

If both run interleaved, the matrix test will need re-running after every PROJ-497 data edit — wasteful and risk of false-red. Hard sequence: **PROJ-497 → PROJ-498**.
