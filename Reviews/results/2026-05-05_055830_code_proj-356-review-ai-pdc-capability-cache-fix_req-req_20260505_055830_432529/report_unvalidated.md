# Review Report: 2026-05-05_055830_code_proj-356-review-ai-pdc-capability-cache-fix_req-req_20260505_055830_432529

## Metadata
- **Date:** 2026-05-04
- **Type:** code (delegated by Claude Code)
- **Description:** 
- **Agents Used:** 4

## Executive Summary
- **Total Findings:** 24
- **Critical:** 2 | **Major:** 3 | **Minor:** 10 | **Info:** 9
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: `has_pdc` and `pdc_components` cache keys computed but never read by any consumer
**ID:** DC-001
**Agent:** Dead Code Audit
**Location:** `Unknown`
**Effort:** Medium

**ID:** DC-001
**Location:** Writer: `game/ai/controller.py:231,236-237` (lines 231, 236-237). No reader exists anywhere in production code.
**Issue:** `_build_capabilities_cache` iterates all weapon components per entity, filters for PDC weapons via `has_pdc_ability()`, and stores the results as `'has_pdc': bool` and `'pdc_components': List[Component]`. No code path reads these keys. The only cache consumers are:

- `_eval_has_weapons_rule` (`target_evaluator.py:184`) — reads only `'has_weapons...

---

### 2. CRITICAL: `is_in_pdc_arc` imported but never used in `controller.py`
**ID:** DC-002
**Agent:** Dead Code Audit
**Location:** `game/ai/controller.py:76`
**Effort:** Simple

**ID:** DC-002
**Location:** `game/ai/controller.py:76`
**Issue:** `is_in_pdc_arc` is imported from `game.ai.combat_utils` on line 76 but is never referenced anywhere in the controller file (469 lines, confirmed by full-file grep). This is a dead import.
**Impact:** Unnecessary namespace pollution and maintenance overhead. Suggests the function was once called from the controller and removed without cleaning up the import.

**Recommendation:** Remove `is_in_pdc_arc` from the import tuple at line...

---

### 3. MAJOR: `is_in_pdc_arc` does redundant full component lookups — cached PDC data sits unused
**ID:** DC-003
**Agent:** Dead Code Audit
**Location:** `game/ai/combat_utils.py:214-222`
**Effort:** Medium

**ID:** DC-003
**Location:** `game/ai/combat_utils.py:214-222`, `game/ai/target_evaluator.py:218-238`
**Issue:** `_eval_pdc_arc_rule` (target_evaluator.py:218) receives only `stat_helpers` — it does NOT receive `ship_capabilities_cache`. When it calls `stat_helpers['is_in_pdc_arc'](ship, candidate)`, `is_in_pdc_arc` performs a full `get_components_by_ability('WeaponAbility')` call to retrieve ALL weapon components (combat_utils.py:214-222), then iterates and filters via `has_pdc_ability()` (line...

---

### 4. MAJOR: Misleading PERF comment in `_score_and_sort_enemies` claims PDC arc benefits from caching
**ID:** DC-004
**Agent:** Dead Code Audit
**Location:** `game/ai/controller.py:272`
**Effort:** Simple

**ID:** DC-004
**Location:** `game/ai/controller.py:272`
**Issue:** The comment reads:
```python
# PERF: Pre-compute capability checks once for all candidates
# Avoids redundant component lookups for has_weapons, pdc_arc rules
```
In reality, pdc_arc rules do NOT use the cache. Only `has_weapons` rules benefit.
**Impact:** This stale claim misleads maintainers into thinking `_eval_pdc_arc_rule` is cache-aware when it is not. The performance claim is false.

**Recommendation:** Remove `pdc_arc` f...

---

### 5. MAJOR: Stale docstring in `_eval_has_weapons_rule` references defunct try/except
**ID:** DC-005
**Agent:** Dead Code Audit
**Location:** `game/ai/target_evaluator.py:174-176`
**Effort:** Simple

**ID:** DC-005
**Location:** `game/ai/target_evaluator.py:174-176`
**Issue:** The docstring states:
```
Previously crashed in the cache-miss fallback; outer try/except silently dropped
the missile from scoring.
```
The outer try/except was removed in PROJ-272 Phase 3 when the code was refactored to use protocol checks (`is_combat_ship`, `is_projectile`) instead of try/except guards. There is no try/except wrapping target evaluation in the current code. The docstring describes historical behavior...

---

### 6. MINOR: PDC weapon discovery logic duplicated between cache builder and is_in_pdc_arc
**ID:** AR-001
**Agent:** Architecture
**Location:** `game/ai/controller.py:226-231`
**Effort:** Simple

**ID:** AR-001
**Location:** `game/ai/controller.py:226-231`, `game/ai/combat_utils.py:216-234`
**Issue:** Both `_build_capabilities_cache` and `is_in_pdc_arc` independently call `get_components_by_ability('WeaponAbility')` followed by `has_pdc_ability()` filtering. The cache pre-computes `pdc_components` but `is_in_pdc_arc` ignores it and rediscover PDC weapons from scratch on every evaluation call.
**Impact:** Efficiency: PDC filtering runs O(1) times in the cache build but may run O(n) times ...

---

### 7. MINOR: is_combat_ship imported from simulation-internal module rather than core protocols
**ID:** AR-002
**Agent:** Architecture
**Location:** `game/ai/controller.py:68`
**Effort:** Medium

**ID:** AR-002
**Location:** `game/ai/controller.py:68`
**Issue:** The controller imports `is_combat_ship` from `game/simulation/interfaces/entity_protocols.py` (designated "Simulation-Internal Protocols" per `docs/01_ARCHITECTURE.md` § Simulation-Internal Protocols). There is a parallel `is_combat_ship` at `game/core/protocols/combat.py:131` with different matching criteria (`'angle', 'layers'` in simulation-internal vs `'team_id', 'hp', 'is_derelict'` in core). The architecture doc lists `ICom...

---

### 8. MINOR: Cache keys 'has_pdc' / 'pdc_components' written but never consumed
**ID:** AR-003
**Agent:** Architecture
**Location:** `game/ai/controller.py:233-238`
**Effort:** Simple

**ID:** AR-003
**Location:** `game/ai/controller.py:233-238`, `game/ai/target_evaluator.py:169` (sole consumer)
**Issue:** `_build_capabilities_cache` computes `has_pdc` and `pdc_components` for every cached ship, but no code reads these keys. The sole cache consumer (`_eval_has_weapons_rule` at `target_evaluator.py:169`) only reads `has_weapons`. `_eval_pdc_arc_rule` bypasses the cache entirely. This is confirmed in `decisions.md` ("purely correctness for future consumers") and `scope.md`.
**Im...

---

### 9. MINOR: Mild pattern duplication between cache builder and `is_in_pdc_arc`
**ID:** CQ-001
**Agent:** Code Quality
**Location:** `game/ai/controller.py:226-231`
**Effort:** Simple

**ID:** CQ-001
**Location:** `game/ai/controller.py:226-231` and `game/ai/combat_utils.py:216-234`
**Issue:** Both `_build_capabilities_cache` and `is_in_pdc_arc` implement the same two-step pattern: (1) fetch components via `get_components_by_ability('WeaponAbility', operational_only=True)`, (2) filter by `has_pdc_ability()`. The list-comprehension vs for-loop syntax differs, but the semantic intent is identical.
**Impact:** Low. The two callers operate on different entities (cache builder on e...

---

### 10. MINOR: `get_capability_cache_key` uses legacy `Optional[str]` syntax
**ID:** CQ-002
**Agent:** Code Quality
**Location:** `game/ai/combat_utils.py:73`
**Effort:** Simple

**ID:** CQ-002
**Location:** `game/ai/combat_utils.py:73`
**Issue:** Return type annotation `Optional[str]` should be `str | None` per §8 (PEP 604 syntax for new or touched signatures). This function is imported by `controller.py:_build_capabilities_cache` (L221), placing it in the fix's call chain.
**Impact:** Low. Conventions note "Existing legacy annotations remain cleanup backlog; do not expand them when editing a file." This signature predates the fix. No behavioral issue.
**Recommendation:...

---


## Findings by Severity

### Critical (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DC-001 | `has_pdc` and `pdc_components` cache key | `Unknown` | Medium |
| DC-002 | `is_in_pdc_arc` imported but never used  | `game/ai/controller.py:76` | Simple |

### Major (3)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DC-003 | `is_in_pdc_arc` does redundant full comp | `game/ai/combat_utils.py:214-22` | Medium |
| DC-004 | Misleading PERF comment in `_score_and_s | `game/ai/controller.py:272` | Simple |
| DC-005 | Stale docstring in `_eval_has_weapons_ru | `game/ai/target_evaluator.py:17` | Simple |

### Minor (10)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-001 | PDC weapon discovery logic duplicated be | `game/ai/controller.py:226-231` | Simple |
| AR-002 | is_combat_ship imported from simulation- | `game/ai/controller.py:68` | Medium |
| AR-003 | Cache keys 'has_pdc' / 'pdc_components'  | `game/ai/controller.py:233-238` | Simple |
| CQ-001 | Mild pattern duplication between cache b | `game/ai/controller.py:226-231` | Simple |
| CQ-002 | `get_capability_cache_key` uses legacy ` | `game/ai/combat_utils.py:73` | Simple |
| DC-006 | `AbilityManager.has_pdc_ability_static`  | `game/simulation/components/abi` | Medium |
| DC-007 | `evaluate()` docstring documents unused  | `game/ai/target_evaluator.py:28` | Simple |
| DC-008 | `_build_capabilities_cache` docstring ad | `game/ai/controller.py:204-211` | Simple |
| TC-001 | Neutral test provides no regression sign | `tests/unit/ai/test_capability_` | Simple |
| TC-002 | `create_mock_enemy` fix drops `has_abili | `tests/unit/ai/test_ai_capabili` | Simple |

### Info (9)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-004 | Duplicate is_projectile TypeGuard defini | `game/ai/protocols.py:117` | Simple |
| AR-005 | Test anti-regression design is exemplary | `tests/unit/ai/test_capability_` | Simple |
| CQ-003 | Docstring documents `pdc_components` / ` | `game/ai/controller.py:204-211` | N |
| CQ-004 | Control comment is historically useful b | `game/ai/controller.py:228-230` | Trivial |
| DC-009 | No `PDCAbility` string references in pro | `Unknown` | Unknown |
| DC-010 | Test-only `PDCAbility` string in `test_c | `tests/unit/ai/test_controllabl` | Unknown |
| TC-003 | `has_pdc` / `pdc_components` cache keys  | `game/ai/controller.py:231-237` | Medium |
| TC-004 | `test_controllable_adapter_edge_cases.py | `tests/unit/ai/test_controllabl` | N |
| TC-005 | `_make_weapon` mock for `has_ability` is | `tests/unit/ai/test_capability_` | Simple |


## Agent Reports

- [Architecture Report](findings/architecture_report.md)
- [Code Quality Report](findings/code_quality_report.md)
- [Dead Code Audit Report](findings/dead_code_audit_report.md)
- [Test Coverage Report](findings/test_coverage_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 24 |
| Critical | 2 |
| Major | 3 |
| Minor | 10 |
| Info | 9 |
| Agents Used | 4 |

---
*Report generated: 2026-05-04 23:09*
