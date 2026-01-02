# Phase 6: Data Migration Plan

## Status: Ready to Start

## Pre-Migration Action Required (from Code Reviews)

> [!CAUTION]
> **CommandAndControl Ability Missing**: The `ABILITY_REGISTRY` in `abilities.py` does not contain a `CommandAndControl` entry. This ability is referenced in `vehicleclasses.json` requirements for ALL ship classes. 
> **Action**: Add `CommandAndControl` class before running migration.

## Consolidated Audit Findings (Jan 2, 2026)

| Review Area | Status | Key Finding |
|-------------|--------|-------------|
| AI & Formation | ✅ Ready | Uses shims (OK), PDC uses tags correctly |
| Game Integration | ✅ Ready | Ship init and game loop correct |
| Validator | ⚠️ Fix First | Missing `CommandAndControl` ability |
| Data Completeness | ⏳ Migrate | Weapon stats at root, not in abilities dict |

## Data Migration Requirements

### 1. Add Missing Ability (abilities.py)
```python
class CommandAndControl(Ability):
    """Marks component as providing ship command capability."""
    def get_ui_rows(self):
        return [{'label': 'Command', 'value': 'Active', 'color_hint': '#96FF96'}]

# Add to ABILITY_REGISTRY:
"CommandAndControl": CommandAndControl,
```

### 2. Migration Script Tasks
Create `scripts/migrate_legacy_components.py`:

1. **Weapons**: Move `damage`, `range`, `reload`, `firing_arc`, `projectile_speed` from root into:
   ```json
   "abilities": {
       "ProjectileWeaponAbility": {"damage": 40, "range": 2400, ...}
   }
   ```

2. **Engines/Thrusters**: Remove redundant `thrust_force` and `turn_speed` from root (keep `CombatPropulsion`/`ManeuveringThruster` in abilities)

3. **Validation**: Run `ship_validator.py` on all component data after migration

## Verification Checklist
- [ ] Add `CommandAndControl` to `abilities.py`
- [ ] Run tests to verify no regression
- [ ] Create migration script with dry-run mode
- [ ] Run migration on `data/components.json`
- [ ] Verify 470+ tests still pass
