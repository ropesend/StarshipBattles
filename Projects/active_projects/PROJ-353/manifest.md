# PROJ-353 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-353/decisions.md` | Project artifact | T6.8 decision logged + Tier-7 per-concern observations |
| `tests/unit/strategy/facade/test_strategy_session_facade_session_isolation.py` (or extend existing) | Test (NEW or extend) | T6.8 — optional regression trap asserting `_session` is not in `dir()` of facade public surface |
| `game/services/llm/background.py` | Production (refactor) | Tier-7 — fix `_done_event` race (lines 210, 291-297); set event after `_active_workers` cleanup |
| `tests/unit/strategy/engine/test_production_spawner.py` | Test (tighten) | Tier-7 — `assert_called_once` → `assert_called_once_with(...)` |
| `tests/unit/strategy/turn_engine/test_*team_modifiers*.py` (locate) | Test (rewrite) | Tier-7 — replace brittle import patch |
| `tests/unit/...` (multiple) | Test (annotate) | Tier-7 — dead-branch pin annotations on `_apply_damage_to_ship` etc. |
| `tests/unit/strategy/turn_engine/` | Test (add) | Tier-7 — PROJ-332 5 lazy-property defaults + `create_default_turn_engine` factory tests |
| `tests/unit/strategy/data/` | Test (add) | Tier-7 — PROJ-335 4 from_dict edge-case tests |
| `tests/unit/strategy/services/` (locate) | Test (rewrite or delete) | Tier-7 — PROJ-336 vacuous module-constant tests |
| `tests/unit/...` (locate via grep) | Test (extend) | Tier-7 — `test_get_font_enforces_minimum_size_8` quantize-to-2 |
| `Tools/lint_test_files.py` | Tool (possible update) | Tier-7 PROJ-326 — allowlist header lie, Python version comment |
| `tests/unit/...` (recover from history) | Test (NEW) | Tier-7 PROJ-321 — recover and rewrite `test_start_battle_ship_builder_calls_to_ship_with_position_and_team_id` |
| `tests/unit/...` (locate) | Test (rewrite) | Tier-7 — `TestRegisterOnConstruction` actually-test-registration |
| `tests/fixtures/ui_widget_factory.py` (or wherever `bypass_init` lives) | Tool (refactor) | Tier-7 — MRO leak under pytest-xdist; isolate per worker or document |
| `Projects/projects_index.md` | Project index | Status update at end of Phase 2 |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 (T6.8) | `pytest tests/unit/strategy/facade/ -x -q` |
| 2 (Tier-7) | `pytest tests/unit/ -q -p no:cacheprovider` after each commit |
| Final | `python Tools/lint_test_files.py` then user verification |
