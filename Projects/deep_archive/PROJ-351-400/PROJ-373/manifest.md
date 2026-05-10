# PROJ-373 File Manifest

> Generated during project scaffolding. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files modified or created

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/ui/panels/build_queue_controller.py` | Production (modify) | 1 | Add `_validation_cache: Dict[str, Tuple[Any, bool]]` and `_design_fingerprint(design_id)` helper. Modify `_validate_designs` to check cache before validating; store result on miss. Add `reset_filters()` (Phase 2 prerequisite) — sets `selected_category="complex"`, `selected_role="Any"`. |
| `game/strategy/services/design_validator.py` | Production (read-only) | 1 | No changes; the cache lives on the controller. Listed for context only. |
| `game/strategy/systems/design_library.py` | Production (read-only) | 1 | No changes if mtime-based keying is used. If we switch to a generation-counter approach, `save_design` (line 184) would bump the counter. |
| `game/ui/screens/strategy_build_queue_manager.py` | Production (modify) | 2 | Eliminate the 3 `BuildQueueScreen(...)` construction sites at lines 100, 213, 257. Replace with `self._screen.build_queue_screen.open_for_yard(planet)`. Replace close-callback nulling at line 116 with hide. Construct the screen once in `__init__` (or lazy on first click). Remove the 3 entry guards (lines 74-76, 186-188, 232-234). |
| `game/ui/screens/build_queue_screen.py` | Production (modify) | 2 | Split `__init__` (line 48) into "construct shell" (UI-shell state) + new `open_for_yard(yard)` (yard-specific state refresh + show). Add `hide()` / `show()` methods. Replace `_close()` (line 639) — instead of `panels.background.kill()` + `manager.update(0)` + nulling, just hide. Yard-switch logic in `open_for_yard` resets `build_context`, `hex_coord`, `queue_sources`, `active_queue_source`, `selected_queue_indices`, `selected_queue_index`, `planet_selection_window`. Detect context-type transitions (planet ↔ fleet) and call panel rebuild only on those. |
| `game/ui/screens/build_queue_drag_handler.py` | Production (modify) | 2 | Add `reset_state()` method that clears `dragged_item`, `drag_start_pos`, `selected_design` (lines 74-81). Called from `BuildQueueScreen.open_for_yard`. |
| `game/ui/components/table/virtual_table.py` | Production (modify) | 3 | Cache last-seen `(panel_height, row_height)` in `__init__`. Modify the rebuild path so `_rebuild_row_pool` only fires when those values change. Confirm `update_visible_rows` re-binds row content on data change (read-only verification — likely already correct). |
| `data/builder_theme.json` | Data (modify) | 4 | Edit the `panel` block (lines 60-70): change `"shape": "rounded_rectangle"` (line 67) to `"shape": "rectangle"`. Drop or zero out `shape_corner_radius` line for clarity. |
| `game/ui/screens/build_queue_panel_factory.py` | Production (modify — Phase 4b only) | 4 | Only if Phase 4a's global change causes a visible regression somewhere. Scoped fallback: pass `object_id={"object_id": "@build_queue_panel"}` (or class_id) to each UIPanel construction in the factory; add the matching theme entry. |
| `tests/unit/ui/panels/test_build_queue_controller.py` | Test (modify) | 1 | Add tests: cache hit returns same result without calling validator; cache miss calls validator and stores result; mtime change invalidates a single entry; exception during validate doesn't poison cache; cache survives category-switch within one controller. |
| `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` | Test (new) | 2 | New test module: `BuildQueueScreen` constructed once and reused across opens; yard switch resets selection state; planet→fleet transition triggers panel rebuild; planet→planet transition does not; drag handler state cleared on open; hide/show toggles `panels.background.visible` without killing it. |
| `tests/unit/ui/components/table/test_virtual_table.py` | Test (modify) | 3 | Add tests: `_rebuild_row_pool` is NOT called when `set_queue` runs with same panel dimensions; `_rebuild_row_pool` IS called when panel dimensions change. |
| `tests/unit/ui/screens/test_build_queue_replay_button.py` | Test (read-only check) | 2 | Existing test (referenced in repo `git status`); verify it still passes after Phase 2's lifecycle change. May need an update if it asserts on construction count. |
| `Tools/profile_game/profile_game.py` | Tool (read-only) | — | Used to capture before/after profiles. Already exists. |
| `findings/profile_summary.md` | Project doc (already created) | — | Originating profile evidence. |
| `findings/01_lifecycle_research.md` | Project doc (already created) | — | Build-queue UI lifecycle research from Explore subagent. |
| `findings/02_drawable_cost_research.md` | Project doc (already created) | — | pygame_gui rounded-rect cost research from Explore subagent. |
