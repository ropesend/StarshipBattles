# PROJ-479: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-22 | Project initialized | Starting point for Test review P1 brittle-bloated remediation 2026-05-20 |
| 2026-05-22 | Acted only on findings that passed independent verification of `2026-05-20_210550_test-review` (P1 tier) | OpenCode test-review confirms 94% of Phase-1 claims; a third skeptical pass with a different model catches blind spots the OpenCode verifier may share with its Phase-1 reviewer. P1 tier verification: 95 verified, 11 needs-rework, 8 rejected, 0 out-of-scope; rejected and out-of-scope items recorded in `findings/verification_report.md` |
| 2026-05-22 | DUP-004 REJECTED (do not consolidate ShipInstance serializer files) | The 3 cited files serve different contract layers (HP roundtrip via `to_ship`/`update_from_ship`, dict schema via `to_dict`/`from_dict`, and a separate ShipInstanceSerializer adapter). Forcing consolidation would obscure intent and couple unrelated tests |
| 2026-05-22 | DUP-003 + DUP-006 narrowed scope vs original cross-shard claim | Verification re-read cited files: DUP-003 IO vs entity layers serve different purposes (full consolidation loses tmp_path scope); DUP-006 stub classes are real in builder/UI only, not the propulsion test that was tangentially cited |
| 2026-05-22 | CAT-5 fixture-mutability rejections preserved | 8 CAT-5 fixture-scope rescoping claims were rejected during verification because MagicMock accumulates `call_args_list`/`call_count`, `seeded_rng` is stateful PRNG, density maps mutate, and damage_calculator factory fixtures must stay function-scoped for test isolation. Function scope is correct for mutable fixtures regardless of construction cost |
| 2026-05-22 | NEEDS_REWORK fixture rescopes (S02-F005, S05-F002, S06-F015, S08-F003, S10-F005, S11-F005, S13-F007, S16-F012) entered the plan with adjusted scope | Original suggestions were too broad (e.g., session-scope unsafe); verified suggestions narrow to module-scope or split mutable/immutable fixtures |
| 2026-05-22 | Conftest/fixture extraction targets fixed up-front | DUP-001 → `tests/conftest.py:_make_mock_fleet`; DUP-002 → `tests/fixtures/battle_panels.py` (new); DUP-005 → `tests/unit/strategy/engine/conftest.py`; HLP-001/005 → `tests/unit/strategy/save_game_service/conftest.py`; HLP-002 → `tests/fixtures/colonization_fixtures.py` (new); HLP-003/004 → `tests/conftest.py`; HLP-006 → `tests/unit/strategy/engine/conftest.py`. Established hierarchy keeps fixtures scoped to the smallest sensible directory |
