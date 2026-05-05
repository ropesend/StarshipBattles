# Review Report: PROJ-356 Follow-up — Audit Remediation Verification

## Metadata
- **Date:** 2026-05-05
- **Type:** code (follow-up, delegated by Claude Code)
- **Follow-up to:** req_20260505_055830_432529
- **Parent report:** `Reviews/results/2026-05-05_055830_code_proj-356-review-ai-pdc-capability-cache-fix_req-req_20260505_055830_432529/report.md`
- **Remediation commit:** `fd3a51738` (fix(PROJ-356): audit remediation (DC-001..DC-005))
- **Review mode:** targeted follow-up (not full re-review). Scope limited to the 5 CRIT/MAJ findings from the parent review.
- **Scope files verified at commit `fd3a51738`:**
  - `game/ai/controller.py`
  - `game/ai/target_evaluator.py`
  - `Projects/active_projects/PROJ-356/decisions.md`

## Verification Matrix

| Parent Finding | Status | Notes |
|---|---|---|
| DC-001 (CRIT) | **rejection-rationale-sound** | Cache keys intentionally populated for future consumers per original decisions.md row; cost negligible; PERF comment updated to make intent explicit. |
| DC-002 (CRIT) | **resolved** | `is_in_pdc_arc` removed from `controller.py` import tuple at line 72-76. Confirmed zero non-comment references to `is_in_pdc_arc` in controller.py (the only remaining occurrence is in the PERF comment at line 274 explaining the deferral). |
| DC-003 (MAJ) | **deferred (acknowledged)** | Out of scope for this audit remediation. Deferral documented in PERF comment at `controller.py:270-274` and decisions.md. Per-firing-ship PDC component caching needed. |
| DC-004 (MAJ) | **resolved** | PERF comment at `controller.py:270-274` rewritten to accurately state: only `has_weapons` rules consume the cache today; `has_pdc`/`pdc_components` keys are for a future PDC-arc cache consumer; `_eval_pdc_arc_rule` still calls `is_in_pdc_arc` directly. |
| DC-005 (MAJ) | **resolved** | Stale "Previously crashed in the cache-miss fallback; outer try/except silently dropped the missile from scoring" sentence removed from `_eval_has_weapons_rule` docstring at `target_evaluator.py:172-176`. Replaced with accurate `is_combat_ship` TypeGuard route description. |

## Evidence — Per-Finding

### DC-002: Unused `is_in_pdc_arc` import → RESOLVED

**Before (parent commit):**
```python
from game.ai.combat_utils import (
    get_capability_cache_key,
    get_entity_id,
    get_hp_percent,
    is_in_pdc_arc,          # <-- unused in controller.py
)
```

**After (fd3a51738, controller.py:72-76):**
```python
from game.ai.combat_utils import (
    get_capability_cache_key,
    get_entity_id,
    get_hp_percent,
)
```

Grep for `is_in_pdc_arc` in `game/ai/controller.py` returns only the comment reference at line 274 (`# \`_eval_pdc_arc_rule\` still calls \`is_in_pdc_arc\` directly.`). No code references. `target_evaluator.py` retains its own correct import.

### DC-004: Misleading PERF comment → RESOLVED

**Before:**
```python
# PERF: Pre-compute capability checks once for all candidates
# Avoids redundant component lookups for has_weapons, pdc_arc rules
```

**After (fd3a51738, controller.py:270-274):**
```python
# PERF: Pre-compute capability checks once for all candidates.
# Today only `has_weapons` rules consume the cache. The `has_pdc`
# / `pdc_components` keys are populated for a future PDC-arc cache
# consumer (see decisions.md PROJ-356 audit remediation, DC-003);
# `_eval_pdc_arc_rule` still calls `is_in_pdc_arc` directly.
```

The comment now accurately reflects runtime reality. Cross-references DC-003 deferral and decisions.md.

### DC-005: Stale docstring → RESOLVED

**Before (`target_evaluator.py:172-176`):**
```python
"""Evaluate has_weapons rule.

PROJ-272 Phase 3: projectile candidates (missiles) have no
components — rule treats them as "no weapons" without crashing
on the `get_components_by_ability` call. Previously crashed in
the cache-miss fallback; outer try/except silently dropped the
missile from scoring.
"""
```

**After (fd3a51738, target_evaluator.py:172-176):**
```python
"""Evaluate has_weapons rule.

PROJ-272 Phase 3: projectile candidates (missiles) have no
components — rule treats them as "no weapons" without crashing
on the `get_components_by_ability` call. Non-ship candidates
are routed through the `is_combat_ship` TypeGuard before any
component query.
"""
```

The historical crash-recovery narrative (no longer accurate after the cache refactor) is removed. The replacement accurately describes the current flow: non-ship candidates go through `is_combat_ship` TypeGuard.

### DC-001: Rejection rationale → SOUND

The parent review flagged `has_pdc`/`pdc_components` cache keys as CRITICAL because nothing reads them. The rejection rationale is sound on these grounds:

1. **Pre-disclosed in original work.** The PROJ-356 `decisions.md` row from 2026-05-04 (line 14) explicitly states the consumer audit found these keys unused and concludes: *"fixing the always-empty list is purely correctness for future consumers; no observable AI behavior changes today."* The original committer was aware and chose to populate them anyway.

2. **Intent is now explicit in-code.** The PERF comment at `controller.py:270-274` (updated for DC-004) now reads: *"The \`has_pdc\` / \`pdc_components\` keys are populated for a future PDC-arc cache consumer (see decisions.md PROJ-356 audit remediation, DC-003)."* No reader needs to guess why the keys exist.

3. **Cost is negligible.** The computation is an O(n) `has_pdc_ability()` tag scan per enemy where n = weapon component count (typically < 10). This is inside `_build_capabilities_cache` which already iterates all enemies and weapon components for other purposes.

4. **No convention violation.** AGENTS.md Rule 3 prohibits compatibility shims, fallback systems, monkey patches, and duplicate logic. Future-consumer cache keys are none of these — they are forward-looking surface area exposed via a documented public API (the `ship_capabilities_cache` dict contract), not a workaround for legacy behavior.

5. **Regression suite locks in correctness.** `tests/unit/ai/test_capability_cache_pdc.py` validates the tag-based `has_pdc_ability()` detection, so the cache values are correct regardless of whether read.

## Regressions / New Issues

**None found.** The remediation diff is minimal (21 insertions, 6 deletions across 3 files):
- `controller.py`: 1 import removed, 1 comment expanded (no logic changes)
- `target_evaluator.py`: 1 docstring updated (no logic changes)
- `decisions.md`: Audit Remediation table appended (documentation only)

All three resolved findings (DC-002, DC-004, DC-005) are clean, targeted fixes with no side effects. DC-001 rejection rationale holds under scrutiny. DC-003 is properly deferred with tracking links.

## Findings Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 0 |
| Info | 0 |
| **Total** | **0** |

No new findings — this is a zero-finding verification report confirming all targeted audit remediation items are correctly addressed.
