# Review Scope: Skeptical audit of PROJ-321/322/323/324 as-shipped state

**Type:** consistency (delegated by Claude Code)
**Request ID:** req_20260504_132454_ba99d6

## Scope
**Language:** en
**Review Mode:** full

Four completed projects — skeptical audit for missed deletions, unresolved deferrals, false-positive checkmarks, bypass_init placement bugs, factory robustness gaps, LLMBackgroundCall edge cases, and documentation drift.

## Instructions (abbreviated)
1. PROJ-321: Were deletions over-aggressive? Spot-check 3-5.
2. PROJ-322: Walk all 25 deferrals — verify each cited resolution/disposition.
3. PROJ-323: Verify CRIT-001 fix + check for OTHER false-positive checkmarks.
4. PROJ-324: Examine bypass_init guard placement in StrategyModalWindow, RaceSetupScreen, NewGameSetupScreen. Compare against §33 claims.
5. make_ui_widget factory robustness: edge cases (no bypass_init, conflicting kwargs, *args).
6. LLMBackgroundCall _done_event.set() placement — outside _state_lock? Any path where event might NOT get set?
7. Documentation drift: §33 accuracy, known-issues.md RESOLVED claims.

Be skeptical — assume bugs until proven otherwise.

## Context
Part of a 7-reviewer skeptical audit of PROJ-321 through PROJ-328. Three OpenCode reviews + 4 Claude Explore subagents auditing in parallel.

## Prior Reviews
- PROJ-321 review: Reviews/results/2026-05-04_015902_*proj-321*/report.md
- PROJ-322 review: Reviews/results/2026-05-04_015938_*proj-322*/report.md
- PROJ-323 review: Reviews/results/2026-05-04_020005_*proj-323*/report.md
