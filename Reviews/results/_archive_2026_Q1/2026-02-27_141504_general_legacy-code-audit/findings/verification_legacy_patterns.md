# Skeptical Verification Report: Legacy Patterns & Tech Debt

**Reviewer:** Verification Agent (Skeptical)
**Date:** 2026-02-27
**Scope:** Independent verification of 6 findings from legacy code audit

---

## Finding SIM-001: Module Identity Drift Fallback in AbilityManager

**Original Claim:** `game/simulation/components/ability_manager.py:58-66` has a fallback for test module reloading that uses `__name__` string matching when `isinstance()` fails.

**Verification Result:** CONFIRMED

**Evidence:** The code at lines 58-66 is exactly as described:

```python
# [KNOWN_ISSUE] Fallback for Module Identity Drift in tests.
# When test modules reload ability classes, isinstance() fails due to
# different class objects. This __name__ check provides test isolation.
# Ref: Phase 2 Task 2.5 audit - documented as intentional tech debt.
else:
    for cls in ab.__class__.mro():
        if cls.__name__ == ability_name:
            found.append(ab)
            break
```

The fallback is well-documented with a `[KNOWN_ISSUE]` tag and a reference to the Phase 2 audit where this was flagged. The comment explains the exact scenario: test module reloading creates different class objects with the same name, causing `isinstance()` to fail.

However, the fallback has a subtle architectural problem: it runs on **every** non-matching ability, not just when `isinstance()` fails for the target class. Line 56 checks `if target_class and isinstance(ab, target_class)`, and if that fails (which it will for any ability that is NOT of the requested type), the else branch walks the MRO. This means the MRO walk happens for every non-matching ability in normal production use, not just during test module reloading. It is a performance concern, not a correctness concern, since the MRO walk will correctly not match for unrelated abilities.

**Risk of Fix:** Removing the fallback could break tests that use module reloading or pytest-xdist parallel execution if class identity drifts. The safe approach would be to restructure the logic so the MRO fallback only triggers when `target_class` is None (i.e., the registry entry is not a type), rather than as a catch-all else branch.

**Recommendation:** MODIFY APPROACH

**Reasoning:** The issue is real but the fix is not simply "remove the fallback." The code structure could be improved to only use the MRO fallback when `target_class` is None (registry lookup failed) rather than as a catch-all. This would preserve the safety net for edge cases while eliminating unnecessary MRO walks in the common path. A targeted restructure of the if/else logic would be a clean improvement:

```python
for ab in instances:
    if target_class and isinstance(ab, target_class):
        found.append(ab)
    elif not target_class:
        # Fallback: string-based match only when registry has no class
        for cls in ab.__class__.mro():
            if cls.__name__ == ability_name:
                found.append(ab)
                break
```

---

## Finding SIM-002: Inconsistent Fallback in load_components()

**Original Claim:** `game/simulation/components/component.py:558-596` uses a cache fallback pattern inconsistent with PROJ-50 strict DI.

**Verification Result:** PARTIALLY CONFIRMED

**Evidence:** The `load_components()` function at line 558 is a wrapper that:
1. Gets the `ComponentCacheManager` singleton (line 568)
2. Gets the default registry provider (line 569)
3. Checks the cache for a hit by comparing `file_path` (lines 573-576)
4. On cache miss, creates a `GameRegistries` from the default provider (lines 579-584)
5. Calls the pure `load_components_data()` function (line 585)
6. Populates the cache and registry (lines 590-595)

The pure function `load_components_data()` (line 483) properly accepts an optional `registries` parameter and creates registries from the default provider if None. This IS consistent with PROJ-50 DI -- it provides a DI entry point while also supporting a convenience default.

What IS inconsistent is the `load_components()` wrapper itself, which:
- Uses a singleton cache manager (`ComponentCacheManager.instance()`)
- Mutates the global registry via `provider.get_components()` dict
- Has no DI parameter for the cache or provider

But this is the **legacy entry point** -- it wraps the pure function for backward compatibility. The pure function (`load_components_data`) is properly designed for DI. The wrapper exists because `app.py:116` and `workshop_data_loader.py:138` call `load_components()` directly.

**Risk of Fix:** Removing or refactoring `load_components()` would require updating `app.py`, `registry_loader.py`, and `workshop_data_loader.py` to use the pure function directly with explicit registry injection. Not high risk but multiple call sites.

**Recommendation:** KEEP (low priority cleanup)

**Reasoning:** The original claim overstates the problem. The `load_components_data()` pure function is properly DI-compliant. The wrapper `load_components()` is a convenience function for production use where the global registry is the intended target. This is a common pattern (pure core + convenience wrapper) and is not really "inconsistent" -- it is a deliberate two-tier design. The cache is also a reasonable optimization, not a DI violation. If anything, the wrapper could be documented more clearly as the "production convenience" entry point vs. the pure function for testing/DI.

---

## Finding AIR-002: Global State Mutation in exit_dialog.py

**Original Claim:** `game/exit_dialog.py` uses module-level globals for button rects, mutated during rendering.

**Verification Result:** CONFIRMED (but not worth fixing)

**Evidence:** The file is exactly 102 lines with:
- Two module-level globals: `_exit_yes_rect = None` and `_exit_no_rect = None` (lines 9-10)
- `draw_exit_dialog()` mutates them via `global` keyword (line 22, lines 51 and 64)
- `handle_exit_dialog_click()` and `handle_exit_dialog_cancel()` read them (lines 84, 99)

The file is a small, self-contained utility with 3 functions. The globals are underscore-prefixed (private convention) and the pattern is: render sets the rects, click handlers read them. This is a valid "render then query" pattern common in immediate-mode UI.

**Risk of Fix:** Converting to a class would add boilerplate with zero functional benefit. The file has exactly one consumer (`game/app.py`, which imports all three functions). There is no concurrency concern, no testing concern (the globals are only meaningful during an active render frame), and no complexity concern (102 lines).

**Recommendation:** KEEP

**Reasoning:** This is textbook "code smell in a tiny utility file" that is not worth fixing. The globals are private, the file is small, the pattern is standard for Pygame immediate-mode UI, and there is exactly one consumer. Refactoring this to a class would add 15-20 lines of boilerplate (`__init__`, `self.` references) for zero maintainability improvement. The original finding identifies a real pattern but fails to consider the cost-benefit ratio. Not all code smells warrant action.

---

## Finding AIR-001: Test-Only AI Behaviors in Production Code

**Original Claim:** `game/ai/behaviors.py:405-483` has `StraightLineBehavior`, `RotateOnlyBehavior`, `ErraticBehavior` that are test-only.

**Verification Result:** DISPUTED

**Evidence:** The behaviors ARE explicitly categorized under a `# TEST-SPECIFIC BEHAVIORS` section header (line 405-407), and the module docstring lists them under "Test/Debug Behaviors" (lines 44-49). However:

1. **They are instantiated in every `AIController`** (controller.py:83-89). Every ship in every battle creates instances of all 6 test behaviors.

2. **They are referenced by string key in strategy data.** The behavior dict keys (`'do_nothing'`, `'stationary_fire'`, `'straight_line'`, `'rotate_only'`, `'erratic'`) are strategy-selectable behaviors. The `AIController.update()` method sets the current behavior based on the strategy's `behavior` field. This means any AI strategy JSON can reference these behaviors.

3. **They have legitimate gameplay uses.** The comment in controller.py even hints at this: `"stationary_fire: Don't move, just fire (for testing/satellites)"`. A stationary defense platform, a debris field drifting in a straight line, an erratic evasion maneuver -- these are all valid gameplay behaviors, not just test utilities.

4. **Extensive test usage.** 35 test files and 60 simulation test files reference these behaviors. Removing them from production code would require a parallel definition in test infrastructure.

5. **No production JSON data files reference them.** A search of `data/*.json` found no references to these behavior keys. They are only referenced in test data files (`tests/unit/data/`, `simulation_tests/data/`).

**Risk of Fix:** Moving these to a test-only module would require:
- Conditional imports or a plugin system in `AIController`
- Duplication of behavior classes in test infrastructure
- Changes to 95+ test files
- Loss of the ability to use these behaviors for future gameplay features (defense platforms, scripted encounters, tutorials)

**Recommendation:** KEEP (relabel from "test-only" to "utility behaviors")

**Reasoning:** The original claim that these should be extracted to test-only code is wrong. They are general-purpose movement behaviors that happen to be primarily used in tests today. Moving them would add significant complexity to the test infrastructure and close off legitimate future gameplay uses. The correct action is to rename the section header from "TEST-SPECIFIC BEHAVIORS" to "UTILITY BEHAVIORS" and update the docstring, since their current labeling is misleading. They are simple, well-tested, low-maintenance code in the right location.

---

## Finding UIS-003: Duplicate Formatter Modules

**Original Claim:** `game/ui/screens/strategy_detail_fmt.py` (393 lines) and `game/ui/screens/strategy_detail_formatter.py` (422 lines) are "nearly identical."

**Verification Result:** DISPUTED -- These are NOT duplicates

**Evidence:** These are two deliberately different modules with a clear relationship:

**`strategy_detail_fmt.py`** (394 lines) is a **pure function library**:
- Contains standalone formatting functions: `format_spectrum_html()`, `format_atmosphere_raw()`, `format_planet_info()`, `format_star_system_info()`, `format_star_info()`, `format_fleet_info()`, `get_label_for_object()`
- Helper functions: `_format_ship_groups()`, `_format_cargo_summary()`, `_format_orders()`
- No class, no state, no Pygame dependency (except protocol imports)
- Imported by: `strategy_detail_formatter.py`, `planet_report_panel.py`, tests

**`strategy_detail_formatter.py`** (422 lines) is a **stateful UI controller class**:
- Contains `StrategyDetailFormatter` class (PROJ-86 extraction from strategy_ui.py)
- Manages Pygame widgets (portrait, detail text, graph, buttons)
- Holds state (current_selection, current_raw_data, planet_report_panel)
- **Imports from `strategy_detail_fmt.py`** (line 21-24) and delegates to it
- Has UI-specific methods: `show_detailed_report()`, `show_raw_data_popup()`, `_show_planet_report()`
- Imported by: `strategy_ui.py`, tests

The relationship is clear: `strategy_detail_fmt.py` is the **formatting utility layer** and `strategy_detail_formatter.py` is the **UI controller** that uses those utilities. The formatter class has its own formatting methods (e.g., `_format_star_system()` at line 243) that duplicate some content from `strategy_detail_fmt.py` -- specifically the star system and star info formatting. This is because the class version also manages graph widgets and button visibility alongside the text formatting.

There IS minor duplication in `_format_star_system()` and `_format_star()` within the class, which could call the pure functions instead. But the files themselves serve completely different purposes.

**Risk of Fix:** N/A -- the files are not duplicates. Trying to "merge" them would conflate a pure function library with a stateful UI controller.

**Recommendation:** MODIFY APPROACH -- Minor dedup only

**Reasoning:** The original claim is wrong: these are not duplicate files. They are a utility module and a controller that uses it. The only actionable item is that `_format_star_system()` and `_format_star()` in the class could delegate to the existing pure functions `format_star_system_info()` and `format_star_info()` rather than re-implementing the text formatting inline, which would remove ~20 lines of actual duplication. But this is a minor cleanup, not the "nearly identical" merge the original finding suggests.

---

## Finding AIR-006: Research System Disconnected

**Original Claim:** `game/research/` is a functional prototype completely disconnected from the game.

**Verification Result:** DISPUTED

**Evidence:** The research system is NOT disconnected from the game. It is actively integrated:

1. **Main menu entry**: `game/app.py:175` adds "Research Tree" to the main menu.
2. **Scene management**: `game/app.py:406-420` has `start_research_tree()` and `on_research_tree_return()` methods that create `ResearchTreeScene` and manage transitions.
3. **GameState enum**: `game/core/constants.py:34` defines `RESEARCH_TREE = 8` as a valid game state.
4. **Input handling**: `game/app.py:672` handles input routing for `RESEARCH_TREE` state.
5. **UI layer**: `game/ui/research/` contains three modules (`research_scene.py`, `research_renderer.py`, `research_controls.py`) that form a complete UI layer using `game.research` data classes.
6. **Extensive test coverage**: Unit tests in `tests/unit/research/` and integration tests in `tests/integration/research_workflow/` cover the system thoroughly.

The `__init__.py` docstring describes it as "a standalone sandbox for testing tech tree balance," which is accurate -- it IS a sandbox/prototype accessible from the main menu. But "sandbox" does not mean "disconnected." It means it is a self-contained game mode, similar to a Combat Lab.

What IS true: the research system does not integrate with the strategy layer's turn engine or galaxy gameplay loop yet. You cannot research tech that affects your empire's production or combat. In that sense, it is an isolated prototype feature -- but it is a **shipped, accessible, tested** isolated prototype feature, not dead code.

**Risk of Fix:** Removing or flagging `game/research/` as experimental could break:
- The main menu "Research Tree" option
- 50+ unit and integration tests
- The UI layer in `game/ui/research/`

**Recommendation:** KEEP

**Reasoning:** The original claim dramatically overstates the issue by calling it "completely disconnected." The system is reachable from the main menu, has a full UI, and has extensive tests. It is a standalone sandbox feature (like Combat Lab) that is not yet integrated into the strategy game loop. This is a feature-completeness gap, not a technical debt issue. The correct action is to document it as "standalone sandbox -- not yet integrated into strategy gameplay" rather than treating it as dead code to be removed or flagged.

---

## Summary Table

| Finding | Verdict | Recommendation | Priority |
|---------|---------|---------------|----------|
| SIM-001 | CONFIRMED | Restructure if/else to limit MRO fallback scope | Low |
| SIM-002 | PARTIALLY CONFIRMED | Keep as-is; two-tier design is intentional | None |
| AIR-002 | CONFIRMED (not actionable) | Keep; cost exceeds benefit for 102-line file | None |
| AIR-001 | DISPUTED | Relabel section header; keep behaviors in production | Trivial |
| UIS-003 | DISPUTED | Minor dedup of ~20 lines; files are NOT duplicates | Low |
| AIR-006 | DISPUTED | Document as standalone sandbox; it IS connected | None |

**Overall Assessment:** Of the 6 findings, only SIM-001 warrants a code change (restructuring the if/else logic). AIR-001 and UIS-003 have trivial improvements available (relabeling a comment, deduplicating ~20 lines). The remaining 3 findings are either non-issues or not worth the effort to fix. The original audit significantly overstated the severity of most findings.
