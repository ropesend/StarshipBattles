# PROJ-480 — Verification Report (P2 tier)

**Source review:** `Reviews/results/2026-05-20_210550_test-review/`
**Run date:** 2026-05-20
**Priority tier:** P2 (CAT-8 Needless Complexity, CAT-9 Simplification, CAT-10 Parametrize, CAT-11 Fragile Assertion, CAT-12 Logic-Heavy)
**Batch summary:** 145 verified / 4 needs-rework / 4 rejected / 32 out-of-scope out of 185 OpenCode CONFIRMED candidates for this tier.

The per-shard re-verification reports under `.agent_reports/2026-05-20_210550_test-review/` (15 files) capture every CAT-8/9/10/11/12 verdict; the tables below summarize the P2 subset.

## Verified

Full per-shard tables are in the per-shard re-verification reports. The high-volume categories:

| Category | Verified | Tasks in this project |
|----------|----------|------------------------|
| CAT-9 Simplification | 22 | Phase 1 (28 tasks; some retained for traceability) |
| CAT-8 Needless Complexity | 28 | Phase 2 (30 tasks; some retained for traceability) |
| CAT-10 Parametrize | 78 | Phase 3 (51 tasks; many tasks bundle multiple cluster sites within one file) |
| CAT-11 Fragile Assertion | 11 | Phase 4 (11 tasks) |
| CAT-12 Logic-Heavy | 18 | Phase 5 (18 tasks; some marked "no action" for already-acceptable patterns) |

All verified P2 items are detailed in:
- `.agent_reports/2026-05-20_210550_test-review/verification_w1_s01.md` through `verification_w6_s16.md` (16 files)

## Needs Rework

| id | original suggestion | Claude's adjusted suggestion | rationale |
|----|---------------------|------------------------------|-----------|
| S02-F005 | Parametrize 6 ability tests (CAT-9 → CAT-10) | Keep separate; document semantic distinctness | Each test exercises a distinct ability class through unique production path |
| S03-F006 | Suggested CAT-8 nesting "5 patches + patch.object" | Actual is 4 patches; downgrade or describe accurately | Real nesting count differs from claim |
| S06-F005 | Parametrize 15 superweapon tests | Reject parametrization; document per-weapon class structure as deliberate | Per-weapon Order structures + Stellerate's fleet-consumption assertion differ |
| S16-F011 | Severity MAJOR CAT-8 (7-patch constructor) | Downgrade severity to MINOR; use `patch.multiple` | Patch count reflects constructor's DI count, not test design flaw |

## Rejected

Each row is a potential bug in the test-review skill — kept scannable so it can feed back later.

| id | original claim | contrary evidence (file:line) | rationale |
|----|----------------|--------------------------------|-----------|
| S13-F012 | test_targeting_system.py:1141 CAT-6 MAJOR call_args | File is 1110 lines; line 1141 doesn't exist | Cited line doesn't exist; appears copy-paste from test_weapon_firing_system.py:804 |
| S13-F013 | test_targeting_system.py CAT-9 30+ duplicate patterns | File already uses shared helpers (_make_ship_mock, _make_pdc_weapon, _make_candidate); confidence low | Insufficient evidence; would need full-file audit to validate 30+ claim |
| S14-F005 | test_naming.py:246-251 CAT-12 logic-heavy 5-line loop | 5-line enumerate-with-inline-assert is straightforward, not logic-heavy | Below the bar for CAT-12 |
| S14-F011 | test_isolation.py CAT-5 ordering dependency | `reset_game_state` autouse fixture ensures clean state | Tests pass in any order; docstring misleading not test buggy |

## Out of Scope

| id | claim | reason for not acting |
|----|-------|------------------------|
| S01-F014 | test_workshop_screen.py:185-191 — conftest helper self-test | `conftest_advisory` — helper validation not SUT test |
| S03-F011 | test_system_selection_window.py:239-283 — __new__ bypass | `intentional_smoke_test` (PROJ-347 Pattern §33 convention) |
| S03-F021 | test_planet_list_window.py:33-66 — __new__ bypass | `intentional_smoke_test` (PROJ-322 file-header comment) |
| S07-F007 | test_decorators.py:135-145 — sleep for profile_block measurement | `deliberate_latency_simulation` |
| S10-F002 / F003 / F004 | conftest files flagged CAT-3 with no test fns | `conftest_advisory` per SUMMARY caveat #5 |
| S10-F020 / F021 | test_no_carried_items_proxy.py / test_no_commands_specs_module.py — file-existence guards | `ast_guard_intentional` (PROJ-436 Phase 9, PROJ-371 Phase 2) |
| S12-F009 / S12-F016 | constants validation and deletion guards | already correctly excluded by rubric |
| S13-F025 | test_hit_effects.py — 3 early-return tests | Test names document branches; serve discovery purpose; keep |
| S14-F003 | test_galaxy_test_screen.py — constants validation isinstance | already-downgraded per rubric exemption |
| S14-F020 | test_boundary.py — protocol-conformance check | `intentional_smoke_test` — already-parametrized, well-suited |
| S16-F001 / F002 / F003 | conftest fixture-only files flagged CAT-3 | `conftest_advisory` |
| Plus: 19+ other items marked OUT_OF_SCOPE in per-shard reports for `conftest_advisory`, `ast_guard_intentional`, or `intentional_smoke_test` reasons | | See per-shard verification files |
