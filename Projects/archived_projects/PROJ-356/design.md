# PROJ-356: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit](../../../Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/)
- **Type:** Technical Debt Review
- **Date:** 2026-05-04
- **Report:** [View Full Report](../../../Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/report.md)
- **Source finding:** #9 — "AI PDC capability cache checks a non-existent ability" (P1)

## Initial Analysis

### Bug location
`game/ai/controller.py:229` — inside `_build_capabilities_cache()`:
```python
weapons = entity.get_components_by_ability('WeaponAbility', operational_only=True)
pdc_weapons = [w for w in weapons if w.has_ability('PDCAbility')]
```

### Why it is dead code
A repo-wide grep finds no `class PDCAbility` definition anywhere. PDC was generalized to a tag-based query in PROJ-241. The current API surfaces:
- `Component.has_pdc_ability()` (`game/simulation/components/component.py:191`) — delegates to ability_manager
- `AbilityManager.has_pdc_ability()` — `'pdc' in ab.tags`
- `IComponentProtocol.has_pdc_ability()` documented as "True if any ability has 'pdc' in its tags"

The string `'PDCAbility'` is not a real ability class name. `has_ability('PDCAbility')` therefore always returns False. `pdc_components` is permanently `[]`; `'has_pdc'` is permanently `False`.

### Consumer analysis
- `targeting_system.py:166` — uses `comp.has_pdc_ability()` directly, unaffected.
- `weapon_firing_system.py:184` — uses `comp.has_pdc_ability()` directly, unaffected.
- `TargetEvaluator` paths that consume `ship_capabilities_cache['pdc_components']` / `'has_pdc'` — these silently see no PDC weapons. Verify in Phase 1 whether any rule evaluation depends on this branch (it would be silently misbehaving today).

## Architecture
- AI controller layer — `game/ai/`
- Component capability surface — `game/simulation/components/component.py`, `ability_manager.py`
- The fix is local to the cache builder; no cross-layer change.

## Key Patterns to Reuse
- **Tag-based ability queries** — `Component.has_pdc_ability()` is the canonical check; mirror this rather than introducing yet another path.
- **Test pattern** — see existing `tests/unit/ai/test_controllable_adapter_edge_cases.py:231` for how the test fixture stubs `get_components_by_ability`.

## Dependencies & Risks
1. **Behavior change risk** — fixing the cache may change AI targeting behavior if a `pdc_arc` rule was silently scoring zero candidates. Mitigation: characterization test of current behavior first, then assert the fixed behavior, then run sharded suite.
2. **Test fixture in `test_controllable_adapter_edge_cases.py:231`** asserts the call uses `'PDCAbility'` — that test will need updating to reflect the corrected query.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
