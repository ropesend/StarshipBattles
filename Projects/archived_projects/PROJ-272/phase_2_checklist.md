# Phase 2: Reconcile Phase 7 stack_group claim + thread stack_group through strategy compiler

**Status:** Complete
**Risk:** MEDIUM (semantic change; must not break existing Track A tests)
**Depends On:** None
**Objective:** PROJ-271 Phase 7 claimed "unified cross-source MAX within shared stack_group" but provider auras bucket by `type(ab).__name__` ("ShieldModifier") while external entries bucket by `stat_key` ("shield_capacity_mult"). They never compose via MAX even with matching stack_group. Separately: strategy compiler's `_real_entry` hardcodes `stack_group=None`, so even same-source strategy entries (e.g., two overlapping storms) SUM instead of MAX. Phase 2 scales back the claim + threads stack_group through where it's missing.

## Tasks

### Task 2.1: Audit current stack_group flow [Simple]
- [ ] Grep `stack_group` across `game/` — map every producer + consumer.
- [ ] Document in Notes: which paths correctly thread stack_group, which hardcode None, which drop it.
- [ ] Confirm: provider path uses `type(ab).__name__` key; external path uses `stat_key` key. Write the finding as a locked constraint.

### Task 2.2: Strategy compiler threads stack_group [Medium]
**File:** `game/strategy/combat/spec_compiler.py`

- [ ] Failing test: two overlapping storm `shield_capacity_mult` entries with same `stack_group="storm"` → MAX, not SUM.
- [ ] `_real_entry` currently takes `stack_group=None` implicitly. Update signature to accept `stack_group: Optional[str] = None` and propagate to `ModifierEntry`.
- [ ] `_entries_from_environmental_effects` passes `stack_group="storm"` (or similar) for storm entries.
- [ ] `_entries_from_fleet_combat_modifiers` passes appropriate stack_groups (e.g., `"fleet_shield_mult"`, `"fleet_damage_mult"`, `"fleet_flat_shield"`).
- [ ] Run — test passes.

### Task 2.3: Update docs to reflect WITHIN-SOURCE-ONLY composition [Simple]
**Files:** `docs/02_PATTERNS.md` Pattern 24, `docs/systems/combat_simulation.md`, `Projects/active_projects/PROJ-271/decisions.md` (historical note)

- [ ] Pattern 24 "External-Stats Bridge": clarify that stack_group composition is within-source (provider-only OR external-only), NOT cross-source. Document the key-scheme constraint (provider uses class names; external uses stat_keys).
- [ ] `combat_simulation.md` §External modifiers: same clarification.
- [ ] Add a "Known Limitation" subsection explaining why cross-source unification would require a class-name → stat_key registry.

### Task 2.4: Test lock for within-source composition [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

- [ ] Explicit test proving provider ShieldModifier aura + external `shield_capacity_mult` entry with matching `stack_group` do NOT compose via MAX (they're in different buckets). Test documents the intentional limitation.

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] Strategy compiler stack_group threading tested
- [ ] Docs reflect within-source-only composition
- [ ] Update plan.md
