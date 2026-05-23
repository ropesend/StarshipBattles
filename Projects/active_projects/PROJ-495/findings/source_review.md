# PROJ-495: Source Review

## Origin

This project carries over the **core mechanical** (non-UI, non-risky) subset of PROJ-480's deferred backlog.

- Source review: `Reviews/results/2026-05-20_210550_test-review/` (P2 test review, 2026-05-20)
- Source project: `Projects/active_projects/PROJ-480/` (stalled at ~36/138 tasks)
- Structure consult (locality-first split): `AgentCoordination/Scratchpad/Consult/20260523T125719Z_plan-PROJ-480-followthrough/response.md`

## How the backlog was partitioned

See `Projects/active_projects/PROJ-494/findings/source_review.md` for the full Codex recommendation. PROJ-495 owns:

> core unit mechanical ownership. Non-UI CAT-8/9/10 cleanup under `tests/unit/strategy/**`, `tests/unit/simulation/**`, `tests/unit/ai/**`, `tests/unit/modifiers/**`, `tests/regression/**`, excluding the risky guard/introspection/integration files

## PROJ-480 Phase-by-phase contribution

| PROJ-480 phase | PROJ-480 task IDs landing in PROJ-495 |
|---|---|
| Phase 1 (CAT-9) | 1.16, 1.21 (1.7 lives in PROJ-494's integration scope since the file moved to `tests/integration/ui/`) |
| Phase 2 (CAT-8) | 2.5, 2.8, 2.11, 2.12, 2.23, 2.29 |
| Phase 3 (CAT-10) | 3.3, 3.6, 3.7, 3.8, 3.9, 3.11, 3.17, 3.18, 3.24, 3.25, 3.27, 3.28, 3.35, 3.39, 3.42, 3.44, 3.46, 3.47, 3.48, 3.49 |
| Phase 4 (CAT-11) | 4.3 |
| Phase 5 (CAT-12) | 5.1, 5.2, 5.15 |

Total: ~32 actionable tasks across 4 execution phases.

## Source-review categories covered

- CAT-8 Needless Complexity
- CAT-9 Simplification
- CAT-10 Parametrize (the bulk — 20 tasks)
- CAT-11 Fragile Assertion
- CAT-12 Logic-Heavy

## Note on T1.7 routing

PROJ-480's Task 1.7 (`MockPlanetType` 8 inline defs) targeted `tests/unit/strategy/services/test_colonization_facade.py`. The file has since moved to `tests/integration/ui/test_colonization_facade.py` (verified 2026-05-23). Codex spot-check confirmed the inline enums are still there at `:71, :380, :441, :494, :583, :642, :697, :751, :819`. Because the file is now integration-shaped, it could plausibly live in PROJ-494 (integration/ui is in PROJ-494's scope) or PROJ-496 (non-UI integration). Decision: route to **PROJ-494** since the path is `tests/integration/ui/**`. If PROJ-494 finds it doesn't fit (no UI interaction in the test bodies), move to PROJ-496 in that project's Phase 0.

## Verification protocol

Phase 0 must re-grep every task's target pattern before TDD work begins. Every file path here was re-verified against the live tree on 2026-05-23, but **line numbers were not** — they are still advisory.
