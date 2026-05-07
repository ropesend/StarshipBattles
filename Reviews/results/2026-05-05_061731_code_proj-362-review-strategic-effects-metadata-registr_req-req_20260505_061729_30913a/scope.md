# Review Scope: PROJ-362 Strategic Effects Metadata Registry
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_061729_30913a
**Scope:**
- `game/strategy/services/effect_ability_metadata.py` (new)
- `game/strategy/services/system_effects_collector.py` (decomposed `_aggregate`)
- `tests/unit/strategy/services/test_effect_ability_metadata.py` (new)
- `tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py` (new)
- `tests/unit/strategy/services/test_system_effects_collector_decomposition.py` (new)
- `Projects/active_projects/PROJ-362/decisions.md`

**Instructions:**
- Verify the registry covers all current strategic effect abilities (no gaps)
- Confirm decomposed functions are layered cleanly with single responsibility each
- Check that EnvironmentalDamage special-case fallback is correctly preserved
- Confirm Phase 4 (_legacy_provider_fields retirement) is genuinely deferred — UI consumers still rely on it
- The _aggregate still accepts unused registries/system params; verify removal would break callers (justify deferral or flag)
- Layer-boundary check (registry should not import from UI/simulation)

**Context:** Just-completed project commit `f9bdd27e1`. CC dropped 47→3 in `_aggregate`. Phase 4 deferred per plan. 5 UI consumers still read legacy keys.
