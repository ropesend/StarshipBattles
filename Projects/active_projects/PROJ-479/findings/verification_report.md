# PROJ-479 — Verification Report (P1 tier)

**Source review:** `Reviews/results/2026-05-20_210550_test-review/`
**Run date:** 2026-05-20
**Priority tier:** P1 (CAT-4 Duplicate Testing, CAT-5 Fixture Bloat, CAT-6 Mocking Brittleness, CAT-7 Sleep/Latency, DUP-001/002/003/005/006, HLP-001..006)
**Batch summary:** 95 verified / 11 needs-rework / 8 rejected / 0 out-of-scope out of 110 OpenCode CONFIRMED candidates + 11 cross-shard cluster definitions for this tier.

The per-shard re-verification reports under `.agent_reports/2026-05-20_210550_test-review/` (15 files) capture every CAT-4/5/6/7 verdict; the tables below extract the P1 subset that affects this project. See `verification_w6_cross_shard.md` for the cluster verdicts.

## Verified

Full per-shard tables are in the per-shard re-verification reports. The summary below lists the categories and high-impact items entering this project's plan. Sample of the largest items:

| id | category | severity | file | test_name | suggestion |
|----|----------|----------|------|-----------|------------|
| S07-F012 | CAT-9 ←→ CAT-10 | MINOR | tests/.../test_engine_validation.py | 12 near-identical engine validation classes | Parametrize handler classes (note: this item is CAT-9 — goes to P2) |
| S08-F004 | CAT-6 | MAJOR | tests/.../test_turn_engine_progress_callback.py | call_args_list exact tuple | assert_has_calls relaxed |
| S08-F006 | CAT-6 | MAJOR | tests/.../test_ship_detail_panel.py | 23 patch.object(__init__) tests | Accept w/ coupling comment per PROJ-211 |
| S07-F005 | CAT-6 | MAJOR | tests/.../test_event_log_window.py | _make_window no-op __init__ | bypass_init pattern |
| S04-F004 | CAT-6 | MAJOR | tests/.../test_strategy_input_handler_core.py | private _click_dispatch | public handle_click + observable |
| S07-F006 | CAT-6 | MAJOR | tests/.../test_superweapon_order_processor.py | SuperweaponValidator patch ×10 | DI stub validator |
| S07-F017 / S07-F018 / S07-F025 | CAT-5 | MAJOR | tests/integration/...* | pygame init per test, full quickstart filesystem | Module-scope |
| S02-F010 | CAT-5 | MAJOR | tests/.../test_theme_discovery.py | 9 autouse pygame.init classes | Class-scope |
| S02-F013 / S03-F008 | CAT-5 | MAJOR | tests/.../test_ai.py / test_combat.py | Function-scope Ship + components | Class-scope + deepcopy |
| DUP-001 / DUP-002 / DUP-005 / HLP-001..HLP-006 | cluster | — | (cross-shard) | Various local helper duplications | Extract to canonical conftest/fixture |

All other verified P1 items are detailed in:
- `.agent_reports/2026-05-20_210550_test-review/verification_w1_s01.md` through `verification_w6_s16.md` (16 files)
- `.agent_reports/2026-05-20_210550_test-review/verification_w6_cross_shard.md` (cluster verdicts)

## Needs Rework

| id | original suggestion | Claude's adjusted suggestion | rationale |
|----|---------------------|------------------------------|-----------|
| S03-F017 | Use real Fleet (CAT-6) | Use real Fleet + minimal GameSession; drop closure stubs | Adds explicit guidance on dropping `lambda add_order` + `_get_fleet_by_id` closures |
| S05-F002 | Delete legacy class (CAT-4) | Merge classes but verify Component.add_modifier's recalc path is tested at Component level | Legacy tests exercise `Component.recalculate_stats` as a side effect that stateful tests don't |
| S06-F005 | Parametrize (CAT-10) | Reject parametrization; document per-weapon classes as deliberate | Setup differs substantially per weapon; Stellerate uses different assertion path |
| S06-F015 | Session-scope (CAT-5) | Keep `seeded_rng` and `simple_density_map` function-scoped; only rescope confirmed-immutable primitives | Stateful PRNG + mutable density map make blanket rescope unsafe |
| S08-F003 | Rescope CAT-5 MAJOR | Downgrade severity to MINOR; rescope to module after confirming immutability | 9 fixtures verified read-only, but priority is lower than original tag suggested |
| S10-F005 | Session scope (CAT-5) | Rescope to `scope="module"` not session | Per-test importlib reload is wasteful but session scope risks cross-module bleed |
| S13-F007 | All fixtures read-only (CAT-5) | Function-scope only `mock_race_config_empty`; keep others function-scoped | Verification found mutations at lines 583-584, 681 |
| S15-C004 / HLP-005 | Identical 10-line pattern (HLP) | Unified fixture supporting both chdir + patch modes, not a 1:1 swap | test_auto_save uses `os.chdir` vs canonical's `patch(Paths.SAVES_DIR)` |
| DUP-003 | Full consolidation | Selective `_assert_roundtrip_property` helper for 4 overlapping fields; keep test files separate | IO layer (tmp_path) vs entity layer serve different scopes |
| DUP-006 | 5+ files across 3 shards | Narrow scope to builder/UI only (2-3 copies) | `test_propulsion_ability_bindings.py` uses inline `MockComponent`, not Modifier stubs |
| S16-F011 / S16-F012 / S16-F006 | MAJOR severity | Downgrade to MINOR | Verification re-read shows lower priority than original tag |

## Rejected

Each row is a potential bug in the test-review skill — kept scannable so it can feed back later.

| id | original claim | contrary evidence (file:line) | rationale |
|----|----------------|--------------------------------|-----------|
| S06-F011 | conflict_resolution/conftest.py CAT-5 MAJOR — session-scope MagicMock fixtures | MagicMock accumulates `call_args_list`/`call_count`/`called` | Session scope would leak state across tests |
| S06-F012 | armor_mechanics/conftest.py CAT-5 MAJOR — same | Mutable hp / current_shields fields persist | Same reason as F011 |
| S13-F012 | test_targeting_system.py:1141 CAT-6 MAJOR — call_args mock | File is only 1110 lines; line 1141 doesn't exist; grep call_args = 0 | Claim cites non-existent line; copy-paste error from test_weapon_firing_system.py:804 |
| S13-F013 | test_targeting_system.py CAT-9 — 30+ duplicate patterns | File already uses _make_ship_mock / _make_pdc_weapon / _make_candidate helpers | Insufficient evidence for the 30+ claim |
| S14-F005 | test_naming.py:246-251 CAT-12 — logic-heavy 5-line enumerate | 5-line loop with inline assert is straightforward | Not logic-heavy |
| S14-F011 | test_isolation.py CAT-5 — ordering dependency | `reset_game_state` autouse fixture clears state | Tests pass in any order; docstring is misleading |
| S14-F015 | test_damage_calculator.py:331-370 CAT-5 — factory fixtures should be class-scope | Mutable test instances require function-scope isolation | Class-scope risks shared state |
| DUP-004 | ShipInstance roundtrip 3-file cluster | Three files test different contract layers | HP roundtrip vs dict schema vs adapter |

## Out of Scope

(No P1-tier items were out of scope — those went to PROJ-478 or were excluded entirely.)
