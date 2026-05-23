# PROJ-460 Phase 6: doc consolidation (LAST-runner responsibility, protocol §9.2)

**Status:** Complete
**Objective:** As the LAST of PROJ-457 / PROJ-459 / PROJ-460 to finish, apply all three projects' staged `_doc_consolidation/PROJ-*_pending.md` blocks as a single coordinated edit to `docs/01_ARCHITECTURE.md` (+ `docs/systems/strategy_layer.md` per PROJ-459's block) and `git rm` the three pending files.

**Last-runner determination:** `git ls-tree --name-only origin/main Projects/active_projects/_doc_consolidation/` returned `PROJ-457_pending.md` + `PROJ-459_pending.md` (both already on main → neither was last). With `PROJ-460_pending.md` on group-c, all three are present → PROJ-460 is the LAST runner (protocol §9.2).

## Tasks
- [x] Read all three pending blocks (PROJ-457: no-op/zero edits; PROJ-459: fleet_serde → 01_ARCHITECTURE data/ bullet + strategy_layer.md; PROJ-460: simulation serde modules → 01_ARCHITECTURE).
- [x] Apply PROJ-459's `docs/01_ARCHITECTURE.md` edit (add `fleet_serde.py` to the `data/` bullet).
- [x] Apply PROJ-459's `docs/systems/strategy_layer.md` edit (append the fleet_serde sentence).
- [x] Apply PROJ-460's `docs/01_ARCHITECTURE.md` edits (replay/ bullet → 3 serde modules; root-modules bullet → battle_state_serde + battle_controller_spec).
- [x] PROJ-457 block is a no-op (its plan dropped the exceptions.py split; Phases 1-3 are concrete instances of existing patterns) — nothing to apply.
- [x] `docs/02_PATTERNS.md`: both PROJ-459 and PROJ-460 marked their patterns-doc edit OPTIONAL; left as no-op (the existing generic serde/AST-guard wording covers the sibling-module pattern; not adding a new § for a structural one-off).
- [x] `git rm` the three `_doc_consolidation/PROJ-*_pending.md` files.
- [x] Verify docs still coherent (no broken anchors).

## Phase Completion Checklist
- [x] All three pending blocks applied (or confirmed no-op)
- [x] Three pending files removed via `git rm`
- [x] Commit message: `PROJ-457 + PROJ-459 + PROJ-460 consolidated doc updates`
- [x] No production code touched (docs only)
- [x] Race-condition guard: re-fetched origin/main before the merge; confirmed docs were not already consolidated by another group
