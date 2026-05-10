# Phase 4: UI verification + docs

**Status:** Complete (2026-04-27)
**Objective:** Verify the existing System panel shows star-projected system-scope effects; the Sector panel shows star sector-scope effects at the star's hex. Update docs.

---

## Tasks

### Task 4.1: Manual UI verification [Manual]

- [ ] Generate a galaxy. Find a neutron star system.
- [ ] Click any hex inside the neutron star system. System panel shows `Radiation Damage -<rolled>/turn — Active (<star.name> (Neutron Star))` in the system effects section.
- [ ] Sail a fleet through the system; confirm hull damage applies each turn.
- [ ] Find a pulsar system. Resolve combat there. Confirm shield modifier applies (existing combat path picks up the system-scope `ShieldModifier`).
- [ ] Click a binary system; confirm thrust and strategic-speed reductions apply.

**Notes:**

### Task 4.2: Hostile-system hazard hint in System panel [Medium] *(added 2026-04-27, decisions.md D8)*
**File:** `game/ui/panels/system_tree_panel.py`
**Tests:** `tests/unit/ui/panels/test_system_tree_panel_hazard.py` (NEW, or extend existing)

- [ ] Failing tests first:
  - [ ] `test_pulsar_system_renders_hazard_hint` — system with star-projected `ShieldModifier scope: system` < 1.0 produces a hazard line in the System panel.
  - [ ] `test_neutron_star_system_renders_hazard_hint` — system with star-projected `EnvironmentalDamage scope: system` produces a hazard line.
  - [ ] `test_g_class_system_renders_no_hazard_hint` — benign systems do not.
- [ ] Implement `_add_system_hazard_hint(system, empire_id)` in the panel:
  - Walk system effects via `collect_system_effects`.
  - For any effect whose any provider has `source_kind == 'star'` AND ability is `ShieldModifier (multiplier < 1.0)` OR `EnvironmentalDamage (rate > 0)`, emit a single red-bordered "Hazard: <star.name> (<type>) — <human description>" line at the top of the system panel.
  - Reuses the existing System Effects renderer for the detail lines below.
- [ ] Run tests — green.

**Notes:** Counterpart to decisions.md D7. The "uncapped hostile systems" decision only works if the player can see hostility before entering. This task closes that loop.

### Task 4.3: Update docs [Simple]

- [ ] `docs/systems/strategy_layer.md` — add star-intrinsic effects subsection. Document D7 (hostile systems are intentional, no cap) and D8 (hazard hint UI).
- [ ] `docs/systems/ability_reference.md` — add stellar effects entries.
- [ ] `docs/01_ARCHITECTURE.md` — list `StarAbilitySource` if applicable.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] Manual UI verification passes
- [ ] Docs updated
- [ ] `python Tools/test_sharded/test_sharded.py` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md → "Awaiting Verification"
