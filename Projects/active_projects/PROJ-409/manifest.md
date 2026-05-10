# PROJ-409 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| game/ui/screens/strategy_game_state_manager.py | Production | MAJ-014 — remove `EnginePhaseError` import + defensive catch. |
| tests/unit/ui/screens/test_strategy_game_state_manager.py | Test | New regression: canonical `TurnFailedError` path + raw `EnginePhaseError` propagates after removal. |
| game/strategy/facade/strategy_session_facade.py | Production (read-only) | The conversion that makes the defensive catch unnecessary. |
| MAJ-013 target | TBD | Discovered during investigation. |
| Projects/active_projects/PROJ-409/decisions.md | Decisions | Both closures documented. |
| Projects/active_projects/PROJ-395/decisions.md | Decisions (cross-ref) | Pointer to PROJ-409 closure SHAs. |
