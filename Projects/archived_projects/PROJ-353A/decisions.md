# PROJ-353A: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Starting point for Closeout follow-up - Tooling and test-quality polish (T6.8 facade _session lint + Tier-7 polish bundle) |
| 2026-05-04 | T6.8: Keep `facade._session` enforcement convention-only — no lint rule added. | Confirmed current state via `git grep -nE "facade\._session|\.facade\._session" game/ tests/`: zero production violations; only three references in `tests/integration/strategy/facade/test_facade_init.py:17`, `tests/unit/strategy/facade/test_strategy_session_facade_contract.py:110,114` which are legitimate test-internal access (one asserts identity, two patch the inner session for behaviour pinning). The Python single-leading-underscore convention is already understood across the codebase; adding a lint rule would generate false positives on internal facade modules and on these legitimate contract/init tests, while delivering only marginal protection. Per Codex consensus (`proj343_349_remaining_plan_r003.md`) the rule is added only if an external-access regression actually appears. Sub-task 1.3 (regression-trap test) skipped: not cheap enough — would either re-implement a grep in test form or duplicate the lint logic we just declined to add. |

| 2026-05-05 | Codex audit (discussion 20260505T034007Z) found 2 MAJORs + 1 nit; remediated in commits 2ac1b2c8d, 7c7e4cece, 7a8f07a61, 04b2aee2f | R1: `LLMBackgroundCall.start()` was sequentially idempotent but not concurrently idempotent — pre-fix two threads racing into start() on the same instance could both pass the `_thread is None` guard before either reserved a slot. Fix: collapse guard + reservation + assignment under a single `_state_lock` block; new deterministic two-thread test using a `_GatedLock` wrapper + `threading.Barrier(2)` pins the contract. R2 coverage: new `tests/unit/ui/screens/test_planet_abilities_controller_scanner.py` (14 tests) directly characterizes `scan_abilities`, `get_available_editors`, `should_show_food_editor`, and the humanization helper — PROJ-351A T6.4's data-driven scanner had no direct tests prior. R2 docs: `docs/systems/strategy_layer.md` and `docs/guides/adding_abilities.md` updated to reflect the deletion of `TOGGLEABLE_ABILITIES`, the data-driven scan via `activation_time`, and `ENVIRONMENT_EDITORS` documented as an intentional UI editor-routing list. R3: stale module-docstring claim removed from `test_planetary_facility_characterization.py:13`. Final unit suite: 15,797 pass / 1 known-flaky LLM-timing test (documented in MEMORY.md, Windows-specific `time.sleep` resolution flake, NOT this fix's regression) / 2 skip. |

## Observations (recorded mid-task; NOT auto-fixed per Phase 2 discipline)

