# PROJ-281 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `tests/fixtures/battle.py` | Test fixture | **Modified (Phase 1 + 2.1).** Added `make_minimal_spec(ships_by_team, *, seed, max_ticks, telemetry_level) -> BattleSpec` + `start_battle_screen_with_minimal_spec(screen, ships_by_team, *, headless, start_paused, seed, max_ticks) -> BattleController`. Module docstring updated with PROJ-281 helper section. |
| `tests/fixtures/test_make_minimal_spec.py` | Test | **New (Phase 1 + 2.1).** 23 tests covering: shape invariants (6), instance_id format (2), defaults (5), overrides (3), ship pose (2), helper smoke (4). Organized into 6 classes. |
| `tests/integration/test_make_minimal_spec_smoke.py` | Test | **New (Phase 1).** 2 end-to-end tests: spec feeds `BattleController.start_from_spec`; spec feeds headless `run_battle(spec)`. |
| `tests/unit/ui/test_battle_screen.py` | Test | **Phase 2.2 target (NOT YET TOUCHED).** 7 legacy `scene.start([ship1], [ship2], ...)` callers at lines 57, 67, 83, 93, 117, 137, 149. |
| `tests/unit/ui/test_battle_screen_simulation.py` | Test | **Phase 2.3 target (NOT YET TOUCHED).** 37 legacy callers — bulk of the migration work. |
| `tests/unit/ui/screens/test_battle_setup_logic.py` | Test | **Phase 2.4 target (NOT YET TOUCHED).** 3 callers at lines 78, 100, 104. WARNING: tests query `scene.ships` / `scene.ai_controllers` directly — assertion reshaping required, not just call-site replacement. `test_battle_scene_clear_state` likely needs deletion (shim-specific contract). |
| `game/ui/screens/battle_screen.py` | Production | **Phase 3 target (NOT YET TOUCHED).** Delete `start(self, team0_ships, team1_ships, ...)` method at line 227. Delete `_build_fallback_outcome` (~90 LOC). |
| `tests/unit/simulation/test_unified_entry_guard.py` | Test | **Phase 3.4 target (NOT YET TOUCHED).** Guard test around line 565 documents the shim's retention — flip to enforce deletion after Phase 3. |
| `docs/systems/combat_simulation.md` | Docs | **Phase 4.1 target (NOT YET TOUCHED).** Remove references to the test-convenience shim and fallback outcome. |
| `combat_lab/COMBAT_LAB_DOCUMENTATION.md` | Docs | **Phase 4.2 target (NOT YET TOUCHED).** Check for shim mentions; update if found. |
| `tests/fixtures/README.md` | Docs | **Phase 4.3 target (CHECK EXISTENCE).** Add section documenting `make_minimal_spec` as the canonical test-writing helper. Create if doesn't exist. |
