# PROJ-490 — Audit verification (Codex consult 2026-05-23)

Source: `AgentCoordination/Scratchpad/Consult/20260523T124002Z_audit-PROJ-490/response.md`

| # | Codex finding | Verdict | Action |
|---|---------------|---------|--------|
| 1 | No executable lines changed in any of the 7 file diffs — all edits comment/docstring only | VERIFIED (positive) | No action |
| 2 | LEG-02-002 not fully closed: comment in `mine_group_service.py:128-130` was tightened but the plan's request for "dated TODO + PROJ reference" was not satisfied. Codex also notes the new "older test stubs" wording is imprecise — mine-group-self-destruct tests in `tests/unit/strategy/services/test_mine_group_service.py:83-116` and `tests/integration/test_fms_b_e2e.py:246-260` already use `deployed_groups`, not `fleets`. | **VERIFIED + IN-SCOPE** | Remediate in Phase 2: add a dated TODO. Reword the rationale to be precise (the fallback covers empire-shaped stubs that don't expose `deployed_groups`, not "older test stubs that haven't migrated"). |
| 3 | No important historical info lost — ship_instance.py still has the canonical PROJ-436 / bay_inventory narrative at lines 78-80, 126-127, 767-770 | VERIFIED (positive) | No action |
| 4 | No new docstring or convention regressions | VERIFIED (positive) | No action |
| 5 | No layer/path-convention violation (comment-only edits) | VERIFIED (positive) | No action |

## Decision

One in-scope remediation: tighten the `mine_group_service.py:128-130` comment to (a) add a dated note + follow-up tracking, and (b) reword the rationale to match what the code actually does. Phase 2.
