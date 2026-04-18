# Phase 4: Documentation update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-281 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove all references to the deleted `BattleScreen.start(team0, team1)` shim and `_build_fallback_outcome` from the docs. Document the `make_minimal_spec` helper as the canonical way to write tests that need a minimal battle.

---

## Tasks

### Task 4.1: Update `docs/systems/combat_simulation.md` [Simple]
**File:** `docs/systems/combat_simulation.md`
**Tests:** N/A

- [ ] Grep the file for "`BattleScreen.start(team0, team1)`", "test-convenience shim", "_build_fallback_outcome", "fallback outcome"
- [ ] Delete/rewrite each mention — the shim is GONE, not "retained for tests"
- [ ] Update the "Battle Results Screen" section if it mentions the fallback path
- [ ] Ensure the "every battle emits a BattleOutcome" contract is described without reference to the deprecated fallback

**Notes:** The PROJ-270 Phase 4.5 section likely mentions the fallback retention — that text needs to flip to "deletion complete via PROJ-281."

### Task 4.2: Update `combat_lab/COMBAT_LAB_DOCUMENTATION.md` (if applicable) [Simple]
**File:** `combat_lab/COMBAT_LAB_DOCUMENTATION.md`
**Tests:** N/A

- [ ] Grep for references to the legacy shim or fallback outcome — delete if found
- [ ] Grep for test-writing patterns that mention `scene.start([...])` — update to `make_minimal_spec`
- [ ] If the doc is silent on this, no changes needed

**Notes:**

### Task 4.3: Document the `make_minimal_spec` helper [Medium]
**File:** `tests/fixtures/README.md` (or `tests/README.md` if it's the canonical test-writing guide)
**Tests:** N/A

- [ ] Add a section explaining the helper: "Writing unit tests that need a minimal BattleSpec"
- [ ] Canonical pattern: `make_minimal_spec({0: [ship1], 1: [ship2]})` + `BattleController.start_from_spec` OR `run_battle`
- [ ] Cross-link from `docs/guides/simulation_testing.md` if that's where test authors look
- [ ] Note that this replaces the deleted `BattleScreen.start(team0, team1)` shim

**Notes:** Check whether `tests/fixtures/README.md` exists first. If not, either create it or add the section to the most discoverable place.

### Task 4.4: Update `CLAUDE.md` and other eradication-policy references [Simple]
**File:** `CLAUDE.md`
**Tests:** N/A

- [ ] Search for mentions of the "~46 test callers" legacy shim — update or remove
- [ ] If `CLAUDE.md` has a "System Migration Policy" example list, consider adding PROJ-281 as a worked example of successful eradication

**Notes:** This is low-priority polish — only do it if obvious content needs updating.

### Task 4.5: Final documentation verification [Simple]
**File:** N/A
**Tests:** N/A

- [ ] Repo-wide grep: `BattleScreen.start(team0` — only docstring breadcrumbs + archived project history remain
- [ ] Repo-wide grep: `_build_fallback_outcome` — zero non-historical hits
- [ ] Repo-wide grep: "test-convenience shim" — zero current references (it's gone)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All doc references to the deleted shim + fallback are either removed or flipped to "deleted in PROJ-281"
- [ ] `make_minimal_spec` helper is discoverable (documented in the tests-writing guide)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to "Awaiting archival"
