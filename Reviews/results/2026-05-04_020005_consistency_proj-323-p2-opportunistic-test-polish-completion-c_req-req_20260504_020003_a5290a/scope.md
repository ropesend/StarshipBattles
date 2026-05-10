# Review Scope: PROJ-323 Completion + Continuation Review

**Type:** consistency (delegated by Claude Code)
**Request ID:** req_20260504_020003_a5290a
**Scope:** PROJ-323 P2 opportunistic test polish — all 5 phases, 149/149 tasks complete, 1 documented deferral (Task 3.34). 41 of 159 source items obsoleted by upstream PROJ-321 deletions. Net delta: ~-1,418 LOC.

**Instructions:**
1. Quality of parametrize sweeps (CAT-10, Phase 3). Spot-check 4-5 consolidations for discoverability and per-case error messages.
2. CAT-12 reference-value pattern. Check `test_projectile_manager.py` (deleted) and other CAT-12 tasks — docstring presence, brittleness.
3. CAT-11 fragile-assertion replacements (Phase 4). Did semantic comparisons preserve regression signal? Focus on Task 4.2 soft assertions.
4. Task 3.34 deferral. 11-handler `fleet_not_found` cluster — valid rationale or avoidance?
5. ≥3-member parametrize threshold rule. Audit 3.15, 3.27, 3.37 — correctly left or worth parametrizing?
6. Below-the-line items. 1 rejected, 6 out-of-scope — confirm rejections are sound.
7. Continuation work. Lowest-value-but-worth-doing follow-up in P2 territory.

**Context:** Part of 3-project chain review (PROJ-321/322/323). PROJ-323 is the largest by item count (159) but lowest priority (P2 polish).
