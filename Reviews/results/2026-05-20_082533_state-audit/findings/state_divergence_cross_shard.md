# Cross-Shard Divergence Report

## Summary
- **Singletons Analyzed:** 14
- **High Divergence Risk:** 1 (CRITICAL)
- **Medium Risk:** 8 (MAJOR)
- **Low Risk:** 5 (MINOR)

---

## Singleton Divergence Risk Map

### CRITICAL: `_default_provider` (DefaultRegistryProvider) — `game/core/registry.py:466`

- **Module-level call sites:** 68+ across all layers
  - Core: `registry.py:133,376,469` + `registry_cache.py:59` — (4 get_default)
  - Strategy: `game_session.py:165`, `simulation_adapter.py:52`, `component_layers.py:53` — (3 get_default)
  - UI: `screen_router.py:508`, `app.py:383`, `app_bootstrap.py:217`, `workshop_data_loader.py:128,204`, `battle_setup/controller.py:48`, `test_lab/screen_actions.py:171`, `design_selector_window.py:411,427`, `strategy_fleet_command_router.py:270`, etc. — (~50 get_default)
- **ctx.xxx accesses:** 0 (not ctx-wired — no `ctx.provider` field exists)
- **Setter coverage:** NO SETTER FUNCTION. `get_default_registry_provider()` auto-creates a `DefaultRegistryProvider` on first access via `registry.py:469-478`.
- **Mutable:** No (reference), but wraps `RegistryManager` which holds mutable registries
- **Risk:** Widely used across 4+ layers with no ctx binding and no formal setter. The auto-create path in `get_default_registry_provider()` can produce a provider that diverges from the `RegistryManager` held by `ctx.registry_manager` if called before `create_production()` hydrates both. Only `set_default_registry_manager()` (line 175) is called in `create_production()` — the `DefaultRegistryProvider` is a separate layered abstraction over `RegistryManager` with no synchronization. Any consumer calling `get_default_registry_provider()` before `GameRegistries` is built via `ctx.registry_manager` will get a provider referencing a different (default-constructed) `RegistryManager` instance.
- **Recommendation:** Add `ctx.registry_provider` to `ApplicationContext` (or bind `DefaultRegistryProvider` through `create_production()`). Add `set_default_registry_provider()` and call it in `create_production()`, or eliminate the module-level default entirely and require explicit DI everywhere (preferred per architecture doc: "Simulation-layer code does not call global registry accessors").

---

### MAJOR: `_default_policy_manager` — `game/ai/policy_manager.py:23`

- **Module-level call sites:** 3
  - AI: `ai/controller.py:125` — (1 get_default)
  - UI: `ui/screens/workshop_data_loader.py:107,179` — (2 get_default)
- **ctx.xxx accesses:** 0 (ctx.policy_manager exists but never accessed in live code)
- **Setter coverage:** NO SETTER FUNCTION. create_production() line 190 assigns directly: `_pm_module._default_policy_manager = policy_manager`
- **Mutable:** No (reference)
- **Risk:** Lacking a `set_default_policy_manager()` function, create_production() bypasses the convention with a raw module-attribute assignment. The singleton auto-creates on first access via `get_default_policy_manager()` (line 36) — if called before create_production(), it creates a fresh `PolicyManager()` that diverges from `ctx.policy_manager`.
- **Recommendation:** Add `set_default_policy_manager()` function. Wire it in create_production() line 190. Consider migrating AI call sites to accept `PolicyManager` via constructor injection.

---

### MAJOR: `_default_cache_manager` — `game/simulation/components/component_loader.py:37`

- **Module-level call sites:** 4
  - Simulation: `component_loader.py:156,255`, `component.py:397` — (4 get_default)
- **ctx.xxx accesses:** 0 (ctx.component_cache exists but never accessed)
- **Setter coverage:** NO SETTER FUNCTION. create_production() line 188 assigns directly: `_ccm_module._default_cache_manager = component_cache`
- **Mutable:** No (reference, but wraps mutable caches)
- **Risk:** Same pattern as `_default_policy_manager` — no formal setter, direct attribute assignment. Auto-creates on first access (line 50), creating a divergence window before `create_production()`. `reset_component_caches()` (line 69) directly reassigns `_default_cache_manager` without going through any ctx synchronization path — so `reset_component_caches()` creates divergence between the module-level and `ctx.component_cache` that never resolves.
- **Recommendation:** Add `set_default_cache_manager()` function. Wire it in create_production() line 188. Make `reset_component_caches()` call `set_default_cache_manager()` (once it exists) to maintain ctx sync.

---

### MAJOR: `_default_asset_manager` — `game/assets/asset_manager.py:14`

- **Module-level call sites:** 7
  - UI: `strategy_renderer.py:89`, `planet_selection_window.py:207`, `strategy_screen_assets.py:47,58`, `star_data_source.py:56`, `planet_data_source.py:84`, `strategy_detail_fmt.py:429` (via registry_manager) — (7 get_default)
- **ctx.xxx accesses:** 0
- **Setter coverage:** `set_default_asset_manager()` (line 371), called in create_production() line 179. Only caller in production code.
- **Mutable:** No (reference, but wraps image caches)
- **Risk:** ctx-wired but 100% of callers use module-level accessor. The setter is a bridge mechanic whose only production caller is create_production(). If any code path sets `ctx.asset_manager` without also calling `set_default_asset_manager()`, the instances diverge.
- **Recommendation:** Migrate UI call sites to `ctx.asset_manager` where ctx is available, or accept the module-level pattern and remove ctx.asset_manager as dead-weight.

---

### MAJOR: `_default_sprite_manager` — `game/ui/renderer/sprites.py:14`

- **Module-level call sites:** 2
  - UI: `workshop_screen.py:109` — (1 get_default)
  - App bootstrap: `app_bootstrap.py:265` — (1 get_default)
- **ctx.xxx accesses:** 0
- **Setter coverage:** `set_default_sprite_manager()` (line 122), called in create_production() line 180. Only caller in production code.
- **Mutable:** No (reference, but wraps sprite dict)
- **Risk:** Same pattern as `_default_asset_manager`. ctx-wired but unused. `app_bootstrap.py:265` calls `get_default_sprite_manager()` even though `ctx` is in scope — this is the canonical example of dual-pattern coexistence in the same file.
- **Recommendation:** `app_bootstrap.py:265` should use `ctx.sprite_manager` since `ctx` is already in scope. Migrate `workshop_screen.py` once ctx is threaded through.

---

### MAJOR: `_default_ship_theme_manager` — `game/ui/assets/ship_theme_manager.py:54`

- **Module-level call sites:** 15
  - UI: `fleet_data_source.py:296`, `ship_detail_panel.py:297`, `race_summary_panel.py:641`, `build_queue_portraits.py:123`, `workshop_screen.py:112`, `race_theme_gallery.py:132`, `race_browser_dialog.py:167`, `race_asset_loader.py:237`, `race_setup/ship_preview.py:60`, `design_image_helper.py:75`, `builder/right_panel.py:272`, `game_renderer.py:76`, `design_report_panel.py:178` — (15 get_default)
- **ctx.xxx accesses:** 0
- **Setter coverage:** `set_default_ship_theme_manager()` (line 450), called in create_production() line 181. Only caller in production code.
- **Mutable:** No (reference, but wraps theme caches with threading locks)
- **Risk:** Most heavily used get_default singleton. ctx-wired but 100% of 15 call sites use module-level accessor. The setter is a pure bridge mechanic.
- **Recommendation:** Highest-priority migration target. Thread ctx through UI component constructors (screen_router.py passes ctx to scenes). This is the biggest contributor to the get_default count in the UI layer.

---

### MAJOR: `_default_llm_provider` — `game/services/llm/defaults.py:17`

- **Module-level call sites:** 1
  - UI: `race_setup/panel_factory.py:167` — (1 get_default)
- **ctx.xxx accesses:** 0 (ctx.llm_provider exists but never accessed)
- **Setter coverage:** `set_default_llm_provider()` (line 31), called in create_production() line 183. Only caller in production code.
- **Mutable:** No (reference)
- **Risk:** ctx-wired but unused. Only one module-level consumer. The setter is a pure bridge mechanic.
- **Recommendation:** Migrate `panel_factory.py:167` to `ctx.llm_provider`. Then `set_default_llm_provider` becomes stale and can be removed.

---

### MAJOR: `_default_manager` (RegistryManager) — `game/core/registry.py:284`

- **Module-level call sites:** 9
  - Core: `registry.py:324,336,345,360,382,386,390,394` — (8 get_default)
  - UI: `strategy_detail_fmt.py:429` — (1 get_default)
- **ctx.xxx accesses:** 2
  - App bootstrap: `app_bootstrap.py:229,245` — (2 ctx.registry_manager)
  - Core: `registry.py:133` — (1 ctx.registry_manager in TestRegistryProvider)
- **Setter coverage:** `set_default_registry_manager()` (line 287), called in create_production() line 175. Also invalidates registry cache.
- **Mutable:** No (reference, but wraps mutable registries and auto-creates on first access)
- **Risk:** Both patterns coexist within the same layer (Core). The auto-create path in `get_default_registry_manager()` (line 314: `if _default_manager is None: _default_manager = RegistryManager()`) creates a divergence window. `freeze_registry()`, `set_validator()`, `clear()`, and the `DefaultRegistryProvider` all route through the module-level accessor regardless of what `ctx.registry_manager` holds. The 8 module-level sites in `registry.py` itself mean this singleton's design is still primarily module-level.
- **Recommendation:** The module-level wrappers (`freeze_registry`, `set_validator`, `get_validator`, `clear`) are convenience functions that should route through `ctx.registry_manager` when available. Add a `ctx`-aware path or accept this as an intentional bridge pattern for convenience.

---

### MINOR: `_default_profiler` — `game/core/profiling.py:17`

- **Module-level call sites:** 0 (getter returns None if not set — no auto-create)
- **ctx.xxx accesses:** 22+
  - App: `app.py:527` — (1 ctx.profiler)
  - App bootstrap: `app_bootstrap.py:150,151,174,180,190,192,198,204,218,220,227,239,244,257,264,269,279,300,326` — (19 ctx.profiler)
  - Run loop: `run_loop.py:136,218` — (2 ctx.profiler)
- **Setter coverage:** `set_default_profiler()` (line 25), called in create_production() line 176. Only caller in production code. However `get_default_profiler()` does NOT auto-create — returns None if not set.
- **Mutable:** No (reference)
- **Risk:** LOW. This is the most successfully ctx-migrated singleton. All production call sites use `ctx.profiler`. The module-level getter is intentionally bare (no auto-create) to force DI. The setter is a bridge mechanic that could be removed once `get_default_profiler` usage hits zero.
- **Recommendation:** Reference implementation for other singletons. The setter can be removed after verifying zero module-level consumers.

---

### MINOR: `_default_game_settings` — `game/ui/services/game_settings.py:22`

- **Module-level call sites:** 0 (no consumers found outside definition)
- **ctx.xxx accesses:** 0 (no consumers found outside ctx init)
- **Setter coverage:** `set_default_game_settings()` (line 91), called in create_production() line 182. Only caller in production code.
- **Mutable:** No (reference)
- **Risk:** LOW. Fully wired but neither access pattern is used by consumers. The setter is a pure bridge mechanic with no bridge traffic.
- **Recommendation:** Candidate for removal. If no consumer exists, both the module-level default and the ctx field can be removed.

---

### MINOR: `_default_image_provider` — `game/ui/services/image/defaults.py:19`

- **Module-level call sites:** 0 (no consumers found outside definition)
- **ctx.xxx accesses:** 0 (no consumers found)
- **Setter coverage:** `set_default_image_provider()` (line 34), called in create_production() line 184. Only caller in production code.
- **Mutable:** No (reference)
- **Risk:** LOW. Same pattern as `_default_game_settings` — fully wired but unused.
- **Recommendation:** Candidate for removal. If no consumer exists, both accessors can be removed.

---

### MINOR: `_default_sink` (IReplayCaptureSink) — `game/simulation/replay/replay_capture.py:110`

- **Module-level call sites:** 4
  - Simulation: `battle_runner.py:184,369`, `battle_controller.py:443` — (4 get_default)
- **ctx.xxx accesses:** 0 (not ctx-wired — no ctx field)
- **Setter coverage:** `set_default_capture_sink()` (line 118), `reset_default_capture_sink()` (line 125). Called in `app_bootstrap.py:286` (NOT in create_production). Has a non-None default: `NullCaptureSink()`.
- **Mutable:** No (reference)
- **Risk:** LOW. Not ctx-wired, which is acceptable since it's a simulation-layer concept (simulation intentionally avoids ctx). Bootstrap sets it explicitly after create_production(). The module-level default (`NullCaptureSink()`) prevents silent failure. Consistent pattern within the simulation layer.
- **Recommendation:** Accept as-is. Simulation layer uses this pattern consistently. No ctx wiring needed.

---

### MINOR: `_default_ship_materializer` — `game/simulation/services/ship_materializer.py:177`

- **Module-level call sites:** 1
  - Simulation: `battle_runner.py:243` — (1 get_default)
- **ctx.xxx accesses:** 0 (not ctx-wired)
- **Setter coverage:** `set_default_ship_materializer()` (line 193). NOT called in create_production() — Combat Lab sets it at service init. Lazy-initializes to `InstanceBackedMaterializer()`.
- **Mutable:** No (reference)
- **Risk:** LOW. Simulation-layer singleton with consistent module-level pattern. Combat Lab overrides it via setter for its own tests.
- **Recommendation:** Accept as-is. Consistent with simulation layer conventions.

---

### MINOR: `_default_planet_habitability_service` — `game/context.py:33`

- **Module-level call sites:** 1
  - Strategy: `strategy/data/planet.py:280` — (1 get_default)
- **ctx.xxx accesses:** 0 (not ctx-wired — intentional extension slot per PROJ-372)
- **Setter coverage:** `set_default_planet_habitability_service()` (line 46). Lazy-installed at module import time (line 67). Not called from create_production().
- **Mutable:** No (reference)
- **Risk:** LOW. Intentionally module-level and self-contained in `context.py`. Clear documentation for modders. Only one consumer.
- **Recommendation:** Accept as-is. Documented extension slot. Not part of the ctx-managed service graph by design.

---

## Layer-by-Layer Divergence Summary

| Layer | get_default sites | ctx sites | % via ctx | Trend |
|---|---|---|---|---|
| **ui** | ~55 | ~2 (profiler) | ~3.5% | ❌ Heavily module-level |
| **strategy** | ~7 | ~2 (registry_manager via SessionBoostrap) | ~22% | ⬜ Mixed; session/bootstrap uses DI |
| **core** | ~12 | ~1 (TestRegistryProvider) | ~8% | ⬜ Self-referential module-level |
| **ai** | ~2 | 0 | 0% | ❌ All module-level |
| **simulation** | ~6 | 0 | 0% | ✅ Intentionally module-level (by design) |
| **services** | 0 | 0 | N/A | N/A |
| **app/run_loop** | ~1 | ~22 (profiler) | ~96% | ✅ ctx pattern adopted |

### Per-Shard ctx Usage

| Shard | get_default | ctx | % ctx | Interpretation |
|---|---|---|---|---|
| 01 (UI-heavy) | 40 | 1 | 2.4% | UI pattern: near-total module-level |
| 02 (Strategy/UI mix) | 22 | 9 | 29.0% | Strategy files use more DI |
| 03 (app/bootstrap) | 9 | 62 | 87.3% | Bootstrap chain uses ctx.profiler heavily |
| 04 (UI/Strategy mix) | 33 | 23 | 41.1% | Mixed patterns |

**Overall:** 104 get_default calls vs 95 ctx accesses = **47.7% ctx usage**.

The 47.7% overall figure is misleading — ctx usage is concentrated in 3 files (`app.py`, `app_bootstrap.py`, `run_loop.py`), where `ctx.profiler` access dominates. The UI layer's ~55 `get_default` calls represent the bulk of module-level traffic with almost zero ctx penetration.

---

## Module-Level Collection Safety

### Collections with invalidation mechanisms (SAFE)
These caches have explicit invalidation/clear/reset functions and are lazy-loaded with safe defaults:

| Collection | File | Invalidation |
|---|---|---|
| `_font_cache` (dict) | `ui/fonts.py:27` | Not found — potential stale cache risk |
| `_portrait_cache` (dict) | `ui/screens/design_image_helper.py:35` | Not found — potential stale risk |
| `_topdown_cache` (dict) | `ui/screens/design_image_helper.py:36` | Not found — potential stale risk |
| `_PLANET_TYPES_CACHE` | `strategy/data/galaxy_system_generator.py:241` | Global with lazy load, no clear function |
| `_STAR_TYPES_CACHE` | `strategy/data/galaxy_system_generator.py:295` | Global with lazy load, no clear function |
| `_SYSTEM_ARCHETYPES_CACHE` | `strategy/data/galaxy_system_generator.py:320` | Global with lazy load, no clear function |
| `_WARP_POINT_TYPES_CACHE` | `strategy/data/galaxy_warp_generator.py:360` | Global with lazy load, no clear function |
| `_presets_cache` | `strategy/data/homeworld_presets.py:32` | Has `clear_cache()` |
| `_CACHED` | `strategy/engine/minefield_balance.py:156` | Has `reset_minefield_balance_cache()` |
| `_resource_catalog` | `strategy/data/container.py:81` | Has `set_resource_catalog()` |
| `_RESOURCE_ICON_CACHE` | `ui/panels/empire_treasury_panel.py:333` | Has `_clear_resource_icon_cache()` |
| `_FLAG_THUMBNAIL_CACHE` | `ui/panels/race_flag_gallery.py:42` | Has `_clear_thumbnail_caches()` |
| `_PORTRAIT_THUMBNAIL_CACHE` | `ui/panels/race_portrait_gallery.py:40` | Has `_clear_thumbnail_caches()` |
| `_THEME_THUMBNAIL_CACHE` | `ui/panels/race_theme_gallery.py:39` | Has `_clear_thumbnail_caches()` |
| `_FLEETS_AT_HEX_LOOKUP` / `_FLEETS_IN_SYSTEM_LOOKUP` | `strategy/services/ability_iterator.py:276` | Global mutable dicts set via `set_fleet_lookups()` |
| `_production_rates_cache` | `strategy/data/build_queue_source.py:38` | Lazy load, no clear function |
| `_APTITUDE_DISPLAY_NAMES_CACHE` | `strategy/services/race_description_prompt_builder.py:36` | Lazy load, no clear function |
| `_in_flight_calls` | `services/llm/background.py:144` | Set via `start()` — thread-safety unclear |
| `_in_flight_calls` | `ui/services/image/background.py:115` | Set via `start()` — thread-safety unclear |
| `CREW_PRIORITY_REGISTRY` | `simulation/entities/stat_contributors/registry.py:108` | Global mutable, has `unregister_crew_priority()` |
| `_next_fleet_id` | `ui/screens/battle_setup_state.py:29` | Module-level mutable counter — stale across sessions |
| `_specs_cache` | `strategy/facade/slices/command_dispatch_slice.py:36` | Has `_invalidate_specs_cache()` |

### Thread-safety concerns
- `_in_flight_calls` in LLM and image background modules: set within `start()` method, read/checked in `_run()`. No threading.Lock visible — possible race condition between `start()` setting the dict and `_run()` iterating it.
- `ShipThemeManager` uses `threading.Lock` internally (line 41).
- `PolicyManager` imports `threading` but uses only `Lock` for its own caches (not the module-level default).

### Stale cache risk (no invalidation)
- `_font_cache` in `ui/fonts.py` — cached pygame font objects with no clear function. If screen resolution changes or fonts are reloaded, stale entries persist.
- `_portrait_cache` and `_topdown_cache` in `design_image_helper.py` — cached pygame Surfaces with no clear function. Theme changes would not invalidate.
- Galaxy generator caches (`_PLANET_TYPES_CACHE`, `_STAR_TYPES_CACHE`, `_SYSTEM_ARCHETYPES_CACHE`, `_WARP_POINT_TYPES_CACHE`) — lazy-loaded once, no reset for test isolation or data file changes.
- `_next_fleet_id` in battle_setup_state.py — module-level mutable counter, possibly problematic across test runs.

---

## set_default_xxx() Coverage Analysis

| Singleton | Has setter? | Called in create_production()? | Direct assignment? | Bridge mechanic? |
|---|---|---|---|---|
| `_default_registry_manager` | Yes (L175) | Yes | No | No (also used by convenience wrappers) |
| `_default_profiler` | Yes (L176) | Yes | No | **Yes** — only production caller |
| `_default_asset_manager` | Yes (L179) | Yes | No | **Yes** — only production caller |
| `_default_sprite_manager` | Yes (L180) | Yes | No | **Yes** — only production caller |
| `_default_ship_theme_manager` | Yes (L181) | Yes | No | **Yes** — only production caller |
| `_default_game_settings` | Yes (L182) | Yes | No | **Yes** — only production caller |
| `_default_llm_provider` | Yes (L183) | Yes | No | **Yes** — only production caller |
| `_default_image_provider` | Yes (L184) | Yes | No | **Yes** — only production caller |
| `_default_cache_manager` | **NO** | No — raw attr assign L188 | **Yes** (L188) | N/A |
| `_default_policy_manager` | **NO** | No — raw attr assign L190 | **Yes** (L190) | N/A |
| `_default_provider` | **NO** | No — auto-creates in getter | No | N/A |
| `_default_sink` | Yes | **No** — set in bootstrap L286 | No | N/A |
| `_default_ship_materializer` | Yes | **No** — set by Combat Lab | No | N/A |
| `_default_planet_habitability_service` | Yes | **No** — module-import L67 | No | N/A |

**Stale bridge mechanics** (7 total): `set_default_profiler`, `set_default_asset_manager`, `set_default_sprite_manager`, `set_default_ship_theme_manager`, `set_default_game_settings`, `set_default_llm_provider`, `set_default_image_provider`. These functions exist SOLELY to sync module-level defaults with ctx — their only production code caller is `ApplicationContext.create_production()`. Once all consumers migrate to `ctx.xxx`, these can be removed.

**Missing setters** (3): `_default_cache_manager`, `_default_policy_manager`, `_default_provider`. The first two are assigned directly in `create_production()` via module attribute manipulation. The third auto-creates in its getter.

---

## Prioritized Remediation Plan

Ordered by risk × call-site count × divergence severity:

| # | Singleton | Risk | get_default sites | Action |
|---|---|---|---|---|
| 1 | `_default_provider` (RegistryProvider) | CRITICAL | 68+ | Add ctx wiring + setter; or enforce explicit DI everywhere |
| 2 | `_default_ship_theme_manager` | MAJOR | 15 | Migrate UI callers to `ctx.ship_theme_manager` — highest impact on get_default count |
| 3 | `_default_asset_manager` | MAJOR | 7 | Migrate UI callers to `ctx.asset_manager` |
| 4 | `_default_manager` (RegistryManager) | MAJOR | 9 + 2 ctx | Resolve dual-pattern in Core layer — pick one |
| 5 | `_default_cache_manager` | MAJOR | 4 | Add setter + wire in create_production() + fix reset_component_caches() |
| 6 | `_default_policy_manager` | MAJOR | 3 | Add setter + wire in create_production() |
| 7 | `_default_sprite_manager` | MAJOR | 2 | Migrate 2 callers to ctx (one is in `app_bootstrap.py` where ctx is in scope) |
| 8 | `_default_llm_provider` | MAJOR | 1 | Migrate sole caller; then remove bridge |
| 9 | `_default_profiler` | MINOR | 0 | Remove bridge setter (all consumers already use ctx) |
| 10 | `_default_game_settings` + `_default_image_provider` | MINOR | 0 | Remove dead code — no consumers exist |
| 11 | `_default_sink` | MINOR | 4 | Accept (simulation layer convention) |
| 12 | `_default_ship_materializer` | MINOR | 1 | Accept (simulation layer convention) |
| 13 | `_default_planet_habitability_service` | MINOR | 1 | Accept (documented extension slot) |

### Estimated Migration Path

1. **Short-term (add missing setters):** Add `set_default_cache_manager()` and `set_default_policy_manager()`. Replace raw attribute assignments in `create_production()` lines 188 and 190. Make `reset_component_caches()` call through the new setter so ctx divergence doesn't persist.

2. **Medium-term (migrate UI to ctx):** Thread `ctx` (which is already available via `ScreenRouter` and `BootstrapResult`) through UI component constructors. Start with `_default_ship_theme_manager` (15 call sites, highest impact). Then `_default_asset_manager` (7 sites). Then `_default_sprite_manager` (2 sites, one already in a file with ctx available).

3. **Long-term (remove bridge mechanics):** Once all consumers of a singleton use `ctx.xxx`, remove the corresponding `set_default_xxx()` function and the call in `create_production()`. The 7 bridge mechanics can be removed one at a time as each singleton's consumers are migrated.

4. **Architectural decision needed:** `_default_registry_provider` is the elephant in the room at 68+ call sites. Either wire it into ctx formally, or accept the widely-distributed module-level pattern for registries as a conscious architectural choice (the architecture doc already says "Simulation-layer code does not call global registry accessors" — but most other layers do).
