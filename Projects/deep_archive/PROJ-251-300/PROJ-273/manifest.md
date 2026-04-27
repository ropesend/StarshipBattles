# PROJ-273 File Manifest

> Generated during project init. Used by parallel execution conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/simulation/combat/ability_stat_registry.py` | Production | NEW — registry module + `emit_entries_for_ability` helper |
| `game/ui/screens/battle_setup/spec_compiler.py` | Production | Delete `_ABILITY_TO_STAT_KEY` (L70-74), use shared helper (L349, L354) |
| `game/strategy/combat/spec_compiler.py` | Production | Replace hardcoded `stat_key=...` at L353, L385, L400, L412, L444 with registry emission |
| `game/simulation/combat/fleet_aura_manager.py` | Production | Add unknown-stat_key WARN in `_apply_bonuses` |
| `tests/unit/simulation/combat/test_ability_stat_registry.py` | Test | NEW — unit tests for registry + glob-driven coverage test |
| `tests/unit/simulation/test_unified_entry_guard.py` | Test | Replace hardcoded 10-design list with glob reference (around L540-563) |
| `tests/unit/ui/screens/battle_setup/test_spec_compiler.py` | Test | Update imports if registry import changes |
| `tests/unit/strategy/combat/test_spec_compiler.py` | Test | Update imports if registry import changes |
| `docs/systems/combat_simulation.md` | Doc | Update external-modifier composition paragraph |
| `docs/systems/strategy_layer.md` | Doc | Update "extending `_ABILITY_TO_STAT_KEY`" guidance (L798) to point at new module |
| `docs/02_PATTERNS.md` | Doc | Add "Pattern 26: Ability-Stat Registry" entry |
