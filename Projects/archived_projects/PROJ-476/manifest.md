# PROJ-476 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.
>
> NOTE: PROJ-476 is import-guard-only. The ONLY production-ish files touched are
> the static guard and the policy doc. NO `game/ui/` production code is modified
> (no session reads to migrate). The tooling-screen files below are listed only
> as the SUBJECTS of allowlist triples, not as files to edit.

## Files

| File | Type | Notes |
|------|------|-------|
| `tests/static_guards/test_facade_read_path_imports_guard.py` | Test/Guard | **PRIMARY.** Add `_TOOLING_EXEMPTIONS` category + no-misfile invariant test + positive-control test; move tooling residue triples out of the `TAIL` comment block into it. Phase 2/3. |
| `docs/02_PATTERNS.md` (Pattern #5) | Doc | Add the tooling-exemption policy paragraph (what qualifies, exact-triple scoping, no folder waivers). Phase 3. |
| `tests/static_guards/test_facade_read_path_session_guard.py` | Test/Guard | **UNCHANGED** — verified zero tooling-dir session reads. Listed for explicit no-touch. |
| `game/ui/screens/design_selector_window.py` | Production | **Phase 4 (Codex exec-audit F1).** ONLY production edit: moved the annotation-only `DesignCatalog` import under `TYPE_CHECKING` (PEP 563 — no runtime use) + docstring fix. Behavior-neutral; dropped its tooling-exemption triple. |

## Conflict map (overlap with sibling projects — all upstream, all must land first)

| Project | Shared file | Conflict risk | Resolution |
|---------|-------------|---------------|------------|
| PROJ-474 | `test_facade_read_path_imports_guard.py` (`_UISAFE_SYMBOLS`) | HIGH — same guard file | 474 lands first; 476 builds the `_TOOLING_EXEMPTIONS` category ALONGSIDE the post-474 `_UISAFE_SYMBOLS`. Phase 1 re-inventory reconciles. No-misfile test enforces disjointness. |
| PROJ-474 | `docs/02_PATTERNS.md` (Pattern #5) | MEDIUM — same doc section | 474 adds the UI-safe token list; 476 appends a separate tooling-exemption paragraph. Sequential (474 first). |
| PROJ-475 / 477 | `test_facade_read_path_imports_guard.py` (`TAIL`/`CLUSTER`/`FLEETCAP`) | MEDIUM — same allowlist | 475/477 remove live-reader entries; 476 then operates on the smaller residual `TAIL`. Re-inventory in Phase 1 reflects their removals. |
| PROJ-475 | `build_queue_panel_factory.py` (`compute_planet_production`) | NONE for 476 | Explicitly OUT of 476 (live build-queue). 475 owns it. |

## Subject files (allowlist triple targets — NOT edited by PROJ-476)

| File | Category | Symbols (2026-05-22 snapshot — RE-VERIFY) |
|------|----------|-------------------------------------------|
| `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` | prebattle-editor | `ShipInstance`, `Squadron`, `TaskForce` |
| `game/ui/screens/battle_setup_state.py` | prebattle-editor | `Fleet`, `ShipInstance` |
| `game/ui/screens/galaxy_test/galaxy_mode.py` | sandbox-harness | `Galaxy`, `DensityMap`, `GalaxyLayoutsLoader`, `DensityBasedPlacementStrategy`, `RandomPlacementStrategy` |
| `game/ui/screens/galaxy_test/system_mode.py` | sandbox-harness | `Planet`, `PlanetGenerator`, `MASS_EARTH`, `calculate_escape_velocity`, `calculate_surface_gravity`, `StarSystem`, `Star`, `StarGenerator`, `SystemBlueprintsLoader`, `PlanetImageRegistry` |
| `game/ui/screens/race_setup/controller.py` | race-authoring | `RaceLibrary`, `RaceRandomizer` |
| `game/ui/screens/race_setup/screen.py` | race-authoring | `RaceLibrary`, `RaceRandomizer` (test re-export seam) |
| `game/ui/screens/race_setup/panel_factory.py` | race-authoring | `RaceCaptionLoader`, `RaceDescriptionLLMController` |
| `game/ui/screens/builder/right_panel.py` | design-editor | `get_default_design_role_registry` |
| `game/ui/screens/design_selector_window.py` | design-editor | `get_default_design_role_registry` (`DesignCatalog` moved to TYPE_CHECKING in Phase 4 — no exemption) |
| `game/ui/screens/workshop_event_router.py` | design-editor | `get_default_design_role_registry` |
