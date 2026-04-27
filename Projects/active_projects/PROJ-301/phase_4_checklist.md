# Phase 4: UI verification + docs

**Status:** Complete (2026-04-27)
**Objective:** Confirm the existing Sector panel renders planet-intrinsic providers correctly with no UI code changes (PROJ-300 already made the renderer source-kind-agnostic). Update docs.

---

## Tasks

### Task 4.1: Manual UI verification [Manual]

- [ ] Launch the game; generate a galaxy.
- [ ] Click on a volcanic planet hex. Verify Sector Effects shows `Plasma Damage -<rolled>/turn — Active (<planet.name> (Volcanic))`.
- [ ] Click on a gas giant hex. Verify both `Thrust Modifier` and `Strategic Speed Modifier` rows show with rolled values.
- [ ] Click on an oceanic planet hex. Verify Sector Effects is empty (or shows only any facility-derived effects on that planet).
- [ ] If a planet hex also has a storm: verify both planet and storm appear as separate providers under the right effect (when ability_name + damage_type match).

**Notes:** If labels render badly (e.g. truncated), capture and surface; the renderer itself was changed in PROJ-300 Phase 8 — issues are likely in display sizing, not source-kind logic.

### Task 4.2: Update `docs/systems/strategy_layer.md` [Simple]

- [ ] Add a planet-intrinsic-effects subsection under the unified ability source pipeline section. Reference `data/planet_types.json`.

**Notes:**

### Task 4.3: Update `docs/systems/ability_reference.md` [Simple]

- [ ] Add a "Planet intrinsic abilities" section listing the planet types with intrinsic effects, the abilities they project, and the rolled-value ranges.
- [ ] Note that empty `abilities` means "no intrinsic effects" — this is expected for most planet types.

**Notes:**

### Task 4.4: Add to `docs/01_ARCHITECTURE.md` if appropriate [Simple]

- [ ] If the architecture doc lists ability sources by name, add `PlanetIntrinsicAbilitySource`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] Manual UI verification passes
- [ ] Docs updated
- [ ] `pytest tests/ --testmon` clean
- [ ] `python Tools/test_sharded/test_sharded.py` clean (full suite before declaring project done)
- [ ] Update status to `Complete`
- [ ] Update plan.md
- [ ] Move project to "Awaiting Verification"
