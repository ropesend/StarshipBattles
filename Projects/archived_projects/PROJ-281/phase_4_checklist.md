# Phase 4: Documentation update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-281 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove all references to the deleted `BattleScreen.start(team0, team1)` shim and `_build_fallback_outcome` from the docs. Document the `make_minimal_spec` helper as the canonical way to write tests that need a minimal battle.

---

## Tasks

### Task 4.1: Update `docs/systems/combat_simulation.md` [Simple]
**File:** `docs/systems/combat_simulation.md`
**Tests:** N/A

- [x] Grepped the file for "`BattleScreen.start(team0, team1)`", "test-convenience shim", "_build_fallback_outcome", "fallback outcome" — only the PROJ-270 Phase 4.5 paragraph (line 362–368) still referenced the shim
- [x] Rewrote that paragraph: appended a PROJ-281 (2026-04-18) block announcing the deletion, pointing to `make_minimal_spec` / `start_battle_screen_with_minimal_spec` as the canonical test-writing entry, and documenting the new lazy-outcome behavior on `BattleController.get_outcome()`
- [x] "Every battle emits a `BattleOutcome` that the UI consumes" is now unconditional — no fallback path

**Notes:** The PROJ-270 Phase 4.5 text is preserved as historical context; the PROJ-281 block states the current contract authoritatively.

### Task 4.2: Update `combat_lab/COMBAT_LAB_DOCUMENTATION.md` (if applicable) [Simple]
**File:** `combat_lab/COMBAT_LAB_DOCUMENTATION.md`
**Tests:** N/A

- [x] Grepped for references to the legacy shim — zero matches. No changes needed.
- [x] Grepped for `scene.start([...])` test-writing patterns — zero matches. No changes needed.

**Notes:** Combat Lab docs never mentioned the shim — it was a pure UI-layer artifact.

### Task 4.3: Document the `make_minimal_spec` helper [Medium]
**File:** `tests/fixtures/README.md`
**Tests:** N/A

- [x] Added a "Writing unit tests that need a minimal battle (PROJ-281)" section to the `battle.py` module entry
- [x] Canonical pattern documented: `start_battle_screen_with_minimal_spec(scene, {0: [ship], 1: [ship]})` with code example
- [x] Helper contract documented: ship-identity preservation, `TeamEliminatedCondition` default, 2+ teams, empty-team support
- [x] Headless-path documented: `make_minimal_spec` + `run_battle(spec, ...)` for tests with no screen/controller lifecycle
- [x] Noted that this replaces the deleted `BattleScreen.start(team0, team1)` shim
- [x] Updated the module's "Factory Functions" listing to include `make_minimal_spec` and `start_battle_screen_with_minimal_spec`
- [x] Updated `Last Updated:` marker to 2026-04-18 (PROJ-281 Phase 4)

**Notes:** `docs/guides/simulation_testing.md` is the Combat Lab simulation-test author guide (different audience — Combat Lab scenarios, not pytest unit tests). No cross-link added; pytest test authors work from `tests/fixtures/README.md` and `tests/README.md`.

### Task 4.4: Update `CLAUDE.md` and other eradication-policy references [Simple]
**File:** `CLAUDE.md`
**Tests:** N/A

- [x] Grepped `CLAUDE.md` for `BattleScreen.start` / "test callers" / PROJ-281 — zero mentions to update
- [x] The "System Migration Policy" section in `CLAUDE.md` is deliberately general (no project-specific examples); no change needed. PROJ-281 archival notes will be added to auto-memory when the project closes rather than to `CLAUDE.md`

**Notes:** `CLAUDE.md` stays generic by design.

### Task 4.5: Final documentation verification [Simple]
**File:** N/A
**Tests:** N/A

- [x] Repo-wide grep: `BattleScreen.start(team` under `game/` → zero hits. Under `docs/` → only the PROJ-281 deletion announcement in `combat_simulation.md`. Under `tests/` → only the regex in the guard test + migration-history docstring in `test_make_minimal_spec.py` (both are forward-pointing, not callers). Under `Projects/` → PROJ-281 planning docs + archived PROJ-270/272 findings (historical, expected).
- [x] Repo-wide grep: `_build_fallback_outcome` under `game/` → zero hits. Under `docs/` → only the PROJ-281 deletion announcement. Elsewhere → archived planning docs only.
- [x] Repo-wide grep: "test-convenience shim" under `game/` → zero hits. Under `docs/` → only the PROJ-281 deletion announcement. Elsewhere → archived planning docs only.

**Notes:** Phase 4 complete. Every production-code + live-docs mention of the deleted shim/fallback has been updated. The remaining mentions are all in the PROJ-281 deletion announcement (intentional record of the change) or archived project history (historical record, immutable).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All doc references to the deleted shim + fallback are either removed or flipped to "deleted in PROJ-281"
- [x] `make_minimal_spec` helper is discoverable (documented in `tests/fixtures/README.md::battle.py`)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to "Awaiting archival"
