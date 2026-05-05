# PROJ-344 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-336/decisions.md` | Doc (update) | T2.1 — D-008 rewrite to match `fleet_cargo_projector.py:54-61` |
| `Projects/active_projects/PROJ-327/decisions.md` | Doc (update) | T2.2 — annotate `-3.9s` claim at line 31 with `(retracted per audit S2.7)` |
| `Projects/active_projects/PROJ-327/runtime_delta.md` | Doc (update) | T2.2 — annotate lines 37, 41 |
| `Projects/active_projects/PROJ-327/phase_5_checklist.md` | Doc (update) | T2.2 — annotate lines 27, 44, 56, 83 |
| `Projects/active_projects/PROJ-327/phase_1_checklist.md` | Doc (update) | T2.2 — annotate line 92 |
| `Projects/active_projects/PROJ-327/virtual_table_runtime.md` | Doc (update) | T2.2 — annotate lines 25, 38 |
| `docs/known-issues.md` | Doc (update) | T2.2 — annotate lines 128, 132 (USER-FACING — high priority) |
| `Projects/active_projects/PROJ-332/design.md` | Doc (update) | T2.3 — `harvest` → `harvesting` at lines 69-72 |
| `Projects/active_projects/PROJ-332/phase_1_checklist.md` | Doc (update) | T2.3 — `harvest` → `harvesting` at line 31 |
| `tests/unit/ui/screens/test_strategy_screen_composition.py` (or wherever) | Test (update + add) | T2.4 — fix docstring; add 2 tests (same-screen reuse passes, different-screen reuse raises) |
| `Projects/active_projects/PROJ-329A/findings/concurrent_commit_audit.md` | Doc (update) | T2.5 — add 2 new contaminated commits (`ddfec64e0`, `9d16524f1`); verify each via `git show --stat <sha>` first |
| `tests/unit/strategy/services/test_strategy_session_facade_contract.py` | Test (verify; possibly extend) | T2.6 — diff method-surface coverage vs PROJ-321 deleted `TestPublicMethodSurface`; restore invariant test if gap |
| `Projects/active_projects/PROJ-344/plan.md` | Project artifact | Updated as phases progress |
| `Projects/projects_index.md` | Project index | Status update at end of Phase 1 |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 | `pytest tests/unit/strategy/services/ tests/unit/ui/screens/test_strategy_screen_composition.py -x -q` then `python Tools/lint_test_files.py` |
