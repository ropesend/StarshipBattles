# Phase 3: `StarAbilitySource` adapter + iterator registration

**Status:** Not Started
**Objective:** Implement the adapter; register with both hex and system iterators; verify system-scope effects flow into the System panel and sector-scope (at star's hex) flow into the Sector panel.

---

## Tasks

### Task 3.1: Implement `StarAbilitySource` [Medium]
**File:** `game/strategy/services/ability_sources/star.py` (NEW)
**Tests:** `tests/unit/strategy/services/ability_sources/test_star.py` (NEW)

- [ ] Failing tests first:
  - [ ] `test_source_kind_is_star`
  - [ ] `test_source_label_format` — `"Sol (G-class)"`.
  - [ ] `test_source_id_format`
  - [ ] `test_owner_id_is_none`
  - [ ] `test_get_abilities_returns_intrinsic_dict`
  - [ ] `test_affects_hex_true_only_at_star_global_location`
  - [ ] `test_affects_system_true_only_for_parent_system`
  - [ ] `test_get_activation_state_returns_none`
- [ ] Implement per [design.md](design.md). Adapter takes both `star` and parent `system` (system-context needed for global location).
- [ ] Re-export from `__init__.py`.

**Notes:**

### Task 3.2: Register provider with iterator [Simple]
**File:** `game/strategy/services/ability_iterator.py`
**Tests:** `tests/unit/strategy/services/test_ability_iterator.py`

- [ ] Failing tests:
  - [ ] `test_iter_at_star_hex_yields_star_source` — fixture: a system with a neutron star. Querying iterator at the star's hex yields the source.
  - [ ] `test_iter_at_non_star_hex_in_system_yields_no_star_for_sector_collection` — only system iteration picks up system-scope.
  - [ ] `test_iter_in_system_yields_star_source` — system iterator yields the star.
- [ ] Register both at-hex and in-system providers (or extend the single provider if iterator API supports both; match PROJ-300's API).

**Notes:**

### Task 3.3: Integration test — system-scope effect at non-star hex [Medium]
**File:** `tests/integration/strategy/test_system_effects_neutron_star.py` (NEW)

- [ ] Build fixture: a system with a neutron star and an empty hex H far from the star.
- [ ] `collect_sector_effects(system, H, ...)` — confirm the star's `EnvironmentalDamage scope: system` IS picked up at H (system-scope sources apply to every hex in the system per PROJ-300's iterator semantics).
- [ ] Confirm `collect_system_effects(system, ...)` also includes it.
- [ ] Confirm a sector-scope-only ability (if added in test fixture) at H is NOT picked up at H.

**Notes:** This test is the canonical proof that system-scope sources reach every hex in the system without per-hex registration.

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
