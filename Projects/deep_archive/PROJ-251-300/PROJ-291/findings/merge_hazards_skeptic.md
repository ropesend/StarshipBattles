# Cross-Project Merge Hazards (PROJ-289 ↔ PROJ-290) — Skeptical Audit

## Verdict

**MERGED STATE IS SEMANTICALLY SOUND WITH MINOR DOCUMENTATION GAPS.** All tests pass; kwargs compile; no runtime failures detected. However, the `view` parameter (PROJ-289's per-species habitability rendering) is preserved in the function signatures but is **never wired by PROJ-290's callers** (PlanetListWindow, EmpirePanelWindow), creating a **latent half-feature:** when PROJ-290's windows display uncolonized planets, they show the habitability-for-empire section (new PROJ-290 feature) but NOT the per-species detail sub-block (PROJ-289 feature) because `view=None` always. This is **intentional by PROJ-290's design** (it prioritizes habitability scoring over species breakdown for uncolonized planets), but the asymmetry between the `view` unconditional assignment and `empire`/`race_registry` None-sentinel fallback in `update_planet` creates unexpected behavior if callers later mix PROJ-289 and PROJ-290 semantics.

---

## Hazard Investigation

### Hazard 1: Asymmetric fallback semantics in `update_planet`

**Finding:** `PlanetReportPanel.update_planet()` applies two different update policies:
- `self.view = view` — **unconditional overwrite** (PROJ-289 policy)
- `if empire is not None: self._empire = empire` — **None-sentinel fallback** (PROJ-290 policy)
- `if race_registry is not None: self._race_registry = race_registry` — **None-sentinel fallback** (PROJ-290 policy)

**Scenario Analysis:**

If a caller constructs the panel with `view=None, empire=empire_1, race_registry=reg_1` for planet A (uncolonized), then navigates to planet B and calls `update_planet(planet_B, view=None)` WITHOUT passing `empire`/`race_registry` kwargs:
- `self.view = None` (unconditional) → no per-species sub-block rendered.
- `self._empire` stays `empire_1` and `self._race_registry` stays `reg_1` (reuse from construction).
- Renders habitability against `empire_1` for planet B.

**Correctness depends on:** whether the viewing empire changes during panel lifecycle. If the game supports hotseat or empire-switching, and a new empire takes over without reconstructing the panel, the panel will render habitability against the **wrong empire** for the new planet. This is **not currently a bug** because PROJ-290's wiring (PlanetListWindow._on_planet_selected, EmpirePanelWindow) always passes both kwargs together or neither, maintaining empire consistency. But the asymmetry violates the principle of least surprise: developers may later call `update_planet(planet, view=None)` expecting a "clear overrides" behavior.

**Severity:** Minor (by design; PROJ-290's callers don't trigger the hazard).

---

### Hazard 2: Positional-argument migration risk (low risk, mitigated by tests)

**Finding:** `format_planet_info` signature has `view` as optional positional parameter. If legacy code ever passed a non-view second positional argument, it would bind to `view` and corrupt rendering.

**Mitigation:** Grep of all callers shows only keyword usage across tests, panels, and PlanetListWindow. No unsafe positional calls found. Signature is backward-compatible.

**Severity:** None (mitigated by exhaustive grep + test coverage).

---

### Hazard 3: Resource grid routing inconsistency (actually coherent)

**Finding:** `PlanetReportPanel._build_resource_grid()` checks `if view is not None` to render PROJ-289's projection grid; otherwise uses legacy stockpile grid. PROJ-290's PlanetListWindow passes `empire` + `race_registry` but NO `view`, so it always renders the legacy grid.

**Correctness:** This is **intentional by design.** PROJ-289 targets detailed colony management; PROJ-290 targets uncolonized habitability scoring. An uncolonized planet has no `view` DTO, so the legacy grid is appropriate. **No hazard.** Both features display correctly; the split is clean.

**Severity:** None (correct behavior).

---

### Hazard 4: Test fixture drift (fixture is consistent)

**Finding:** `test_strategy_detail_fmt.py` mock_planet defaults to `owner_id = None` (uncolonized). PROJ-289 tests override locally; PROJ-290 tests depend on the default. Both sections concatenated in the file.

**Verification:** No conflicts. Fixtures are isolated per test method via pytest scoping.

**Severity:** None.

---

### Hazard 5: Docs merge coherence (both sections present)

**Finding:** `docs/systems/strategy_layer.md` contains both PROJ-289 and PROJ-290 subsections in dependency order. No stale phrasing found. Cross-references are consistent.

**Severity:** None (docs are accurate).

---

### Hazard 6: Merge resolution method (octopus merge, clean)

**Finding:** Git resolved the merge as an octopus merge (true merge, not rebase). Both `strategy_detail_fmt.py` and `planet_report_panel.py` were modified by both projects. Git found no text conflicts because changes are additive.

**Semantic correctness:** The function signature `format_planet_info(planet, view=None, *, empire=None, race_registry=None)` correctly preserves both features:
- PROJ-289: `view` parameter and per-species sub-block logic.
- PROJ-290: `empire`/`race_registry` parameters and uncolonized habitability logic.

Both code paths are correct and independent.

**Severity:** None (merge is semantically sound).

---

## Findings

### Finding 1: Asymmetric update semantics in `update_planet` (documentation gap)
**Severity:** Minor  
**Location:** `game/ui/panels/planet_report_panel.py` lines 273–281  
**What's wrong:** `self.view = view` (unconditional) vs. `if empire is not None: self._empire = empire` (fallback). The contract is not documented.  
**Evidence:** The two update styles are inconsistent; the docstring (lines 257–269) explains `view` but not the None-sentinel fallback for `empire`/`race_registry`.  
**Recommended fix:** Add a docstring note documenting the None-sentinel fallback contract.

### Finding 2: PlanetListWindow never passes `view` to PlanetReportPanel (latent feature, by design)
**Severity:** Minor (intentional)  
**Location:** `game/ui/screens/planet_list_window.py` lines 511–521  
**What's wrong:** PROJ-289's `view` parameter is part of the panel's public API but is never used by PROJ-290's PlanetListWindow. The per-species demographic sub-block never renders in the list window.  
**Evidence:** The panel is created with explicit `empire=` and `race_registry=` kwargs but no `view=` kwarg.  
**Recommended fix:** Not a bug; no action needed. If colonized-planet views are threaded later, the feature is ready.

---

## False Positives

- "view kwarg never passed from PlanetListWindow" — By design; uncolonized planets have no `view` DTO.
- "Test fixture has owner_id=None" — Correct default; PROJ-289 tests override locally.
- "No view in resource grid" — By design; uncolonized planets use the legacy stockpile grid.

---

## Summary

The merged state compiles, 89/89 tests pass, and both PROJ-289 and PROJ-290 features activate correctly in their respective contexts. The only latent semantic hazard is the **asymmetric fallback semantics in update_planet**, which is mitigated by PROJ-290's consistent kwargs-passing discipline. Documentation could be slightly improved to clarify the None-sentinel contract, but the code is not broken.

**Risk Level:** Very Low.
