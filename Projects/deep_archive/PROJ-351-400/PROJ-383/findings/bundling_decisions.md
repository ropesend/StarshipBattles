# Bundling Decisions — 2026-05-07_220621_legacy-audit

This file is identical across all 11 sibling projects (PROJ-383..PROJ-393) created from the same audit. It records the Phase D decisions made during the interactive bundling.

## Default Proposal (Phase D Step 1)

| # | Proposed Project | Cluster | Verified | Uncertain | INFO |
|---|------------------|---------|----------|-----------|------|
| 1 | command_handlers.py shim eradication | shim | 4 | 0 | 0 |
| 2 | PROJ-241 deprecated `*_static` methods | abilitymanager+modifiermanager | 2 | 0 | 0 |
| 3 | formula_evaluator backward-compat aliases | formula_evaluator | 1 | 0 | 0 |
| 4 | Save-format migration eradication | save migrations (4 files) | 4 | 0 | 0 |
| 5 | Galaxy backward-compat property forwarders | galaxy `_global_hex_*` | 1 | 0 | 0 |
| 6 | ModifierLogic deprecated class wrapper | ModifierLogic | 1 | 1 | 1 |
| 7 | score_planet_for_race wrapper | score_planet | 1 | 0 | 0 |
| 8 | log_event module-level compat shim | event_logging shim | 1 | 0 | 0 |
| 9 | Underscore-prefixed legacy pairs | dup pairs | 2 | 0 | 0 |
| 10 | Misc orphan wrappers + zero-call-site placeholders | scattered | 9 | 5 | 1 |
| 11 | Test-injection legacy fallbacks + comment cleanups | scattered | 11 | 3 | 0 |

## User Adjustments (Phase D Step 2)

- Accepted 11 separate projects (Recommended, default).
- Save-format migration kept as one project (bundle 4) covering all 4 files (Recommended, default).

## UNCERTAIN Resolutions (Phase D Step 3)

| ID | Symbol | Decision | Routed to |
|---|---|---|---|
| LEG-01-008 | `find_metadata` (effect_ability_metadata) | Exclude — intentional API stability layer | — |
| LEG-01-017 | `_formation_to_dict/from_dict` dups (task_force + replay_serialization) | Include — move to `FormationSpec.to_dict/from_dict` | PROJ-391 |
| LEG-02-001 | `Game.running` flag (app.py) | Exclude — test-bypass backdoor still needed | — |
| LEG-02-006 | `format_planet_info` `view is None` branch | Include — audit callers, migrate, delete branch | PROJ-393 |
| LEG-02-015 | `_menu_scene` private property (app.py) | Include — rename to public `menu_scene` | PROJ-392 |
| LEG-03-012 | `Ship.to_dict/from_dict` | Exclude — documented Facade pattern | — |
| LEG-03-013 | `to_roman` (planet_naming) | Exclude — 1 LOC convenience | — |
| LEG-03-023 | Combat Lab vars in battle_screen.py | Include — PROJ-270 archived, reclaim now | PROJ-393 |
| LEG-03-024 | `_LEGACY_PATTERN` sprite regex | Include — task starts with asset scan, deletes if no matches | PROJ-393 |

## INFO Resolutions (Phase D Step 4)

| ID | Symbol | Decision | Routed to |
|---|---|---|---|
| LEG-02-005 | Historical save-format comment | Include | PROJ-393 |
| LEG-02-017 | Stale "PROJ-258" docstring tag | Include | PROJ-393 |
| LEG-03-010 | `get_asset_manager` 1-line alias | Include — find-and-replace | PROJ-392 |
| LEG-03-015 | `calculate_snap_value` static | Include — disappears with cluster 6 | PROJ-388 |
| LEG-03-016 | `get_crew_required` wrapper | Include — rename helper to public | PROJ-392 |
| LEG-04-014 | `policy_manager` auto-create singleton | Exclude — large scope, separate project | — |
| LEG-04-015 | `registry.py` module-level singleton | Exclude — large scope, separate project | — |
| Pair 4 | `ModifierService` vs `ModifierLogicService` | Exclude — needs architectural decision first | — |

## Final Bundle Composition

| PROJ-NNN | Title | Verified | Included Uncertain | Included INFO |
|---|---|---|---|---|
| PROJ-383 | command_handlers.py shim eradication | 4 | 0 | 0 |
| PROJ-384 | PROJ-241 deprecated `*_static` methods | 2 | 0 | 0 |
| PROJ-385 | formula_evaluator backward-compat aliases | 1 | 0 | 0 |
| PROJ-386 | Save-format migration eradication | 4 | 0 | 0 |
| PROJ-387 | Galaxy backward-compat property forwarders | 1 | 0 | 0 |
| PROJ-388 | ModifierLogic deprecated class wrapper | 1 | 0 | 1 |
| PROJ-389 | score_planet_for_race wrapper migration | 1 | 0 | 0 |
| PROJ-390 | log_event module-level compat shim retirement | 1 | 0 | 0 |
| PROJ-391 | Underscore-prefixed legacy pair consolidations | 2 | 1 | 0 |
| PROJ-392 | Misc orphan wrappers + zero-call-site placeholders | 9 | 1 | 2 |
| PROJ-393 | Test-injection fallbacks + comment cleanups | 11 | 3 | 2 |

## Excluded From All Projects

**UNCERTAIN excluded:** LEG-01-008, LEG-02-001, LEG-03-012, LEG-03-013

**INFO excluded:** LEG-04-014, LEG-04-015, ModifierService/ModifierLogicService Pair 4

**OUT_OF_SCOPE (audit's own verifier disputed or marked intentional):**
LEG-01-002 (audit recommended keep), LEG-01-012 / LEG-04-009 (`ModifierManager` vs `ModifierService` intentional split), LEG-01-013 / LEG-01-014 (empty `__init__.py` DISPUTED), LEG-02-008, LEG-02-010 (false positives), LEG-02-011, LEG-02-012 (Pattern 30/31 documented coexistence), LEG-02-014 (no action needed), LEG-03-001 (`noqa: F401` intentional side-effect), LEG-03-011 (factory pattern), LEG-03-019 (legitimate deserialization), LEG-03-020 (no findings), LEG-03-026 (state-audit territory), LEG-04-002 / LEG-04-016 (style-only), LEG-04-003 / LEG-04-011 / LEG-04-012 (DISPUTED duplicates), LEG-04-010 / LEG-04-013 / LEG-04-017 (verified no violations / retracted).
