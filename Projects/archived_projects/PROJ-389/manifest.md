# PROJ-389 File Manifest

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/formulas/habitability.py` | Production | Edit | LEG-02-009 — delete `score_planet_for_race` wrapper at line 99 |
| `game/strategy/formulas/__init__.py` | Production | Edit | LEG-02-009 — drop `score_planet_for_race` from public re-export at line 9 |
| `game/strategy/engine/population_engine.py` | Production | Migrate-callers | 1 call site at line 139 |
| `game/strategy/engine/happiness_engine.py` | Production | Migrate-callers | 1 call site at line 117 |
| `game/strategy/facade/slices/economy_slice.py` | Production | Migrate-callers | 1 call site at line 157 |
| `game/strategy/formulas/colony_output.py` | Production | Migrate-callers | 3 call sites at lines 47, 95, 152 |
| `game/ui/screens/strategy_detail_fmt.py` | Production | Migrate-callers | 1 call site at line 129 |
| `game/strategy/facade/dto/colony_demographic_view.py` | Production | Doc-update | Docstring referenced wrapper — updated to `calculate_habitability` |
| `tests/unit/strategy/engine/test_happiness_engine.py` | Tests | Migrate-callers | Direct import + 18 call sites updated alongside wrapper deletion |
| `tests/unit/strategy/formulas/test_colony_output.py` | Tests | Migrate-callers | 3 monkeypatches + 3 docstring refs updated |
| `tests/unit/strategy/engine/test_harvesting_engine_habitability.py` | Tests | Migrate-callers | 1 monkeypatch + 1 docstring updated |
| `tests/unit/ui/screens/test_strategy_detail_fmt.py` | Tests | Migrate-callers | 8 patch targets + 2 docstring refs updated |
| `docs/04_SERVICES.md` | Docs | Edit | 2 references updated to canonical name |
| `docs/systems/strategy_layer.md` | Docs | Edit | 1 reference updated to canonical name |

> **PROJ-406 reconciliation Note:** The original 6-caller estimate covered the production sites only. The 4 test files + 3 live doc files above were migrated alongside the wrapper deletion (deleting the wrapper would otherwise break their imports / monkeypatch targets / cross-references). Recorded in `phase_1_checklist.md` "Out-of-band cleanup" section.
