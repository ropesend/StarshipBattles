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
