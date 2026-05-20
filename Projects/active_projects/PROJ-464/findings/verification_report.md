# Verification Report — PROJ-464 (presentation)

- **Source audit:** `Reviews/results/2026-05-19_223900_type-audit/`
- **Run date:** 2026-05-19 (independent third pass by Claude against live source)
- **Batch summary (whole audit):** 51 verified / 1 rejected / 2 uncertain (resolved) / 0 out-of-scope, out of a 53-item normalized candidate set drawn from ~250 audit findings.

This report covers the presentation bundle. The Rejected and Uncertain sections are the audit-wide results (identical narrative across siblings); the Verified table is presentation-specific.

## Verified (this bundle)

| id | file | symbol | current | suggested |
|----|------|--------|---------|-----------|
| TYP-SS | game/ui/screens/strategy_screen.py (15 props) | StrategyScreen.galaxy/empires/systems/... | `-> Any` | Galaxy/list[Empire]/list[StarSystem]/StrategySessionFacade/GameSession |
| TYP-SR | game/ui/screens/strategy_renderer.py:115-157 (13 props) | StrategyRenderer scene delegates | `-> Any` | renderer-scene Protocol (NOT StrategyScreen) — see Uncertain |
| TYP-BSCREEN | game/ui/screens/battle_screen.py:172,199,207,211,215,219,481,485 | BattleScreen delegates | `-> Any` | BattleEngine\|None/bool/int/list[Ship]/list[Projectile]/int\|None |
| TYP-PLF | game/ui/screens/planet_list_filters.py:38,174,215,252,280,333,348 | 7 filter fns | `-> Any` | list[PlanetInfo]/str/dict[str,tuple] |
| TYP-SLF | game/ui/screens/star_list_filters.py:20,67,121,163,203,217 | 6 filter fns | `-> Any` | list[StarInfo]/... |
| TYP-BUILDERVM | builder/left_panel:453, modifier_logic:150, weapons_viewmodel:110,392 | get_add_count/calculate_snap_value/hovered_weapon/calc_damage_at_range | `-> Any` | int/float/Component\|None/float |
| TYP-COLMGR | game/ui/components/table/column_manager.py:79,137 | toggle_column/is_column_visible | `-> Any` (dict[str,Any].get) | Optional[bool]/bool |
| TYP-IGN-STM | game/ui/assets/ship_theme_manager.py:254 | expected[0],expected[1] | `# type: ignore[index]` | type as tuple[int,int]\|None |
| TYP-IGN-RTG | game/ui/panels/race_theme_gallery.py:118 | _discover_assets override | `# type: ignore[override]` (genuine mismatch) | fix override return-type shape |
| TYP-RBOOT | game/app_bootstrap.py:310 | _replay_combat_lab_fallback | no return annotation | `-> Ship` (sev downgraded CRITICAL→MAJOR by audit verifier) |
| TYP-MISC-MR (UI part) | atmosphere_target_editor:223, radiation_shield_editor:176, water_target_editor:173, test_lab/details/validation:39, transfer_mass_preview:189 | _button_handlers/_phase_color/_get_catalog | no return annotation | per audit |
| TYP-TUPLE | game/ui/pygame_gui_patch.py:90 | _to_tuple | no return annotation | `-> tuple \| None` (sev downgraded CRITICAL→MINOR by audit verifier) |
| TYP-UIMINOR | builder/stat_getters.py (~40 fns), stat_rows_dynamic.py:36-557 (23 fns) | UI display getters/formatters | `-> Any` | str\|float\|int / dict[str,Any] |
| TYP-PIMPL2 (UI part) | profiling.py:90, resources.py:85, ui/renderer/sprites.py:33 | implicit Optional params | `Type = None` | `Type \| None = None` |
| STRICT-unknown | top-level (app.py/run_loop/screen_router) | — (layer) | est. ~16 errors | adopt `--strict` (scene proxies stay Any) |
| STRICT-ui | game/ui/ | — (layer) | est. ~1,084 errors | adopt `--strict` (pygame_gui mostly external) |

Note on strict-migration counts: per-layer numbers are audit estimates (its scanner attributed by path; `mypy <path>` follows imports). Aggregate re-run: 2,269 errors / 325 files, consistent with the audit's 2,108 real errors. Confirm per-layer counts at task start. No layer is at zero.

(`TYP-MISC-MR` and `TYP-PIMPL2` are multi-layer findings; only their UI/top-level sites are in this bundle. `profiling.py`/`resources.py` are core files but their implicit-Optional sites were flagged in Shard 03's UI context and are grouped here for continuity; the only foundation-bundle implicit-Optional site is `json_utils.py:56`.)

## Rejected (audit-wide)

| id | original audit recommendation | contrary evidence | rationale |
|----|-------------------------------|-------------------|-----------|
| TYP-APP | Narrow `game/app.py:198-233` Game scene accessor properties from `-> Any` to `-> IScene` | `game/app.py:173-188` (`_route_get`/`_route_set`); Shard 04 minor#5; `tests/unit/test_app_delegators.py`, `tests/unit/test_run_loop.py` assign loose `object()`/MagicMock scenes | Scene proxies are intentionally loose so `Game.__new__(Game)` tests assign attributes directly; narrowing to IScene breaks those mocks. A separate test-surface hardening question, not clean audit residue. Codex concurred. |

## Uncertain (resolved)

| id | verifier question | decision |
|----|-------------------|----------|
| TYP-COREPROTO | Some core protocol Any narrowable; position/location seams must stay Any | **INCLUDE (PROJ-462)** with boundary-preserving carve-out. Not in this bundle. |
| TYP-SR | StrategyRenderer 13 props: cross-layer report says narrowable; Shard 04 says acceptable; tests use MagicMock scenes | **INCLUDE (this bundle)** framed as a minimal renderer-scene Protocol seam (Phase 1.2). Phase 1.2 explicitly forbids hard-narrowing to `StrategyScreen` to keep the MagicMock-scene tests (`tests/unit/ui/screens/test_strategy_renderer.py`) passing. |

## Out of Scope

None promoted. Justified ignores (e.g. `pygame_gui_patch.py:152` monkeypatch attr, `ship_detail_panel.py` PROJ-315 dynamic attrs, `defeat_dialog`/`turn_failed_dialog` bypass-init) were already excluded by the audit's `findings/verification.md` and never entered the candidate set.
