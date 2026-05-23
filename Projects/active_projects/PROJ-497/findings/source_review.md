# PROJ-497: Source Review

## Provenance
- Parent project: PROJ-489 (ModifierService consolidation)
- Parent audit verification: `Projects/active_projects/PROJ-489/findings/audit_verification.md`
- Codex audit consult: `AgentCoordination/Scratchpad/Consult/20260523T120008Z_audit-PROJ-489/response.md`
- Codex planning consult (recommended split into 497/498): `AgentCoordination/Scratchpad/Consult/20260523T120100Z_plan-PROJ-489-blast-radius/response.md`
- Related DI: `DI-2026-05-23-004` (efficient_engines namespace mismatch)

## Background

PROJ-489 fixed `ModifierManager.add_modifier` to enforce `allow_abilities` (previously bypassed). Static scan over `data/components.json` x `data/modifiers.json` after that fix produced 105-168 theoretical mismatches per restricted modifier. `data/designs/*.json` scan: 0 shipped designs use invalid pairs today, so production content is safe. But: any new caller of `Component.add_modifier()` now gets strict behavior with no test coverage for rejection paths, and three data smells were surfaced.

## Static scan (Claude, re-verified 2026-05-23)

> **IMPORTANT — canonical rule.** `ModifierService.is_modifier_allowed()` enforces only
> `allow_types`, `deny_types`, and `allow_abilities` (any match). It does **NOT**
> enforce `deny_abilities`, even though some modifier rows (e.g., `hardened_mount`)
> declare one. See `game/simulation/services/modifier_service.py:79-106` and confirming
> note in `docs/guides/modifier_system.md:98,285` / `docs/guides/adding_modifiers.md:123-128`.
> The PROJ-498 matrix test MUST follow this live rule, not a stricter rule that includes
> `deny_abilities` — flagged by Codex mid-project review consult
> (`AgentCoordination/Scratchpad/Consult/20260523T120300Z_mpr-PROJ-497-498/response.md` Q2).

Script (re-runnable; matches live service rule):
```python
import json
mods = json.load(open('data/modifiers.json'))['modifiers']
comps = json.load(open('data/components.json'))['components']
for m in mods:
    r = m.get('restrictions') or {}
    allow_ab = r.get('allow_abilities') or []
    allow_t  = r.get('allow_types') or []
    deny_t   = r.get('deny_types') or []
    # NOTE: live service does NOT enforce deny_abilities. Do NOT add it here.
    valid = []
    for c in comps:
        abil = set((c.get('abilities') or {}).keys())
        ctype = c.get('type','')
        if allow_t and ctype not in allow_t: continue
        if deny_t and ctype in deny_t: continue
        if allow_ab and not any(a in abil for a in allow_ab): continue
        valid.append(c['id'])
    print(m['id'], len(valid))
```

Result (live rule):

| Modifier | Valid count | Notes |
|----------|-------------|-------|
| hardened_mount | 169 | All components. `deny_abilities=Armor` is declared but NOT enforced by the live service; under the live rule, all 169 components match (the 7 armor parts included). If `deny_abilities` enforcement is desired, that is a separate behavior-change project, not in PROJ-497 or PROJ-498. |
| simple_size_mount | 169 | No restrictions; matches all. |
| turret_mount | 7 | Weapon family. `Weapon` literal in allow list is inert under current key matching but harmless. SeekerWeaponAbility allowance is questionable (seekers ignore arc per `docs/systems/ability_reference.md:287`). |
| range_mount | 6 | Projectile+Beam. Seeker has dedicated endurance family. Likely intentional. |
| facing | 7 | Same SeekerWeaponAbility caveat as turret_mount. |
| precision_mount | 5 | BeamWeaponAbility only. `accuracy_add` consumed only by `BeamWeaponAbility` (`game/simulation/components/abilities/weapons.py:275-279`). Intentional. |
| rapid_fire | 7 | All-weapon. Intentional. |
| seeker_endurance | 1 | Only `capital_missile`. Codex flags as intentional (only seeker component shipped). |
| seeker_damage | 1 | Same. |
| seeker_armored | 1 | Same. |
| seeker_stealth | 1 | Same. |
| automation | 64 | RequiresMaintenance gate. Description matches. Intentional. |
| **efficient_engines** | **0** | **DATA BUG.** `allow_abilities=['Engine','Generator','Weapon','Thruster']` — none of these are real ability keys. Also `consumption_mult: -0.2` with default `multiply` operation would drive consumption negative. See `data/modifiers.json:448-464`, `game/simulation/components/modifiers.py:18-48`. |
| efficiency_mount | 22 | ResourceConsumption gate. Intentional. |

## Component.add_modifier production callers (5 sites)

| Site | Context | Behavior on rejection |
|------|---------|------------------------|
| `game/simulation/components/component.py:328-333` | The method itself; delegates to ModifierManager. | Returns `False`. |
| `game/simulation/battle_state.py:274-280` | Battle save restore: rebuilds component+modifier graph from saved state. | **SILENTLY drops** rejected mods. No log. |
| `game/simulation/entities/ship_serialization.py:223-228` | Ship save restore: rebuilds ship from JSON. | Logs unknown-id, but does NOT log allow_abilities rejection. |
| `game/simulation/services/modifier_service.py:222-234` | `ensure_mandatory_modifiers()`: auto-applies every allowed modifier on add. | If a modifier is allowed but `add_modifier` fails, silently skipped. |
| `game/ui/panels/builder_widgets.py:256` + `game/ui/screens/builder/interaction_controller.py:98` | UI builder: user-driven modifier add. | UI surfaces rejection in builder; existing tests cover this. |

The two save-restore paths are the latent-risk surface PROJ-498 will address.

## Allowed-implies-mandatory coupling (Codex finding)

`get_mandatory_modifiers()` returns every modifier where `is_modifier_allowed()` returns True (`game/simulation/services/modifier_service.py:108-125`). `ShipComponentManager.add_component()` calls `ensure_mandatory_modifiers()` automatically (`game/simulation/entities/ship_component_manager.py:72-80`). Therefore broadening an allow list also broadens the auto-application surface, not just the permitted-by-builder surface. **This raises the stakes of any allowlist edit in PROJ-497 Phase 2.**

## Disposition decisions

See `plan.md` "User Decision Points". Three open decisions:

1. `efficient_engines`: delete vs redesign vs keep inert.
2. `mini_capital_missile`: keep `BeamWeaponAbility` vs retype `SeekerWeaponAbility` vs defer.
3. `facing` / `turret_mount` seeker allowance: remove vs keep with documented intent vs defer.

Codex's recommendations (advisory, user decides):
- `efficient_engines`: prefer **delete**. Least regression risk; doubly malformed; redesign requires more user input than this audit cycle has captured.
- `mini_capital_missile`: USER call. Codex declines to recommend; it's a game-design decision.
- `facing` / `turret_mount` seeker: prefer **remove** OR **explicitly document intent**, but don't leave it ambiguous.

## Out-of-scope artifacts

- `mini_capital_missile` being typed `BeamWeaponAbility` is upstream data, not a modifier-service bug. Listed here only because it affects valid-pair counts for several modifiers.
- The snapshot comparator's "ignore extra keys" behavior (`tests/regression/modifier_ability_snapshots/conftest.py:147-173`) is pre-existing schema-drift tolerance unrelated to this project.
