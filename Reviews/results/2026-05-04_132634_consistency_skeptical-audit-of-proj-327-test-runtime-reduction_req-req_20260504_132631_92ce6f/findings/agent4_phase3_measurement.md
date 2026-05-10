# Agent 4: Skeptical Audit — PROJ-327 Phase 3 Measurement Quality

**Date:** 2026-05-04
**Scope:** `phase_3_runtime_delta.md` + `phase_3_checklist.md` — measurement accuracy, mathematical consistency, and zero-runtime-change honesty.

---

## 1. DUP-001: MATHEMATICALLY IMPOSSIBLE RUNTIME CLAIM

### The contradicting statements

**Source A — `phase_3_runtime_delta.md:17,21`:**
> Combined runtime: 1.73 s for 39 tests (1 run)
> [...]
> Setup time is ~3.6 s of `_get_setup_time(test) for test in tests` **(sum)**, test-body time is sub-millisecond.

**Source B — `phase_3_checklist.md:26`:**
> Construction IS dominant — total setup ~3.6 s **of the** 1.73 s combined runtime

### Why it's impossible

3.6 s > 1.73 s. Setup cannot be 3.6 seconds *of* a 1.73-second total. Either:

1. The 3.6s is a SUM of individually-run per-test setup times (each test run in isolation incurs fresh import costs that the combined run amortizes), while 1.73s is wall-clock of all 39 tests in one process. This would be comparing CPU-time-across-isolated-runs vs. wall-clock-of-combined-run — a category error.
2. The `_get_setup_time()` function (which **does not exist anywhere in the codebase** — grep returned zero matches) is double-counting shared import/setup work.
3. The claim is fabricated or an error.

### What the numbers most likely mean

From the `--durations=10` breakdown (line 18-19):
- 4 tests at ~0.42 s each = ~1.68 s (attributed to "one-time import + Mock construction")
- Remaining 35 tests at ~0.05 s each = ~1.75 s
- Sum of individual test durations ≈ 3.43 s

But the **combined wall-clock** is 1.73 s, because pytest amortizes the one-time import across all tests in a single run. The `--durations` report assigns the full cost to the first few tests that trigger the import.

The 3.6 s "setup time" figure is therefore the **SUM** of per-test durations from `--durations=10` (or from `_get_setup_time` running each test individually), not the actual wall-clock setup portion.

### The conflation

The `phase_3_checklist.md:26` drops the "(sum)" qualifier and writes:

> total setup ~3.6 s **of the** 1.73 s combined runtime

This phrasing implies setup is a *subset* of the 1.73 s total. It is not. It is a sum across individually measured tests. The `phase_3_runtime_delta.md` is more honest (it includes "(sum)"), but then still says "Construction IS dominant" comparing the sum figure to the wall-clock figure — an apples-to-oranges comparison.

### Does this invalidate the decision?

**No.** The decision (re-confirmed deferred) rests on the **mutation surface** argument (lines 23-26 of `phase_3_runtime_delta.md`), not on the specific setup magnitude. Even with correct per-test figures (~44 ms wall-clock per test, dominated by ~43 ms setup), the argument stands: every test mutates `mock_fleet.orders`, `mock_fleet.path`, or reassigns return values — resetting these per-test costs the same as fresh construction.

### Severity assessment

| Category | Rating |
|----------|--------|
| Measurement methodology | **FLAWED** — sum of individual-test measurements compared to combined wall-clock |
| Checklist accuracy | **MISLEADING** — drops "(sum)" qualifier, creates impossible reading |
| Decision validity | **UNCHANGED** — decision rests on mutation-surface reasoning, not magnitude |
| Documentation honesty | **PARTIAL** — `phase_3_runtime_delta.md` includes "(sum)" but still makes the apples-to-oranges comparison |

### Recommendation

Correct the `phase_3_checklist.md:26` line to:

> Construction IS dominant (per-test setup ~43 ms wall-clock; test-body sub-millisecond). The 3.6s figure is the SUM of individually-measured per-test setup times, not the wall-clock component of the 1.73s combined run.

And add a footnote to `phase_3_runtime_delta.md:21` explaining that the 3.6s sum exceeds the 1.73s combined wall-clock because per-test isolation measurements include redundant import/Mock construction that the combined run amortizes.

---

## 2. HLP-001: MEMOIZATION ANALYSIS — PLAUSIBLE BUT UNVERIFIED

### The claims

**Microbenchmark (measured):** 10,000 calls in 6.27 s = **627 µs/call** ✓

**Per-file impact (measured):** 115 calls × 627 µs = **~72 ms** in `test_fleet_report_filters.py` (3.6% of 1.99 s file runtime) ✓

**Memoization rejected because:**
> "Memoization gain is marginal (~50 ms max reclaim per file after deepcopy-on-retrieval cost) and complexity-positive"

### What's verified vs. speculative

| Claim | Measured? | Verdict |
|-------|-----------|---------|
| 627 µs/call | Yes (10K iteration) | Credible |
| 72 ms per-file overhead | Yes (call count × per-call) | Credible |
| Hash + deepcopy ≈ 600 µs | **No — zero measurement** | Speculative |
| Memoization gain marginal | **No** | Derived from speculative cost |
| 4 file shapes are distinct | Yes (manual inspection) | Credible |

### The unstated stronger argument

The document doesn't make the strongest case: **115 calls × 627 µs = 72 ms in a file that takes 1.99 seconds.** Even if memoization were perfectly free, the absolute maximum gain is 72 ms (3.6%). In single-process terms, that's below the noise floor. In sharded terms (median wall 123.9 s per Phase 5 data), 72 ms is 0.06% of total runtime — truly negligible. The decision is correct even without the speculative hash+deepcopy cost estimate; the memoization analysis is therefore **unnecessary complexity that pretends to precision it doesn't have**.

### Severity

| Category | Rating |
|----------|--------|
| Microbenchmark | Sound |
| Memoization cost estimate | Unmeasured — speculative |
| Decision validity | Correct — the maximum win (72 ms) is below noise floor regardless of memoization cost |

---

## 3. ZERO-RUNTIME-CHANGE HONESTY: CONFIRMED

### Claim

> "Phase 3 produces **ZERO runtime change** (no code changes; both items re-confirmed deferred)."

### Verification

`git show --name-only 3b8839a86` (the Phase 2+3 commit):

```
Projects/active_projects/PROJ-322/phase_2_checklist.md  (docs)
Projects/active_projects/PROJ-322/phase_3_checklist.md  (docs)
Projects/active_projects/PROJ-322/phase_6_checklist.md  (docs)
Projects/active_projects/PROJ-327/findings/phase_2_runtime_delta.md  (docs)
Projects/active_projects/PROJ-327/findings/phase_3_runtime_delta.md  (docs)
Projects/active_projects/PROJ-327/phase_2_checklist.md  (docs)
Projects/active_projects/PROJ-327/phase_3_checklist.md  (docs)
Projects/active_projects/PROJ-327/plan.md  (docs)
```

**Zero production files changed. Zero test files changed.** The "no commit" language in `plan.md:30` is technically inaccurate (there IS a commit, 3b8839a86) but its meaning — "no code changes" — is correct.

### Hidden regression check

- No test file was modified → no annotation/fixture change could affect test behavior
- No production file was modified → no import chain change
- Only `.md` files were created/edited → no Python bytecode change

**Verdict: No hidden regression. Genuinely zero runtime change.**

---

## 4. Aggregate Phase 3 Measurement Quality Score

| Dimension | Score | Notes |
|-----------|-------|-------|
| DUP-001 measurement validity | **1/5** | Mathematically impossible numbers; apples-to-oranges comparison; phantom function cited |
| DUP-001 decision validity | **4/5** | Decision rests on valid mutation-surface reasoning independent of flawed numbers |
| HLP-001 measurement validity | **3/5** | Microbenchmark is sound; memoization cost estimate is pure speculation |
| HLP-001 decision validity | **5/5** | Even max gain (72 ms) is below noise floor; decision is correct regardless |
| Zero-runtime-change claim | **5/5** | Verified — no code touched |
| Documentation precision | **2/5** | Checklist drops "(sum)" qualifier, creating impossible reading |

### Overall: 3.3/5 — Measurement quality is below par; decision quality is sound.

The measurement evidence was meant to be the **primary deliverable** of Phase 3 ("future audits won't re-litigate these from scratch — they'll see the measurement and the disposition trail"). But the DUP-001 measurement is self-contradictory. A future auditor who does the math will reject the measurement evidence and have to re-measure from scratch. The disposition trail IS valuable — the *reasons* for deferral are well-documented and valid — but the *numbers* attached to DUP-001 do not withstand scrutiny.
