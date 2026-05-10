# PROJ-381 Bundling Decisions

**Source audit:** `Reviews/results/2026-05-07_220225_error-audit/`
**Bundling run date:** 2026-05-08
**Phase D protocol:** `Projects/protocols/14_create_from_error_audit.md` § Phase D — Interactive Bundling

---

## Default proposal (Phase D Step 1)

26 verified items → V=26 < 30 → single-project bundle per protocol's volume rule. Layer breakdown:

| Layer | Count |
|---|---|
| strategy | 20 |
| ui | 5 |
| assets | 1 |
| simulation | 1 |

Cross-layer boundary findings were placed in the bundle owning the upstream end of the boundary — all 7 verified cross-layer items had strategy or ui as the upstream end, both of which already sat in the single bundle, so no special routing was required.

| # | Title | Layers | Verified | Uncertain | Phases |
|---|-------|--------|----------|-----------|--------|
| 1 | Error handling cleanup — strategy/ui/assets/sim (2026-05-07) | strategy, ui, assets, simulation | 26 | 1 | 1 Critical, 2 Major, 3 Minor |

## User adjustments (Phase D Step 2)

User accepted the single-project proposal as-is. Two alternatives were offered and declined:

- **Split foundation vs presentation** (strategy + assets + sim = 21 items vs ui = 5 items). Declined — UI bundle would have been too small.
- **Split by category** (cross-layer boundaries = 7 vs broad-except/json hygiene = 19). Declined — the user prefers shipping the CRITICAL boundary fix first inside the same project rather than separating it from related strategy-layer work.

## UNCERTAIN resolution (Phase D Step 3)

| ID | Verifier note | User decision |
|---|---|---|
| ERR-04-007 | `star_generation_config.py:192` catches an over-broad tuple `(ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError)`. Narrowing to drop `ValueError` and `KeyError` is the audit's recommendation, but the existing tuple may be intentional defensive caching for a singleton-cached factory. Verdict left UNCERTAIN — user judgement required. | **Include** — narrow the catch tuple. User accepts that malformed config now raises rather than silently returning defaults. Reasoning: silent defaults on bad data is worse than an explicit failure for a boot-time config loader. Added to Phase 3 (Task 3.7) with a regression test confirming the new raise behaviour. |

## Final bundle definition

**1 project, 27 actionable items**, 3 phases:
- Phase 1 (Critical): 1 item — B-5 UI error boundary + regression test
- Phase 2 (Major): 14 items — broad-except hygiene (8), JSON bypass (1), generic-raise (1), cross-layer wrappers (3), silent-swallow fix (1)
- Phase 3 (Minor): 12 items — broad-except hygiene (1 comment-format + 1 over-broad tuple = 2), JSON bypass (4), generic-raise (1), error-chaining (1), context enrichment (3), image parity (1)

Excluded:
- ERR-03-005 (REJECTED) — not in any project; logged in `verification_report.md` § Rejected.
- B-8 (OUT_OF_SCOPE — caller responsibility) and LLM-2 (OUT_OF_SCOPE — no actual leak) — not in any project; logged in `verification_report.md` § Out of Scope.

## Phase D Step 4 — final confirmation

User accepted the locked bundle table.
