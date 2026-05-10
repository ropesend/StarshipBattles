# Review Scope: PROJ-392 — Misc orphan wrappers + zero-callsite placeholders

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260509_030941_2fd173
**Review Mode:** normal (not lightweight)
**No Coverage block present** — standard review, not 03c-phase-aware.

**Scope:**
Project directory: `Projects/active_projects/PROJ-392/` (verification_report has Implementation-Time Corrections section)

4 commits on `feat/03c-phase-aware-execution`: `21ab2bdc0`, `51b216bf9`, `19d929385`, `bd0d150ee`.

12 legacy-items cleaned up (9 verified + 1 uncertain-resolved + 2 INFO-resolved) plus 7 audit-corrections made during implementation.

Production files (~12): `game/simulation/entities/{ship_stats.py, stat_contributors/{command,registry}.py}`, `game/ui/screens/{race_setup/screen.py, strategy_renderer.py, empire_build_queue_window.py, builder/{stat_getters,stats_config}.py, new_game_setup_screen.py, new_game_setup_controller.py, strategy_screen_assets.py}`, `game/ui/panels/battle_panels.py`, `game/strategy/{quickstart_builder.py, services/galaxy_pathfinding_service.py, data/pathfinding.py}`, `game/app.py`, `game/assets/asset_manager.py`, `docs/04_SERVICES.md`

Tests (~13 files) updated for migrated patch targets and renamed APIs.

**Instructions:**
Quick verification of a 12-task catch-all cleanup:
1. Final grep for each of the 12 deleted/renamed symbols. Confirm zero remaining production references.
2. Verify dispatch-registry-key retention (LEG-03-016) — config value, not code shim.
3. Spot-check audit-vs-actual call-site corrections for semantic correctness.
4. Verify `_menu_scene` → `menu_scene` rename completeness.
5. Verify `get_asset_manager` → `get_default_asset_manager` migration.
6. Verify `_get_total_crew_requirement` rename and dispatch registry.
7. Verify `new_game_setup_screen` static-wrapper deletion and controller indirection cleanup.
8. Rule 3 compliance — no replacement shim anywhere.

**Context:**
Last of 11 sequential PROJ runs. Stage 3 closeout. Catch-all bundle for misc legacy items.
7 audit underestimates handled in-stride. Final sharded suite: 19729/19740 (all failures pre-existing and confirmed unrelated).
