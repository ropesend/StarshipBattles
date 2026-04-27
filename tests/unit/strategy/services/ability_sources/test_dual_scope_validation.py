"""PROJ-305 D13: registry validation — components must not declare an
ability with BOTH combat scopes (self/fleet/team) AND strategic scopes
(sector/system/etc) on the same ability instance, since that would
double-apply (FleetAuraManager + FleetAbilitySource both pick it up).

This is a lint-level check on the production data registry. If a future
component violates the rule, this test fails.
"""
import json
from pathlib import Path

from game.core.paths import Paths


COMBAT_SCOPES = frozenset({'self', 'fleet', 'team'})
STRATEGIC_SCOPES = frozenset({
    'sector', 'allied_sector', 'enemy_sector', 'player_sector',
    'system', 'allied_system', 'enemy_system', 'player_system',
    'planet', 'empire', 'allied_empire',
})


def _iter_components():
    path = Path(Paths.COMPONENTS_FILE) if hasattr(Paths, 'COMPONENTS_FILE') else None
    if path is None or not path.exists():
        # Fallback: data/components.json
        path = Path(__file__).resolve().parents[5] / "data" / "components.json"
    with path.open('r', encoding='utf-8') as f:
        registry = json.load(f)
    return registry.get('components', [])


def _scopes_in_entry(entry):
    """Extract every `scope` string from an ability entry (dict or list-of-dicts)."""
    if isinstance(entry, dict):
        scope = entry.get('scope')
        return {scope} if scope else set()
    if isinstance(entry, list):
        scopes = set()
        for sub in entry:
            if isinstance(sub, dict) and sub.get('scope'):
                scopes.add(sub['scope'])
        return scopes
    return set()


def test_no_component_ability_mixes_combat_and_strategic_scopes():
    """PROJ-305 D13: every ability instance is either combat-scoped OR
    strategic-scoped, never both. Mixing would cause double-apply."""
    violations = []
    for component in _iter_components():
        comp_id = component.get('id', '?')
        abilities = component.get('abilities', {})
        if not isinstance(abilities, dict):
            continue
        for ability_name, entry in abilities.items():
            scopes = _scopes_in_entry(entry)
            has_combat = bool(scopes & COMBAT_SCOPES)
            has_strategic = bool(scopes & STRATEGIC_SCOPES)
            if has_combat and has_strategic:
                violations.append(
                    f"  {comp_id}.{ability_name}: scopes={sorted(scopes)} "
                    f"(combat: {sorted(scopes & COMBAT_SCOPES)}, "
                    f"strategic: {sorted(scopes & STRATEGIC_SCOPES)})"
                )

    assert not violations, (
        "PROJ-305 D13 violation — the following abilities declare BOTH "
        "combat and strategic scopes on the same instance, which would "
        "double-apply (FleetAuraManager + FleetAbilitySource both fire):\n"
        + "\n".join(violations)
    )
