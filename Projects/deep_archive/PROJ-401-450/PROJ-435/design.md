# PROJ-435: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.

## Initial Analysis (from PROJ-429 Phase 8 Codex consult)

### Current state — `stat_rows_dynamic.py:381-463`

```python
_ACTIVATABLE_ABILITIES = {
    'GravityModifier': 'Gravity Mod',         # NOT in registry
    'RadiationShield': 'Rad Shield',          # NOT in registry
    'PlanetaryShield': 'Planet Shield',       # tagged PLANETARY_SHIELD + ENERGY_DRAINING
    'GeologicStabilizer': 'Geo Stabilizer',   # tagged STABILIZER + ENERGY_DRAINING
    'StellarStabilizer': 'Star Stabilizer',   # tagged STABILIZER + ENERGY_DRAINING
    'WarpFieldStabilizer': 'Warp Stabilizer', # tagged STABILIZER + ENERGY_DRAINING
}

modifier_abilities = {
    'ShieldModifier': ('Shield Mult', 'multiplier'),       # tagged COMBAT_MODIFIER
    'DamageModifier': ('Damage Mult', 'multiplier'),       # tagged COMBAT_MODIFIER
    'BuildRateBooster': ('Build Rate', 'multiplier'),      # tagged BUILD_RATE_BOOSTER
    'ResourceHarvestBooster': ('Harvest Boost', 'multiplier'),  # tagged RESOURCE_BOOSTER
}
```

### The gap

A naive "iterate `abilities_with_kind_tag(ENERGY_DRAINING)`" migration of
`_ACTIVATABLE_ABILITIES` would:
- Lose `GravityModifier` and `RadiationShield` (not in registry).
- Lose the display labels (`Gravity Mod` etc) which are UI-specific.

Closest registry tag covers only 4 of the 6 entries.

### Design space

**Option A — Extend the registry with a UI label facet.**
Adds a `display_name` or `UILabelFacet` to `AbilityMetadata`. Lets the UI
read the canonical label from one place. Downside: registry takes on a
UI concern. The existing `EffectFacet.display_name` is precedent for
display strings already living in the registry; this would extend that
to all kinds.

**Option B — Keep labels in the UI, drive iteration from kind tags +
named exceptions.**
UI keeps a label map. UI iterates `ENERGY_DRAINING` for activatable
abilities; appends `GravityModifier`/`RadiationShield` as named UI-only
exceptions. Same for modifier_abilities (iterate
`COMBAT_MODIFIER | RESOURCE_BOOSTER | BUILD_RATE_BOOSTER`). Eliminates
the literal ability-name set but keeps labels UI-side.

**Option C — Register `GravityModifier` and `RadiationShield`** with
appropriate kind tags and labels (e.g. add `PLANETARY_DEFENSE` tag),
then use Option A or B for labels.

Recommended starting point: Option B + register the two unregistered
abilities (Option C-lite). This minimises cross-layer concern leakage
while still eliminating the hardcoded ability-name literals.

### Key Patterns to Reuse

- **Registry-iteration pattern**: `planet_energy_engine.get_shield_info` —
  iterate `abilities_with_kind_tag(StrategicKind.PLANETARY_SHIELD)` rather
  than naming the ability inline.

### Dependencies & Risks

1. **Display-name policy**: There is no canonical home for UI labels
   today. Adding one to the registry is a small layering decision;
   keeping it in the UI repeats one map per UI screen if more screens
   appear. PROJ-435 should pick a side.
2. **`GravityModifier`/`RadiationShield` semantics**: They are
   simulation abilities that the UI groups with stabilizers/shields but
   they have no strategy-layer kind today. Phase 1 must decide whether
   their omission from the registry is intentional or an oversight.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
