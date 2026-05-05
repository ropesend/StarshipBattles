# PROJ-353: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Starting point for Closeout follow-up - Tooling and test-quality polish (T6.8 facade _session lint + Tier-7 polish bundle) |
| 2026-05-04 | T6.8: Keep `facade._session` enforcement convention-only — no lint rule added. | Confirmed current state via `git grep -nE "facade\._session|\.facade\._session" game/ tests/`: zero production violations; only three references in `tests/integration/strategy/facade/test_facade_init.py:17`, `tests/unit/strategy/facade/test_strategy_session_facade_contract.py:110,114` which are legitimate test-internal access (one asserts identity, two patch the inner session for behaviour pinning). The Python single-leading-underscore convention is already understood across the codebase; adding a lint rule would generate false positives on internal facade modules and on these legitimate contract/init tests, while delivering only marginal protection. Per Codex consensus (`proj343_349_remaining_plan_r003.md`) the rule is added only if an external-access regression actually appears. Sub-task 1.3 (regression-trap test) skipped: not cheap enough — would either re-implement a grep in test form or duplicate the lint logic we just declined to add. |

## Observations (recorded mid-task; NOT auto-fixed per Phase 2 discipline)

