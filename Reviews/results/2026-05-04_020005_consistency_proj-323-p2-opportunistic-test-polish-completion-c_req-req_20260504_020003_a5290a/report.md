# PROJ-323 Completion + Continuation Review

**Request ID:** req_20260504_020003_a5290a
**Review Type:** consistency
**Date:** 2026-05-04T02:00:05Z
**Scope:** PROJ-323 P2 opportunistic test polish — all 5 phases, 149/149 tasks, 1 deferred

---

## Executive Summary

PROJ-323 delivered solid, mechanically correct P2 test polish across all 5 phases. The parametrize sweeps preserve discoverability and error messages. The CAT-12 reference-value pattern is sound (one precision mismatch noted). CAT-11 soft-assertion handling on Task 4.2 correctly retained hard assertions. The Task 3.34 deferral rationale is partially justified but the work is achievable now. All below-the-line rejections are sound.

**Cross-cutting audit found 2 false-positive checkmarks** (Tasks 3.3 and 3.6 claim work on deleted files), a terminology mismatch between "items" and "tasks" in the plan header, and LOC delta numbers that are pre-work estimates rather than actuals.

The one continuation item worth pursuing is Task 3.34 (parametrize 11-handler fleet_not_found cluster, ~75 LOC savings).

---

## Key Findings

### CRITICAL (1)

**FND-CC-001 — False-positive checkmarks on deleted files**
- Tasks 3.3 (S11-CAT10-005) and 3.6 (S11-CAT10-007) are checked `[x]` as completed, but their target files (`test_colonization_facade.py`, `test_color_helpers.py`) were deleted by upstream PROJ-321. Combined claimed LOC delta of ~314 is fictitious. Sibling items in the same tasks are correctly marked skipped. Fix: mark both as `_(skipped — upstream project already deleted target file)_`.

### MAJOR (3)

**FND-P2-001 — Task 5.19 precision mismatch**
- Docstring derivations use ~ approximations (~0.94, ~0.9787) but assertion uses `rel=1e-9` tolerance on `-0.005596103475344202`. A maintainer cannot re-derive the exact expected value from docstring alone. Recommend adding intermediate values at assertion precision or relaxing tolerance to `rel=1e-5`.

**FND-CC-002 — Item vs. task terminology mismatch**
- Plan header table: 32+32+53+15+27 = 159 "items" (CAT-finding counts). Current State: 149/149 "tasks" (Task N.M counts). Phase 2 has 30 tasks for 32 items; Phase 3 has 46 tasks for 53 items. An apparent 10-item discrepancy that is actually just inconsistent terminology.

**FND-CC-003 — LOC delta numbers are pre-work estimates, not actuals**
- Per-task LOC deltas in verify lines are carried forward from the source review. Many no-op and skipped items retain original estimates (e.g., Task 2.19: "LOC delta ≈ 336 (no-op)"). Naive sum ~7,700+ vs claimed actual ~-1,418. Verify lines should show actual deltas or be clearly marked "(estimate)".

### MINOR (15)

| ID | Description |
|----|-------------|
| FND-P1-001 | Inconsistent parametrize IDs in Task 3.19 (`fallback_to_min_val` vs `fallback_to_modifier_min`) |
| FND-P1-002 | Task 3.44: bare-string parametrize in cancel blocks, inconsistent with `pytest.param(id=...)` style |
| FND-P1-003 | Task 3.37: zero/negative cargo pairs are ideal 2-member parametrize candidates, blocked by ≥3 threshold |
| FND-P2-002 | Task 5.23 tolerance over-generous (0.01 vs ~0.000033 actual rounding delta) |
| FND-P2-003 | Design.md:41 references deleted `test_projectile_manager.py` as canonical example |
| FND-P2-004 | Task 4.9 mis-categorized (data cleanup, not fragile-assertion replacement) |
| FND-P2-005 | Design.md:42 mischaracterizes Task 4.2 pattern as "advisory soft assertions" when actual is hard assertions with soft thresholds |
| FND-P2-006 | Task 5.12: issubset pattern actually strengthened regression signal (correctly increased strictness) |
| FND-P3-001 | 11 fleet_not_found methods share identical assertion logic |
| FND-P3-003 | "Per-class structure mirrors production" deferral rationale is factually incorrect (production is split across 5 sub-modules, test is monolithic) |
| FND-P3-005 | Task 3.2 already established class-level parametrize in same project phase; inconsistency |
| FND-P4-005 | Task 3.34 is lowest-value-but-worth-doing continuation |
| FND-CC-004 | Manifest.md never updated after PROJ-321 deletions (~42/147 entries stale) |
| FND-CC-005 | Task 3.10 marked `[x]` but annotated "deferred" — not done, not left-as-is with docs |
| FND-CC-006 | Tasks 2.8/2.9 LOC deltas (≈307, ≈250) double-count work done in Phase 1 |

### INFO (14)

| ID | Description |
|----|-------------|
| FND-P1-004 | All 5 parametrize spot-checks pass quality review |
| FND-P1-005 | Tasks 3.15 and 3.27 correctly enforce ≥3 threshold |
| FND-P2-007 | Reference-value pattern is fundamentally sound across all 3 implementations |
| FND-P3-002 | All 11 fleet_not_found bodies are semantically identical |
| FND-P3-004 | Construction-queue handlers use different interface (entity_id vs fleet_id), warrants separate group |
| FND-P3-006 | Estimated 70-85 LOC savings if Task 3.34 parametrized |
| FND-P4-001 | All 7 below-the-line items correctly classified |
| FND-P4-002 | All 3 needs-rework items resolved |
| FND-P4-003 | All 23+ no-op rationales are sound |
| FND-P4-004 | All 10 leave-as-is items have solid rationales |
| FND-CC-007 | All 40 unique obsolete-claimed files verified deleted from disk |
| FND-CC-008 | Pass 1/Pass 2 decomposition coherent (27 + 43 = 70 non-obsolete items) |
| FND-P3-004 | Construction-queue interface boundary is a legitimate split point |
| — | No cross-phase contradictions found |

---

## Instruction-by-Instruction Assessment

### 1. Parametrize Sweep Quality — PASS

All 5 spot-checked parametrize consolidations (Tasks 3.13, 3.16, 3.19, 3.33, 3.44) preserve test discoverability and per-case error messages. `pytest.param(id=<descriptive_name>)` is consistently used. No regression-significant case is hidden behind an un-greppable parametrize ID. Two minor cosmetic inconsistencies noted (FND-P1-001, FND-P1-002).

### 2. CAT-12 Reference-Value Pattern — PASS (with one caveat)

The pattern is fundamentally sound across the three implementations examined (Tasks 5.18, 5.19, 5.23). The key risk — reference-value staleness when production formulas change — is well-managed by derivation docstrings. Task 5.19 has a precision mismatch between ~ approximations in the docstring and `rel=1e-9` assertion tolerance (FND-P2-001, MAJOR). Design.md references a deleted file as the canonical example (FND-P2-003).

### 3. CAT-11 Fragile-Assertion Replacements — PASS

Task 4.2 (`test_deprecated_code_removed.py`) was correctly handled as no-op. The existing `assert total <= EXPECTED_X_COUNT` pattern is a hard assertion with an adjustable threshold — this is the correct approach. Converting to `pytest.skip` or `pytest.warns` would have destroyed regression signal. Task 5.12 actually strengthened regression signal via stricter `issubset` check. Task 5.8 (split conditional assertions) and Task 5.10 (split prioritization test) both correctly improved failure diagnosis.

### 4. Task 3.34 Deferral — PARTIALLY JUSTIFIED, recommend parametrize now

The stated rationale ("per-class structure aligns with production") is factually weak: production handlers are split across 5 sub-module files, but the test file is a monolithic 1899-line file. The genuine concern — construction-queue handlers use `entity_id` instead of `fleet_id` — is resolvable with a two-group parametrization. The Task 3.2 precedent in the same project phase already demonstrated successful class-level parametrize across handler classes. Estimated savings: ~75 LOC with no organizational clarity loss. **Recommend adding to continuation work.**

### 5. ≥3-Member Threshold Rule — CORRECTLY ENFORCED

Tasks 3.15 and 3.27 are correctly left as-is — 2-member clusters truly do not benefit from parametrization. Task 3.37 has 4 zero/negative cargo amount tests (across load/unload) that are textbook 2-member parametrize candidates and were unnecessarily blocked by the threshold rule (FND-P1-003, MIN).

### 6. Below-the-Line Items — ALL SOUND

- **S10-CAT12-R01** (rejected): Correctly rejected. `isdisjoint()` vs `len(overlap)==0` is pure style preference; the test verifies a behavioral invariant.
- **S09-CAT12-OOS01-04** (4 out-of-scope): Correctly classified. All are legitimate property-based tests asserting hardcoded constants against production output.
- **S11-CAT10-OOS01** (out-of-scope): Correctly classified. 10 boundary tests with genuinely distinct edge cases and assertion logic.
- **S11-CAT12-OOS01** (out-of-scope): Correctly classified. Legitimate pygame integration test verbosity.

### 7. Continuation Recommendations

| Priority | Item | Est. LOC | Rationale |
|----------|------|----------|-----------|
| 1 (highest) | Task 3.34: Parametrize 11 fleet_not_found tests | ~75 saved | Largest remaining P2-appropriate opportunity. DUP-002 is non-blocking. Two-group approach respects interface boundary. |
| 2 | Task 3.37: Parametrize zero/negative cargo pairs | ~10 saved | Simple 2-member parametrize, previously blocked by threshold rule. |
| 3 | Task 4.12: Behavioral assertion for stateless renderer | ~5 LOC | Low-effort refinement of already-correct test. |
| 4 | Fix FND-CC-001 false-positive checkmarks | 0 LOC | Documentation fix in phase_3_checklist.md. |
| 5 | Fix FND-CC-002 terminology mismatch | 0 LOC | Clarify plan.md header between "items" and "tasks". |
| 6 | Fix FND-P2-001 precision mismatch | ~3 LOC | Add intermediate values to Task 5.19 docstring or relax tolerance. |

---

## Agent Reports

Detailed findings from 5 specialized agents:
- [Agent 1: Parametrize Sweep Quality & Threshold Rule](findings/agent_1_parametrize_quality.md)
- [Agent 2: CAT-12 Reference-Value Pattern & CAT-11 Fragile Assertions](findings/agent_2_cat12_cat11_assertions.md)
- [Agent 3: Task 3.34 Deferral Audit](findings/agent_3_task334_deferral.md)
- [Agent 4: Below-the-Line Items & Continuation Work](findings/agent_4_belowline_continuation.md)
- [Agent 5: Cross-Cutting Consistency](findings/agent_5_crosscutting.md)
