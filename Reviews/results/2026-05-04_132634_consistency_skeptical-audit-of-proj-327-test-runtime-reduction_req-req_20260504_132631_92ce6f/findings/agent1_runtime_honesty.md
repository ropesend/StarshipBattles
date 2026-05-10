# Agent 1 — Runtime Honesty Skeptical Audit: PROJ-327

**Review target:** PROJ-327 cumulative runtime delta claims
**Date:** 2026-05-04
**Documents audited:** `runtime_delta.md`, `virtual_table_runtime.md`, `phase_2_runtime_delta.md`, `phase_3_runtime_delta.md`, `baseline_2026-05-04.md`, `plan.md`, `decisions.md`

---

## CRIT: File-level delta (30ms) cannot mechanically produce the claimed suite-level delta (3.9s)

**Claim being challenged:**

Phase 1 migrated 80 of 81 `@patch` decorators in `test_virtual_table.py` to one autouse fixture. The document claims this produced a **3.9s median suite-level wall-clock reduction** (127.8s → 123.9s), corresponding to a **3.9s slowest-shard reduction** (127.7s → 123.8s). The cumulative project report (`runtime_delta.md`) attributes essentially the entire -3.9s improvement to Phase 1 alone, with Phases 2/3/4 acknowledged as "in the noise floor."

**Evidence from the documents:**

1. **File-level delta is explicit and tiny:** `virtual_table_runtime.md` lines 6-14 tabulate single-process file-only runs. Pre-migration median: 1.03s. Post-migration median: 1.00s. **File delta: 30ms** (~3% reduction). The document itself acknowledges (line 14): *"modern unittest.mock decorator overhead is much less than 1 ms per patch on this hardware. The actual saving is the order of ~30-50 ms."*

2. **Prediction overshoot was 50× in the wrong direction:** `runtime_delta.md` line 22 (Phase 1 Notes): *"predicted-magnitude (~1.4 s/file) overshot by ~50× because modern unittest.mock decorator overhead is sub-millisecond per patch."* The prediction was ~1.4s file-level reduction; actual was 30ms — **50× smaller, not larger.**

3. **The amplification claim is mechanically impossible:** `virtual_table_runtime.md` lines 26-27 attempt to explain the 3.9s suite delta: *"The slowest-shard delta (3.9 s) is roughly the per-test reclaim (~30 ms × 16 tests = ~0.5 s) amplified by the fact that other tests in the same shard depend on this file's runtime budget."* This math is internally contradictory:
   - 30ms × 16 tests = 480ms (0.48s), not 3.9s
   - The 30ms figure is the *whole file* delta (all 24 tests together), not per-test
   - Even if it were per-test: 30ms × 16 = 480ms, needing ~8× additional "amplification" to reach 3.9s
   - "Other tests depending on this file's runtime budget" is not a real causal mechanism — test shards run tests sequentially; finishing one file 30ms faster saves exactly 30ms from the shard wall-clock, period

4. **The shard balancing argument doesn't rescue it:** On a 24-thread, 12-shard runner with greedy bin-packing, a 30ms reduction in one file (of ~128s total runtime) changes the bin-packing assignment by at most 30ms — it cannot redistribute enough work to save 3.9s from the slowest shard. The file in question (`test_virtual_table.py`, 1.03s) is ~0.8% of a single shard's runtime budget. Saving 30ms from it saves at most 30ms from the slowest shard.

**Conclusion:**

The claimed 3.9s suite-level delta is **causally disconnected from the 30ms file-level code change that supposedly produced it**. A 30ms saving on one file cannot, through any described or plausible mechanism, reduce the slowest shard's wall-clock by 3.9s. The 130× discrepancy between file-level delta (30ms) and claimed suite-level delta (3.9s) is unexplained by the documents' own data and attempted explanations. **The headline -3.9s claim should be reduced to the file-level 30ms or removed pending re-measurement with controlled conditions.**

---

## CRIT: Run-to-run variance exceeds the claimed delta — measurement is not reliable

**Claim being challenged:**

The project reports a **3.9s median reduction** (127.8s → 123.9s) as the cumulative outcome, presented as a real improvement attributable to the code changes.

**Evidence from the documents:**

1. **Pre-baseline range is 15.3s:** `baseline_2026-05-04.md` documents 3 runs: 124.6s, 139.9s, 127.8s. Range = 15.3s. The document itself (line 141) states: *"Run 2 vs run 3 variance: 12 s. The ±10% noise in the design.md is real on this hardware."* The claimed 3.9s delta is **only 25% of the 15.3s observed range** for identical code.

2. **Post-baseline range is 5.3s:** Post-Phase-1 runs in `virtual_table_runtime.md`: 122.3s, 123.9s, 127.6s. Range = 5.3s. Again, the 3.9s delta is **within the post-change run-to-run range** for identical code.

3. **Clean-run vs clean-run comparison shows near-zero delta:** The only directly comparable pair of fully-clean, full-test-count runs:
   - Pre Phase 1, Run 3: 127.8s (clean, 16345 tests)
   - Post Phase 1, Run 3: 127.6s (clean, unknown test count but presumed ~16345+)
   - **Delta: 0.2s** — indistinguishable from zero given the 12s run-to-run spread

4. **The pre baseline median is inflated by a ±10% noise outlier:** Pre Run 2 at 139.9s is 12.1s slower than the adjacent clean Run 3 (127.8s). The document acknowledges this as within the ±10% noise band. This single outlier contributes significantly to the pre median: without it, the pre median of [124.6, 127.8] would be 126.2s. The claimed -3.9s shrinks to -2.3s even under this charitable (and methodologically improper) exclusion.

5. **Pre-baseline minimum is already near post-baseline median:** Pre Run 1 was 124.6s (albeit a partial run with a collection error — 14951 tests vs 16345). The post median of 123.9s is only 0.7s faster than a pre run that tested fewer files. The overlap in distributions is substantial.

6. **Test count drift between measurements:** Pre-baseline clean runs collected 16345 tests. Final cumulative runs collected 16468 tests (+123 tests, +0.75%). Runtime deltas should account for test-count changes but don't.

7. **`runtime_delta.md` line 42 honestly concedes the noise problem:** *"Phase 2's 330 ms of single-process reclaim and Phase 4's pattern landing did not show up in the median wall-clock — they're inside the noise floor (run-to-run variance was 2.7 s between this round's fastest and slowest runs of identical code)."* If a 2.7s variance can obscure 330ms of reclaim, then a 3.9s delta is only marginally above the noise floor for the post-data, and well within it for the pre-data (15.3s range).

**Conclusion:**

The claimed -3.9s median delta is **not statistically distinguishable from measurement noise** when:
- The pre-baseline 3-run range is 15.3s (the delta is 25% of the range)
- The post-baseline 3-run range is 5.3s (the delta is 74% of the range — better but still within the noise envelope)
- The best clean-to-clean individual run comparison (both Run 3) shows only 0.2s difference
- The document itself acknowledges ±10% noise (12.8s) as normal on this hardware
- Only 3 runs per measurement with 15.8s pre-baseline variance — sample size is far too small for the claimed effect size

**The -3.9s result requires controlled, larger-n measurement before it can be attributed to code changes rather than ambient machine noise.** A minimum of 5-7 runs per condition (pre/post) with outlier rejection would be needed to claim a 3.9s effect against ~12s of observed noise.

---

## MAJ: The phased measurement samples overlap — Phase 0 baseline and Phase 1 "pre" are the same 3 runs

**Claim being challenged:**

The per-phase breakdown table in `runtime_delta.md` (line 22) credits Phase 1 with "~3.9 s wall reclaim (127.7 → 123.8 slowest shard)" as if it were an independent measurement.

**Evidence from the documents:**

1. **Phase 0 "baseline" and Phase 1 "pre" are identical data:** `baseline_2026-05-04.md` lines 21-24 (Phase 0 Task 0.1): runs at 124.6s, 139.9s, 127.8s. `virtual_table_runtime.md` lines 18-21 (Phase 1 pre): runs at 124.6s, 139.9s, 127.8s. **Exact same three numbers.**

2. **No independent Phase 1 baseline was taken.** The Phase 0 baseline serves double duty as the Phase 1 pre-migration measurement. This is not a measurement error — it's reasonable to use the Phase 0 numbers as "pre" for Phase 1 since no other code changed between phases. But it means the *entire* claimed cumulative delta of 3.9s is just one comparison: Phase 0 baseline vs Phase 5 post. The per-phase breakdown is not independently measured.

3. **The per-phase attribution is retrofitted.** The documents show:
   - Phase 1: 3.9s delta (from Phase 0 baseline to Phase 1 post)
   - Phase 2: 330ms single-process, "sub-second; lost in shard balancing"
   - Phase 3: 0s (no code change)
   - Phase 4: "~no measurable change"
   - Cumulative: 3.9s (same as Phase 1)
   
   But Phases 2/3/4 were measured AFTER Phase 1's 3.9s delta was already claimed. The cumulative says Phase 1 = 3.9s, Phases 2-4 = noise, total = 3.9s. This is consistent IF Phase 1 truly delivered 3.9s, but circular if Phase 1's 3.9s is itself noise (as argued in CRIT-1 above).

**Conclusion:**

The per-phase attribution breakdown is **analytically hollow** — only one before/after measurement pair exists (Phase 0 baseline vs Phase 5 final), and the full 3.9s is claimed for Phase 1. The Phase 2-4 "sub-second / 0 / no change" attributions are qualitatively different (single-process per-file) and don't validate or even relate to the 3.9s sharded delta. This is not fraudulent — the document is honest that Phases 2-4 are noise — but it presents a multi-phase attribution where only one phase actually moved the needle, and that needle-movement is itself suspect.

---

## MAJ: Pre-baseline Run 2 (139.9s) is the dominant driver of the claimed delta

**Claim being challenged:**

The 3.9s median reduction represents a real, sustained improvement.

**Evidence from the documents:**

1. **Sensitivity analysis of the pre baseline median to the Run 2 outlier:**
   - With Run 2 (139.9s): pre median = 127.8s, post median = 123.9s, delta = -3.9s
   - Without Run 2 (only 124.6s and 127.8s): pre median = 126.2s, delta = -2.3s
   - If Run 2 were at the mean of the other two (126.2s): pre median would be ~126.2s, delta = -2.3s
   - **Run 2 alone contributes ~1.6s of the claimed 3.9s delta** (3.9 - 2.3 = 1.6)

2. **The 139.9s value is characterized as "clean"** — 16345 tests, 16341 passed, 0 errors. The document attributes the slowness to "±10% noise on this hardware." But the mechanism of 12s slowdown for identical code on a sequential run is unexplained and uninvestigated — thermal throttling? background process? disk cache state? page cache warmth?

3. **Post-baseline Run 2 (123.9s) had a different anomaly** — an LLM background flake error. Both baselines' Run 2 slots contain anomalous runs, but in opposite directions (pre-slow, post-not-as-slow).

4. **Run 1 is also questionable in both baselines:**
   - Pre Run 1 (124.6s): collection error in shard 6 — partial run (14951/16345 tests)
   - Post Run 1 (122.3s): claimed clean, but if it was truly clean, it's 5.5s faster than clean Pre Run 3 (127.8s) — a large jump in the wrong direction relative to the 30ms code change

**Conclusion:**

Of the 3 runs in each baseline condition, **at least 1 is anomalous in each set** (pre Runs 1+2 both have documented issues; post Run 2 has a documented flake). The pre median is materially inflated by Run 2's 139.9s outlier. **At minimum 40% of the claimed -3.9s delta (1.6s) is attributable to this single outlier run rather than to any code change.** A robust measurement would exclude anomalous runs or use enough samples that outliers don't dominate the median of 3.

---

## MAJ: The claimed 3.9s reclaim contradicts the document's own cost model

**Claim being challenged:**

Phase 1 produced ~3.9s suite-level reclaim.

**Evidence from the documents:**

1. **Own-admitted per-patch overhead is sub-millisecond:** `virtual_table_runtime.md` line 14: *"modern unittest.mock decorator overhead is much less than 1 ms per patch on this hardware."* At sub-1ms per patch × 80 patches removed = at most ~80ms saving per file run. The actual measured 30ms is consistent with this.

2. **Own-admitted magnitude:** `runtime_delta.md` line 22, Phase 1 Notes: *"predicted-magnitude (~1.4 s/file) overshot by ~50×"* — i.e., the actual file-level saving was 50× smaller than predicted. The predicted 1.4s was based on a now-disproven 1ms-per-patch assumption.

3. **Per-test enter/exit accounting:** `virtual_table_runtime.md` line 14 reveals the refined estimate: *"5 enter/exit collapses × 16 tests × ~2 ms each"* = ~160ms. Still far below 3.9s.

4. **The shard composition doesn't support amplification:** The slowest shard runs ~128s of tests. `test_virtual_table.py` at 1.03s is 0.8% of that shard. Reducing it by 30ms can only reduce the shard by 30ms — the remaining ~127s of other tests are unaffected.

5. **No other Phase 1 changes are claimed.** The Phase 1 change was exclusively to `test_virtual_table.py`. No other file was modified in Phase 1.

**Conclusion:**

The project's **own cost model predicts, at most, a few hundred milliseconds of suite-level improvement from Phase 1** (30ms per-file × the shard multiplier of 1, since the file can only be on one shard). The claimed 3.9s is 13-130× larger than the cost model can account for. The project acknowledges the prediction overshoot but then claims a measurement that is equally implausible in the opposite direction. **Either the measurement or the cost model is wrong — they cannot both be right.** Given that the cost model is grounded in observable mechanism (patch decorator overhead, confirmed by the 30ms file-level measurement and modern mock library behavior) and the measurement is grounded in 3 noisy samples, **the measurement is the more likely source of error.**

---

## MAJ: The "stretch target" framing misrepresents scope — 90s target was never addressable by this project

**Claim being challenged:**

The project frames the gap to the 90s stretch target as a finding ("gap of ~34 s remains") when the target was structurally unreachable by PROJ-327's scope.

**Evidence from the documents:**

1. **Phase 0 already knew the 90s target was unreachable:** `baseline_2026-05-04.md` lines 131-134 (Task 0.7 Realistic outlook): *"Phase 1 alone is expected to reclaim ~1.4 s... The bulk of the runtime is in the integration tests (build_queue_screen ~45 s on its own)... Phase 4 trigger is already armed."*

2. **PROJ-327's scope is exclusively the 9 PROJ-322 deferred items** — none of which touch the top time-consuming files (build_queue_screen, race_setup_ships_smoke, quickstart_designs, test_main_integration). The plan.md Scope section is explicit: *"Out: General test runtime improvements not on the deferred list."*

3. **Phase 4 was conditional and the trigger fired.** The plan says Phase 4 executes *"Only if Phases 1-3 have not reduced runtime below the user's target (≤ 90 seconds)."* Phases 1-3 did not achieve this. Phase 4 was executed and delivered "no measurable change" at the suite level. The project exhausted its scope and did not reach 90s — which was entirely predictable from Phase 0.

4. **The "remaining gap" language implies partial progress toward 90s when the project did not actually target the heavy files.** The ~34s gap is composed entirely of files outside PROJ-327's mandate.

**Conclusion:**

This is **MIN** severity (presentation, not data dishonesty). The project's `runtime_delta.md` and `decisions.md` honestly identify where the real runtime lives and that PROJ-327 didn't touch it. However, repeatedly tabulating the "gap to 90s" (virtual_table_runtime.md line 32 table, runtime_delta.md line 15) gives the misleading impression that PROJ-327 made partial progress toward 90s. In reality, PROJ-327 measured the 90s gap and confirmed it lives in untouchable files. The *-3.9s* claimed (even if real) is only 10% of the ~38s gap measured at Phase 0, and the gap composition is unchanged.

---

## INFO: Test count growth between measurements undermines direct comparison

**Claim being challenged:**

The Phase 0 baseline and Phase 5 final measurement are directly comparable.

**Evidence from the documents:**

1. **Phase 0 runs:** 16345 tests (clean runs 2 and 3; Run 1 had 14951 with collection error)
2. **Phase 5 final runs:** 16468 tests (all 3 runs)
3. **Net test growth:** +123 tests (+0.75%) between Phase 0 baseline and Phase 5 final
4. **Source of new tests:** Phase 4 added 17 smoke tests for the Compositional Construction pattern; the remaining ~106 additional tests likely came from other commits on the `feat/03c-phase-aware-execution` branch between measurements.
5. **No adjustment for test count:** The documents compare raw wall-clock times without normalizing for the additional test work. If the new tests average even 100ms each, that's ~12.3s of additional work — enough to entirely mask a real -3.9s improvement if the machine was running slightly faster on the post measurement day.

**Conclusion:**

The test count difference is small (0.75%) but the comparison is non-trivial because the tests were added by other work on the shared branch. The project should note the test-count discrepancy and ideally run a Phase 0 re-baseline at the final test count for clean comparison. This is a **MIN** concern — small enough that it probably doesn't change the outcome, but large enough to note for methodological completeness.

---

## SUMMARY

| Severity | Finding |
|----------|---------|
| **CRIT** | 30ms file-level delta cannot mechanically produce 3.9s suite-level delta (130× gap unexplained) |
| **CRIT** | Run-to-run variance (15.3s pre range, 5.3s post range) exceeds the claimed 3.9s delta; measurement unreliable at n=3 |
| **MAJ** | Phased measurements overlap — only one before/after pair exists; per-phase attribution is hollow |
| **MAJ** | Pre Run 2 outlier (139.9s) alone contributes ~1.6s (41%) of the claimed 3.9s delta |
| **MAJ** | Project's own cost model predicts at most ~160ms suite-level Phase 1 reclaim, not 3.9s |
| **MAJ** | "Gap to 90s" framing obscures that PROJ-327 could never address the heavy files |
| **INFO** | +123 tests between Phase 0 and Phase 5 runs; raw wall-clock comparison is imperfect |

**Overall verdict:** The -3.9s cumulative claim is **not credible at the claimed effect size or causal attribution**. The 30ms file-level change (removing 80 `@patch` decorators) is real, well-measured, and mechanically sound. But the suite-level delta is dominated by measurement noise and outlier runs. The honest contribution of Phase 1 to suite-level runtime is more likely in the **tens to low hundreds of milliseconds** range — consistent with the project's own cost model and file-level measurement. The project documents contain seeds of this honesty (`runtime_delta.md` line 42 acknowledges the noise floor) but the headline number of -3.9s is not supported by the evidence presented.
