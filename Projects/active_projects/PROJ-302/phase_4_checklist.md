# Phase 4: UI verification + docs

**Status:** Not Started
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

### Task 4.2: Update docs [Simple]

- [ ] `docs/systems/strategy_layer.md` — add star-intrinsic effects subsection.
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
