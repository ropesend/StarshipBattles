# Phase 4: UI verification + docs

**Status:** Complete (2026-04-27)

---

## Tasks

### Task 4.1: Manual UI verification [Manual]
- [ ] Generate a galaxy with archetype rolling enabled. Find a nebula system.
- [ ] Click any hex inside — System panel shows the archetype effects with `source_label = "<system.name> (Nebula System)"`.
- [ ] Resolve combat in that system — confirm shield modifier applies.
- [ ] Try other archetypes (ancient_battlefield, precursor_ruins, ion_field) — verify expected effects.

**Notes:**

### Task 4.2: Update docs [Simple]
- [ ] `docs/systems/strategy_layer.md` — system archetype subsection.
- [ ] `docs/systems/ability_reference.md` — list system archetypes.
- [ ] `docs/01_ARCHITECTURE.md` — list `SystemAbilitySource`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] Manual smoke test passes
- [ ] Docs updated
- [ ] `python Tools/test_sharded/test_sharded.py` clean
- [ ] Update plan.md → "Awaiting Verification"
