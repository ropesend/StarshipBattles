# PROJ-484 — Audit verification (Codex consult 2026-05-23)

Source: `AgentCoordination/Scratchpad/Consult/20260523T053310Z_audit-PROJ-484/response.md`

| # | Codex finding | Verdict | Action |
|---|---------------|---------|--------|
| 1 | Scope alignment — code matches corrected scope; ship.py untouched | VERIFIED (positive) | No action; confirmation only |
| 2 | Regression: `CombatEvent.context: Optional[DamageContext]` at `game/simulation/combat/combat_events.py:78` has no in-scope binding after the import deletion at line 62. `typing.get_type_hints(CombatEvent)` raises `NameError`. | **VERIFIED + IN-SCOPE** | Remediate in new Phase 3 — restore `DamageContext` import via `TYPE_CHECKING` block (matches file's existing pattern at lines 28-30) and change annotation to forward-ref string `Optional["DamageContext"]` |
| 3 | `_null_provider` deletion clean; no orphan registration | VERIFIED (positive) | No action |
| 4 | No surviving callers via deleted paths (greps clean) | VERIFIED (positive) | No action |
| 5 | No test deleted that should have been rewritten | VERIFIED (positive) | No action |
| 6 | LEG-A-01 and LEG-A-02 rejection rationales accurate | VERIFIED (positive) | No action; confirms scope correction |

## Risks codex raised

- `allow_tests=false` means codex did not run focused tests. The annotation regression survived sub-agent test-pass because the targeted tests don't call `typing.get_type_hints(CombatEvent)`. Phase 3 remediation should add a one-line guard test that calls `get_type_hints` and asserts it does not raise.

## Decision

One in-scope remediation finding. Proceeding to Phase 3 per protocol Step D.
