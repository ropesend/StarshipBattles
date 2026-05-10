# Skeptical Audit of PROJ-327 Test Runtime Reduction — Report

**Review type:** consistency  
**Request ID:** req_20260504_132631_92ce6f  
**Review date:** 2026-05-04  
**Scope:** PROJ-327 project (all 6 phases + findings + decisions), Phase 1-4 test/production files, patterns docs  
**Review mode:** Normal (full scrutiny, 6 agent shards)  

---

## Executive Summary

PROJ-327 is a test-quality project with two distinct deliverables: (1) a claimed -3.9s sharded-suite runtime reduction, and (2) disposition of 9 PROJ-322 deferred items. The second deliverable is solid — all 9 deferrals have updated rationales, the Phase 2 fixtures are safely rescoped, the Phase 1 patches are correctly migrated, and the Phase 4 composition provides a genuine (if shallow) improvement over the monkey-patch pattern it replaced.

**The first deliverable — the headline -3.9s runtime reduction — does not withstand scrutiny.** The 30ms file-level improvement in `test_virtual_table.py` cannot mechanistically produce a 3.9s suite-level delta (a 130× amplification with no causal explanation). The measurement data shows run-to-run variance (15.3s range) that dwarfs the claimed delta. The pre-baseline median is materially inflated by an anomalous 139.9s outlier run. The project's own cost model predicts at most ~160ms suite-level reclaim from Phase 1, not 3.9s.

The honest runtime contribution of PROJ-327 is likely in the **tens to low hundreds of milliseconds** range — the ~330ms single-process reclaim from Phase 2's `test_ship_io.py` registry rescope, plus whatever Phase 1's 30ms file-level change actually contributed to the sharded suite (at most 30ms per the slowest shard). The -3.9s headline number should be revised or retracted pending controlled re-measurement.

---

## CRITICAL Findings

### CRIT-001: 30ms file-level delta cannot produce 3.9s suite-level delta

**Files:** `findings/virtual_table_runtime.md:6-28`, `findings/runtime_delta.md:17-26`

Phase 1 removed 80 `@patch` decorators from `test_virtual_table.py` and measured a **30ms file-level delta** (1.03s → 1.00s). The project then claims a **3.9s suite-level (sharded) wall-clock reduction** from this change.

The amplification is mechanistically impossible:
- `test_virtual_table.py` runs on exactly one shard and finishes in 1.03s (0.8% of a shard's budget)
- Saving 30ms from one file saves exactly 30ms from its shard's wall-clock
- The remaining ~126s of other tests in the shard are unaffected
- The project's attempted explanation (30ms × 16 tests = 0.48s "amplified" by shard balancing) produces 0.48s, not 3.9s, and the "amplification" mechanism is not real

**The claimed 3.9s delta is 130× larger than the file change can produce.** The measurement is either from an uncontrolled variable (machine state, thermal, background processes) or the 3.9s between Phase 0 median and Phase 5 median is coincidental.

**Recommendation:** Retract the -3.9s headline number. Report only the file-level delta (30ms) and the Phase 2 per-file reclaim (~330ms single-process). Re-measure with 7+ runs per condition and outlier rejection if a suite-level claim is required.

---

### CRIT-002: Measurement noise exceeds claimed delta — result not statistically reliable

**Files:** `findings/baseline_2026-05-04.md:21-24`, `findings/virtual_table_runtime.md:18-23`

The 3-run measurement protocol produces a 15.3s range for identical code (pre-baseline min 124.6s, max 139.9s). The claimed -3.9s delta is **25% of the pre-baseline range** and **74% of the post-baseline range** — in both cases, well within the noise envelope.

Key data points:
| Pre runs | Wall (s) | Post runs | Wall (s) |
|---|---:|---|---|
| Run 1 | 124.6 (partial) | Run 1 | 122.3 |
| Run 2 | **139.9** (clean, anomalous) | Run 2 | 123.9 (flake) |
| Run 3 | 127.8 (clean) | Run 3 | 127.6 (clean) |
| **Median** | **127.8** | **Median** | **123.9** |

- Pre Run 2 at 139.9s is 12.1s slower than Pre Run 3 — a ±10% noise anomaly acknowledged by the project
- Pre Run 1 was a partial run (collection error, 14951/16345 tests)
- In each baseline set, only 1 of 3 runs was fully clean with full test count
- The best clean-to-clean comparison (both Run 3, full test counts): **0.2s delta** — indistinguishable from zero
- Pre Run 2 alone contributes ~1.6s of the claimed 3.9s delta (if Run 2 were excluded, pre median drops to 126.2s, delta shrinks to -2.3s)

**Recommendation:** Run a minimum of 7 measurements per condition with outlier rejection (remove runs >2σ from the local mean) before claiming a delta of this magnitude. Track test count to ensure clean comparison. Report confidence intervals, not just medians.

---

## MAJOR Findings

### MAJ-001: Per-phase breakdown is analytically hollow — only one before/after pair exists

**Files:** `findings/runtime_delta.md:22-26`

The per-phase table credits Phase 1 with -3.9s, Phase 2 with "sub-second", Phase 3 with 0s, and Phase 4 with "~no measurable change." But only one sharded measurement pair was taken: Phase 0 baseline vs Phase 5 final. Phases 1-4 were measured at the per-file (single-process) level but attributed to the sharded (parallel) result. The Phase 0 baseline numbers and Phase 1 "pre" numbers are identical — they are the same 3 runs.

This is not fraudulent (the document acknowledges Phases 2-4 are noise-level), but the tabular presentation implies four independently measured contributions to a 3.9s total when only the Phase 0→Phase 5 comparison exists as a sharded delta, and the full 3.9s is retro-attributed to Phase 1.

---

### MAJ-002: DUP-001 measurement conflation — 3.6s setup cannot be "of" a 1.73s combined runtime

**Files:** `findings/phase_3_runtime_delta.md:17-21`, `phase_3_checklist.md:26`

The Phase 3 documents claim "total setup ~3.6 s of the 1.73 s combined runtime" — which is mathematically impossible (3.6 > 1.73). The 3.6s figure is a **sum of individually-measured per-test setup times** (each including redundant import costs), compared to the combined wall-clock of 39 tests in one process (which amortizes the import once). The phase_3_checklist.md drops the "(sum)" qualifier, creating a flatly contradictory statement.

The decision to re-confirm DUP-001 as deferred is **still valid** — it rests on mutation-surface reasoning (every test mutates mock_fleet.orders/path, requiring per-test reset), not on the flawed magnitude claim. But the measurement evidence that was meant to anchor future audits will not survive scrutiny, undermining Phase 3's stated purpose.

**Recommendation:** Correct the checklist and delta doc to explain the sum-vs-wall-clock discrepancy. The measurement evidence for DUP-001 is salvageable as a per-test setup analysis (44ms wall-clock per test, ~43ms of which is setup) but the 3.6s-vs-1.73s comparison must be removed.

---

### MAJ-003: StrategyScreenComposition pattern does not eliminate bypass-init — tests still use `__new__`

**Files:** `tests/unit/ui/screens/test_strategy_screen.py:37`, `tests/fixtures/strategy_screen_composition.py:102-116`

The Phase 4 migration removed `patch.object(StrategyScreen, '__init__', lambda ...)` and centralized 8 inline MagicMock assignments into `MockStrategyScreenComposition().populate(screen)`. However, the migrated tests STILL use `StrategyScreen.__new__(StrategyScreen)` to bypass `__init__` entirely, and `populate()` sets private attributes directly (`screen._renderer = ...`) without ever calling `__init__`.

The composition seam (`composition=` kwarg on `StrategyScreen.__init__`) exists but is **exercised by zero tests**. The fixture docstring admits running the real `__init__` is "currently impractical" because upstream construction (Camera, StrategyUI, asset loading) is too heavy. The delivered artifact is a cleaner bypass-init pattern, not a true compositional construction as the name implies.

The anti-pattern claim in `decisions.md:55` that `patch.object(__init__, lambda ...)` is "strictly worse than `__new__` bypass-init" is **directionally correct for cross-test leaking** but **overstated for init-bug detection** — both approaches bypass `__init__` and share the same fragility.

**Recommendation:** The pattern doc (Pattern #32) should clarify that the `StrategyScreen` application is a partial seam (sub-objects only, not full init) and that true compositional construction requires the two-stage init pattern demonstrated by PROJ-325's `RaceSetupScreen`.

---

### MAJ-004: Lessons-learned scorecard conflates runtime and code-quality metrics

**Files:** `decisions.md:27-34`

The per-technique scorecard has columns "Wall-clock delta" and "LOC touched" and a "Verdict" column. Compositional Construction is rated "Highest tech-debt-per-LOC win" despite having "~no measurable change" in the Wall-clock delta column. The verdict switches metric domains mid-table — from runtime (every other row's verdict summarizes runtime impact) to code-quality.

By the table's own runtime metric, Compositional Construction at 0ms from +381 LOC is the **worst** ROI, not the best. If the scorecard intends to rate code-quality separately from runtime, it needs a distinct column.

---

### MAJ-005: Pattern §32 is a naming convention, not a reusable pattern

**Files:** `docs/02_PATTERNS.md` §32

The "Compositional Construction" pattern provides no generic infrastructure — no abstract base class, no reusable factory base, no composition registry. Every adoption requires writing a new Protocol + factory + mock from scratch. The claim that this is the "same shape" as PROJ-325's delegate factory and PROJ-322's widget factory is overstated — the three instances differ in method count, return types, and factory structure.

The pattern should be downgraded to a convention note under Pattern #15 (Factory) or #33 (UI Widget Test Factory), not promoted as a standalone canonical pattern. Alternatively, extract the generic infrastructure (a `Composition[Protocol]` base class with `register`/`make`/`mock`) so the pattern earns its slot.

---

## MINOR Findings

### MIN-001: Test count grew by +123 between Phase 0 and Phase 5, unaccounted in comparison

**Files:** `findings/baseline_2026-05-04.md`, `findings/runtime_delta.md:30-35`

Phase 0 baseline measured 16345 tests; Phase 5 final measured 16468 tests (+0.75%). The raw wall-clock comparison does not normalize for this. The 17 new Phase 4 tests are negligible, but if the remaining ~106 new tests average 100ms each, that could mask a real -3.9s improvement. Small effect, but incomplete methodology.

---

### MIN-002: HLP-001 memoization cost estimate is unmeasured speculation

**Files:** `findings/phase_3_runtime_delta.md:44-46`

The claim of ~600 µs for "hash + deepcopy" as part of memoization cost analysis has zero measurement backing. The decision is still correct (72ms max gain is below noise floor regardless), but presenting speculative numbers as analysis weakens the document's credibility.

---

### MIN-003: Known-issues section misplaces Compositional Construction under "measurable wall-clock wins"

**Files:** `docs/known-issues.md:130-135`

The technique with "~no measurable runtime change" is listed under a "measurable wall-clock wins" heading. This is a section-organization error, not a factual error.

---

### MIN-004: MockStrategyScreenComposition.populate() bypasses make_* methods in all 62 migrated tests

**Files:** `tests/unit/ui/screens/test_strategy_screen.py:81-82`

The 62 migrated strategy screen tests call `populate(screen)` which directly assigns attributes, never calling `make_renderer(screen)`, etc. The `make_*` methods are only exercised by the 17 standalone smoke tests. If a production `make_*` method were refactored to include side effects beyond construction, the 62 tests would not catch the change.

---

## Findings by Severity

| Severity | Count |
|---|---|
| CRITICAL | 2 |
| MAJOR | 5 |
| MINOR | 4 |
| INFO | 0 |

---

## Remediation Needed

### Priority 1 (before the -3.9s claim is cited externally)

1. **CRIT-001/CRIT-002:** Retract or caveat the -3.9s headline number. Replace with the measured per-file deltas (30ms Phase 1, ~330ms Phase 2 single-process). If a suite-level claim is necessary, re-measure with 7+ runs, outlier rejection, and confidence intervals.
2. **MAJ-002:** Fix the DUP-001 measurement conflating in phase_3_checklist.md and phase_3_runtime_delta.md. Explain that 3.6s is a sum of isolated per-test setup times, not a component of the 1.73s combined wall-clock.

### Priority 2 (documentation quality)

3. **MAJ-004:** Add a "Code quality impact" column to the decisions.md scorecard, or rewrite Compositional Construction's verdict to use non-misleading language.
4. **MAJ-005:** Downgrade Pattern §32 to a convention note or extract generic infrastructure.
5. **MAJ-003:** Clarify in Pattern §32 that the StrategyScreen application is partial seam only; distinguish from the true two-stage init pattern.

### Priority 3 (minor cleanup)

6. **MIN-001:** Note the +123 test count drift in the runtime delta document.
7. **MIN-003:** Move Compositional Construction out of the "measurable wall-clock wins" subsection in known-issues.md.

---

## What Went Well

The Phase 1 patch sweep is a **correct, zero-regression refactor** — all 24 tests produce identical outcomes with cleaner code. The Phase 2 fixture rescopes are **safe** — the audit confirmed zero attribute writes against shared fixtures. The Phase 3 disposition trail genuinely closes the loop on the PROJ-322 deferrals with measurement evidence (even if some numbers need correction). The Phase 4 composition seam is correct on its own terms (all 8 constructor signatures match, no mismatches) and eliminates the fragile `patch.object(__init__)` pattern from modules where it risked cross-test leaking.
