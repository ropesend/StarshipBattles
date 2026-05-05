# Code Quality Report — PROJ-356 PDC Capability Cache Fix

**Review Date:** 2026-05-05
**Scope:** `game/ai/controller.py` (L229-231), `tests/unit/ai/test_capability_cache_pdc.py`, `Projects/active_projects/PROJ-356/decisions.md`
**Conventions Reference:** `docs/03_CONVENTIONS.md`

---

## Summary

The fix replaces a dead code path (`has_ability('PDCAbility')` against a non-existent class) with the canonical tag-based `has_pdc_ability()` call, which queries ability tags for `'pdc'`. The implementation is clean, idiomatic, and follows all relevant conventions. No compatibility shims, silent fallbacks, or CLAUDE.md Rule 3 violations were found.

- **Total issues found: 4**
- **Critical: 0, Major: 0, Minor: 2, Info: 2**

---

## Findings

#### MINOR: Mild pattern duplication between cache builder and `is_in_pdc_arc`
**ID:** CQ-001
**Location:** `game/ai/controller.py:226-231` and `game/ai/combat_utils.py:216-234`
**Issue:** Both `_build_capabilities_cache` and `is_in_pdc_arc` implement the same two-step pattern: (1) fetch components via `get_components_by_ability('WeaponAbility', operational_only=True)`, (2) filter by `has_pdc_ability()`. The list-comprehension vs for-loop syntax differs, but the semantic intent is identical.
**Impact:** Low. The two callers operate on different entities (cache builder on enemy targets, `is_in_pdc_arc` on the AI-owning ship) and reside in different modules. Future changes to PDC detection logic (e.g., a second tag or a different query method) would require edits in two places.
**Recommendation:** Consider extracting a shared `get_pdc_weapons(entity) -> list[Component]` helper in `combat_utils.py`. Both callers already import from `combat_utils`. This is a follow-up cleanup, not a blocker for this fix.
**Effort:** Simple

#### MINOR: `get_capability_cache_key` uses legacy `Optional[str]` syntax
**ID:** CQ-002
**Location:** `game/ai/combat_utils.py:73`
**Issue:** Return type annotation `Optional[str]` should be `str | None` per §8 (PEP 604 syntax for new or touched signatures). This function is imported by `controller.py:_build_capabilities_cache` (L221), placing it in the fix's call chain.
**Impact:** Low. Conventions note "Existing legacy annotations remain cleanup backlog; do not expand them when editing a file." This signature predates the fix. No behavioral issue.
**Recommendation:** Update to `str | None` in a follow-up annotation modernization pass. Do not block this merge.
**Effort:** Simple

#### INFO: Docstring documents `pdc_components` / `has_pdc` keys that are currently unread
**ID:** CQ-003
**Location:** `game/ai/controller.py:204-211` and `game/ai/target_evaluator.py:286-287`
**Issue:** The cache docstring and `TargetEvaluator.evaluate` parameter docstring both describe `'has_pdc': bool` and `'pdc_components': List[Component]` keys. Per `PROJ-356/decisions.md` L14, no production code currently reads these keys — the only consumer (`_eval_pdc_arc_rule`) calls `is_in_pdc_arc(ship, candidate)` directly rather than consulting the cache.
**Impact:** None. The fields are correctly populated and ready for future consumers. The docstring accurately describes the intent. This is purely informational.
**Recommendation:** No action required. The decision log already documents this. Future work that adds a cache consumer for these keys should reference PROJ-356.
**Effort:** N/A

#### INFO: Control comment is historically useful but slightly verbose
**ID:** CQ-004
**Location:** `game/ai/controller.py:228-230`
**Issue:** The three-line comment block explaining *why* tag-based detection replaced class-name-based detection provides historical context that is not obvious from the code alone. Conventions §6 prefers code that speaks for itself, but this is a design rationale comment that a future maintainer could benefit from.
**Impact:** None. The comment adds 3 lines to a 28-line method (still well under the 50-line target). The code itself (`w.has_pdc_ability()`) is self-documenting; the comment reinforces *why* it is the correct approach.
**Recommendation:** Optional: reduce to one line — `# Tag-based PDC detection (PROJ-241/PROJ-356)` — since `has_pdc_ability()` is self-evidently the canonical surface.
**Effort:** Trivial

---

## Top 5 Priority Issues

1. **CQ-001** (MINOR) — Mild DRY: PDC filter pattern duplicated between cache builder and `is_in_pdc_arc`
2. **CQ-002** (MINOR) — Legacy `Optional[str]` in `get_capability_cache_key` return type
3. **CQ-004** (INFO) — Verbose historical comment in `_build_capabilities_cache`
4. **CQ-003** (INFO) — Docstring documents currently-unread cache keys
5. *(No further issues)*

---

## Positive Observations

- **Tag-based detection is idiomatic:** `has_pdc_ability()` delegates to `has_ability_with_tag('pdc')`, the generalized tag query in `AbilityManager`. This follows §6.5 (no hardcoded type/class name lists) and §6.3 (data-driven lookups over hardcoded lists).
- **No compatibility shims or fallback paths:** The fix completely eradicates the dead `has_ability('PDCAbility')` path. No dual-path logic, no legacy compatibility — consistent with §6.6 (System Migration) and CLAUDE.md Rule 3.
- **Test coverage is thorough:** Four test cases cover PDC-included, PDC-excluded, mixed-weapon, and dead-code-path-absent scenarios. The fifth test explicitly verifies that `has_ability('PDCAbility')` is never called.
- **Test helper mocks mirror real-world behavior:** `_make_weapon` sets `has_ability` to always return `False`, so any code reaching for the dead string path would fail the test. This is a strong regression guard.
- **The shared fixture (`create_mock_enemy` in `test_ai_capabilities_cache.py`) was updated** to mock `has_pdc_ability` instead of `has_ability`, eliminating the bug-locking pattern documented in decisions.md L15.
- **Decision log is comprehensive:** `decisions.md` documents the consumer audit result (cache keys are currently unused), the fixture update rationale, and the intentional non-change to `test_controllable_adapter_edge_cases.py`.
- **List comprehension is clean:** `[w for w in weapons if w.has_pdc_ability()]` is a single-line, single-purpose expression.
- **Method size is healthy:** `_build_capabilities_cache` at ~28 lines is well under the 50-line target (§6.2).
- **Nesting is shallow:** Maximum 2 levels (for-loop + if-guard), within the 3-level limit.

---

## Conclusion

The fix is production-quality. It replaces dead code with the canonical tag-based surface, follows all applicable conventions, and is well-tested with explicit regression guards. The four flagged issues are all minor/informational and none block merge. No critical or major defects were found.
