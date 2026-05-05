# Validation Report: Validator 1

## Summary
- **Findings Reviewed:** 8
- **Confirmed:** 8
- **Downgraded:** 0
- **Rejected:** 0
- **Rejection Rate:** 0%

## Verdicts

#### Finding: AR-001
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — controller.py:226-231 calls `get_components_by_ability('WeaponAbility')` + `has_pdc_ability()` filter; `is_in_pdc_arc` in combat_utils.py:214-234 independently performs the identical two-step pattern with no shared abstraction.

#### Finding: AR-002
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — controller.py:68 imports `is_combat_ship` from `game/simulation/interfaces/entity_protocols` (architecturally designated "Simulation-Internal Protocols" per docs/01_ARCHITECTURE.md:341), while `game/core/protocols/__init__.py:47` re-exports the same TypeGuard from `game.core.protocols.combat` for cross-layer use.

#### Finding: AR-003
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — cache keys `has_pdc` and `pdc_components` are written at controller.py:236-237 but zero consumers read them; `_eval_has_weapons_rule` (target_evaluator.py:184) reads only `has_weapons`, and `_eval_pdc_arc_rule` (target_evaluator.py:230) bypasses the cache entirely by calling `is_in_pdc_arc` directly.

#### Finding: AR-004
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `game/ai/protocols.py:117` defines `is_projectile` TypeGuard (AI-layer `IProjectile`) and `game/simulation/interfaces/entity_protocols.py:474` defines an independent `is_projectile` TypeGuard (simulation `IProjectile`); both check `position` and `type` with near-identical logic.

#### Finding: AR-005
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `_make_weapon` (test_capability_cache_pdc.py:70-83) asymmetrically mocks `has_pdc_ability` (tag-based, correct path) vs `has_ability` (returns False, dead pre-fix path), then test at line 141 asserts `'PDCAbility'` never appears in `has_ability` call args — this dual-path mock design thoroughly guards against regression to the old string-based check.

#### Finding: CQ-001
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — identical to AR-001; both `_build_capabilities_cache` (controller.py:226-231) and `is_in_pdc_arc` (combat_utils.py:214-234) independently implement fetch-WeaponAbility-then-filter-by-pdc-tag without a shared helper.

#### Finding: CQ-002
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `get_capability_cache_key` at combat_utils.py:73 declares return type `Optional[str]` instead of PEP 604 `str | None`, which is the project convention for new/touched code per docs/03_CONVENTIONS.md.

#### Finding: CQ-003
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `_build_capabilities_cache` docstring (controller.py:204-211) documents `has_pdc` and `pdc_components` as returned cache keys, but no consumer reads either key (confirmed in AR-003); the docstring is correct about what is produced but misleading about utility.
