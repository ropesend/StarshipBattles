# Phase 3: `SystemAbilitySource` adapter + iterator registration

**Status:** Complete (2026-04-27)

---

## Tasks

### Task 3.1: Implement `SystemAbilitySource` [Medium]
**File:** `game/strategy/services/ability_sources/system.py` (NEW)
**Tests:** `tests/unit/strategy/services/ability_sources/test_system.py` (NEW)

- [ ] Failing tests (standard adapter set):
  - [ ] `test_source_kind_is_system`
  - [ ] `test_source_label_format` — `"Sol System (Nebula System)"`.
  - [ ] `test_source_id_format`
  - [ ] `test_owner_id_is_none`
  - [ ] `test_get_abilities_returns_intrinsic`
  - [ ] `test_affects_hex_true_for_hex_inside_system`
  - [ ] `test_affects_hex_false_for_hex_outside_system`
  - [ ] `test_affects_system_true_only_for_self`
  - [ ] `test_get_activation_state_returns_none`
- [ ] Implement per [design.md](design.md). Use `system.contains_hex` or equivalent (verify the canonical predicate via `game/strategy/data/pathfinding.py:get_system_at_hex`).
- [ ] Re-export from `__init__.py`.

**Notes:**

### Task 3.2: Register provider with iterator [Simple]
**File:** `game/strategy/services/ability_iterator.py`

- [ ] Failing tests:
  - [ ] `test_iter_at_hex_inside_nebula_system_yields_system_source` — system has nebula archetype; querying iterator at any hex inside the system yields the source.
  - [ ] `test_iter_at_hex_in_archetypeless_system_yields_no_system_source`.
  - [ ] `test_iter_in_system_yields_system_source_when_archetyped`.
- [ ] Register both in-hex and in-system providers.

**Notes:**

### Task 3.3: Integration test — system-scope archetype effect propagates to all hexes [Medium]
**File:** `tests/integration/strategy/test_system_archetype_effects.py` (NEW)

- [ ] Build fixture: a system with `archetype="nebula"` and intrinsic_abilities containing `ShieldModifier scope: system`.
- [ ] `collect_sector_effects` at any hex inside the system returns the archetype's `ShieldModifier`.
- [ ] `collect_system_effects` returns the same effect.
- [ ] Combat in any hex inside this system has the multiplier applied (via PROJ-300 spec compiler path).

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
