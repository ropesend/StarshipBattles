# PROJ-498 File Manifest

> Used by `/proj-parallel` for conflict detection. Updated if implementation
> discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/services/modifier_service.py | Production | Added `AllowanceReason` enum + `AllowanceResult` frozen dataclass + `check_allowance()` method. `is_modifier_allowed()` is now a one-liner delegating to `check_allowance().allowed`. |
| game/simulation/services/modifier_save_restore.py | Production (new, Phase 5) | F1 remediation: houses `apply_modifier_with_rejection_logging()` used by both save-restore call sites to dedupe the rejection-logging block. 80 LOC including module docstring. |
| game/simulation/components/modifier_manager.py | Production (read-only check) | `is_modifier_allowed()` caller at line 124-128 — verified unchanged contract; all 21 modifier_manager tests still green. |
| game/ui/services/component_service.py | Production (read-only check) | `is_modifier_allowed()` caller at line 104-109 — verified unchanged contract; all 16 component_service tests still green. |
| game/ui/screens/builder/modifier_logic.py | Production (read-only check) | `is_modifier_allowed()` caller at line 54-56 — verified unchanged contract; all 26 modifier_logic tests still green. |
| game/simulation/battle_state.py | Production | Phase 2: added `logger.warning` on rejection inside `ShipState.to_ship` modifier-apply loop. Phase 5 (F1): refactored that block to call `apply_modifier_with_rejection_logging()`. Message form unchanged: `"BattleState restore: Modifier '{mid}' rejected for component '{cid}' on ship '{ship_id}': {REASON}; skipping"`. LOC: 612 baseline -> 624 final. |
| game/simulation/entities/ship_serialization.py | Production | Phase 2: added `logger.warning` on rejection inside `ShipSerializer._load_components`, distinct from the pre-existing unknown-id warning. Phase 5 (F1): refactored to call the helper; pre-existing else-branch `not found in registry` warning preserved exactly. Message form unchanged: `"ShipSerializer: Modifier '{mid}' rejected for component '{cid}' on ship '{ship_name}': {REASON}; skipping"`. LOC: 285 -> 283. |
| tests/regression/modifier_ability_snapshots/test_allowance_matrix.py | Test (new) | Data-driven parametrized matrix: 2197 (modifier, component) pairs derived from JSON at collection time + 1 sanity test. Live rule only (no deny_abilities). |
| tests/unit/simulation/services/test_modifier_service.py | Test | Added `TestCheckAllowance` (7 tests) + `TestIsModifierAllowedBoolRegressionGuard` (3 tests). Codex Q5 guard pins the reason enum set. |
| tests/unit/simulation/test_battle_state_live_object_bridges.py | Test | Added `TestShipStateToShipRejectionLogging` covering the new save-restore warning. (No `test_battle_state.py` exists; placed alongside existing `TestShipStateToShip` tests.) |
| tests/unit/simulation/entities/test_ship_serialization.py | Test | Added `TestLoadComponentsRejectionLogging` (2 tests): reason-included assertion + distinct-from-unknown-id assertion. |
| docs/05_ERROR_HANDLING.md | Doc | Added "Save-Restore Modifier Rejection (PROJ-498)" section between JSON/Persistence and Turn Engine Boundary. |
| docs/04_SERVICES.md | Doc | Expanded the Modifiers subsection with `check_allowance()`, the full reason set, and the save-restore log boundary. |
| docs/guides/modifier_system.md | Doc | Added `check_allowance()` + reason enum to the ModifierService Surface listing, plus a "Diagnosing rejections" paragraph. PROJ-489's existing "deny_abilities not enforced" wording (lines 98, 290) verified intact. |

## Conflicts with PROJ-497
PROJ-497 (sibling data-intent project) touches `data/modifiers.json`, `data/components.json`, and snapshot fixtures. PROJ-498 must run AFTER PROJ-497 closes so the matrix test in Phase 3 encodes the final intended data surface, not today's accidental surface.

If both run interleaved, the matrix test will need re-running after every PROJ-497 data edit — wasteful and risk of false-red. Hard sequence: **PROJ-497 → PROJ-498**.
