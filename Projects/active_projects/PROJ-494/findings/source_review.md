# PROJ-494: Source Review

## Origin

This project carries over the **UI-family** subset of PROJ-480's deferred backlog.

- Source review: `Reviews/results/2026-05-20_210550_test-review/` (P2 test review, 2026-05-20)
- Source project: `Projects/active_projects/PROJ-480/` (stalled at ~36/138 tasks, mid-Phase-1 stop per protocol 03a §3)
- Structure consult (locality-first split): `AgentCoordination/Scratchpad/Consult/20260523T125719Z_plan-PROJ-480-followthrough/response.md`

## How the backlog was partitioned

Codex's recommendation (verbatim, response.md F1):

> Recommendation: split by locality first, then by risk:
> - PROJ-494: UI-family ownership. All `tests/unit/ui/**`, `tests/unit/ui/screens/**`, `tests/unit/ui/panels/**`, `tests/repro_issues/test_bug_04_display.py`, `tests/unit/research/test_research_renderer.py`, plus moved UI/integration files...
> - PROJ-495: core unit mechanical ownership. Non-UI CAT-8/9/10 cleanup under `tests/unit/strategy/**`, `tests/unit/simulation/**`, `tests/unit/ai/**`, `tests/unit/modifiers/**`, `tests/regression/**`, excluding the risky guard/introspection/integration files.
> - PROJ-496: risky core + non-UI integration ownership.

This file lists the **UI-family** slice. Cross-reference `manifest.md` for the full mapping of PROJ-480 task IDs → files in this project.

## PROJ-480 Phase-by-phase contribution

| PROJ-480 phase | PROJ-480 task IDs landing in PROJ-494 |
|---|---|
| Phase 1 (CAT-9) | 1.5, 1.11, 1.14 (1.3 dropped — already done; 1.15/1.17 skipped per plan) |
| Phase 2 (CAT-8) | 2.3, 2.4, 2.6, 2.7, 2.9, 2.10, 2.13, 2.14, 2.15, 2.16, 2.17, 2.18, 2.19, 2.20, 2.21, 2.22, 2.28, 2.30 |
| Phase 3 (CAT-10) | 3.1, 3.2, 3.12, 3.13, 3.14, 3.15, 3.16, 3.19, 3.21, 3.22, 3.23, 3.26, 3.30, 3.36, 3.37, 3.38, 3.41, 3.45 |
| Phase 4 (CAT-11) | 4.5, 4.6, 4.7, 4.8, 4.9 |
| Phase 5 (CAT-12) | 5.3, 5.6, 5.7, 5.16 |

Total: ~46 actionable tasks across 4 phases (Phase 0 retarget/prune + 4 execution phases).

## Source-review categories covered

- CAT-8 Needless Complexity
- CAT-9 Simplification
- CAT-10 Parametrize
- CAT-11 Fragile Assertion
- CAT-12 Logic-Heavy

## Verification protocol

Phase 0 must re-grep every task's target pattern before TDD work begins. PROJ-480 stalled in part because the original line refs degraded across PROJ-478/479/487/488/489 file moves. Every file path here was re-verified against the live tree on 2026-05-23, but **line numbers were not** — they are still advisory.
