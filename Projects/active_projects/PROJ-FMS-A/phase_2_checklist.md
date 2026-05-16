# PROJ-FMS-A Phase 2: Abilities — Warhead / Laserhead / SmallTargetingSensor / RamTarget

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Add ability classes that the Phase 1 components reference. **No combat behavior** — that's PROJ-FMS-B. This phase only adds the class definitions, registration, and stat-aggregator integration where it's free.

## Tasks

### Ability classes
- [x] `WarheadAbility` — new class in [`game/simulation/components/abilities/`](../../../game/simulation/components/abilities/) (probably a new file `warhead.py` or under `weapons.py`). `AbilityLayer.BOTH`. Single data attribute: `damage` (int). No `apply()` behavior — that's PROJ-FMS-B Phase 3.
- [x] `LaserheadAbility(BeamWeaponAbility)` — subclass of [`BeamWeaponAbility`](../../../game/simulation/components/abilities/weapons.py). Adds `consume_on_fire: bool = True` data attribute. Inherits everything else (range, damage, accuracy, falloff). Verify [`game/simulation/components/ability_manager.py:71-145`](../../../game/simulation/components/ability_manager.py#L71) MRO lookup finds it AND [`weapon_registry.py:78-94`](../../../game/simulation/combat/weapon_registry.py#L78) `has_ability('BeamWeaponAbility')` returns True for instances.
- [x] `RamTargetAbility` — new class. `AbilityLayer.COMBAT`. Holds an optional `target_id` runtime state. No `apply()` — PROJ-FMS-B Phase 4.
- [x] `SmallTargetingSensor` is a component type only — no new ability class needed (it carries existing `ToHitAttackModifier`). Confirm the ability lookup correctly resolves through the existing aggregator.

### Registration
- [x] Register `WarheadAbility`, `LaserheadAbility`, `RamTargetAbility` in [`game/simulation/components/abilities/__init__.py`](../../../game/simulation/components/abilities/__init__.py).
- [x] Verify [`game/simulation/components/component_loader.py:278-303`](../../../game/simulation/components/component_loader.py#L278) `create_component()` correctly instantiates abilities from the registered classes (this is the actual component / ability instantiation path; the `ability_factory.py` file referenced earlier does NOT exist in this codebase).

### Tests
- [x] Instantiate each new ability class from a component spec; verify fields populate.
- [x] `LaserheadAbility` instance: confirm `isinstance(instance, BeamWeaponAbility)` and `has_ability('BeamWeaponAbility')` both true.
- [x] Create a `Ship` with a `Laserhead` component and verify `BeamWeaponAbility.calculate_hit_chance()` is callable on it (sanity check the MRO path).
- [x] Stack a `SmallTargetingSensor` with a `Laserhead` on the same vehicle; verify the `ToHitAttackModifier` is included in the laserhead's accuracy calc via the existing stat aggregator. (This is the load-bearing reason `Laserhead` subclasses `BeamWeaponAbility` rather than being a fresh class.)

## Verification
- `python Tools/test_sharded/test_sharded.py`
- Targeted: `pytest tests/unit/simulation/components/abilities/ -k 'warhead or laserhead or ram'`
- No regression in existing weapon-firing tests.

## Exit criteria
- All four new components instantiate correctly from data.
- `LaserheadAbility` participates in beam family detection.
- `SmallTargetingSensor` contributes to-hit modifiers through the existing aggregator.
- No combat behavior wired — `WarheadAbility.apply()` and `RamTargetAbility.apply()` raise `NotImplementedError` (will be filled in PROJ-FMS-B).
