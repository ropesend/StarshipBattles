# PROJ-308 Triage — Per-Site Decisions

**Date:** 2026-04-27
**Total sites:** 24

## Summary
- **NARROW:** 4 sites
- **JUSTIFY:** 20 sites
- **DELETE:** 0 sites

The catches in this codebase are dominated by:
1. UI fire-and-forget paths — fetch race/registry/empire context where save-state drift, partial init, or attribute drift can plausibly raise anything (-> JUSTIFY)
2. Event/callback dispatch (event bus, role invalidation, combat events) where third-party handlers may raise anything (-> JUSTIFY)
3. A few cases where the wrapped block has a small set of well-known exception types (file/JSON/registry-key lookup) (-> NARROW)

DELETE was not chosen for any site: every catch wraps real failure modes (third-party callbacks, save-drift, partial init). When unsure between narrow/justify, JUSTIFY was chosen per `decisions.md`.

---

## Triage Table

### 1. `game/core/event_logging.py:53` — `EventBus.log_event` handler dispatch
**Code:** `self._handler(event_type, **kwargs)` inside try; broad except logs via `logger.exception`.
**Decision:** JUSTIFY
**Reason:** Event handler is third-party callback registered by GameSession or test fixtures; it may raise anything. The module docstring already states: "Handler exceptions are caught and logged to prevent simulation crashes" — the catch is intentional fire-and-forget for instrumentation.
**Comment:** `# Intentional broad catch: third-party event handler may raise anything; instrumentation must never crash the simulation`

### 2. `game/core/event_logging.py:87` — module-level `log_event` handler dispatch
**Code:** Same pattern as #1, module-level compatibility API.
**Decision:** JUSTIFY
**Reason:** Same as #1 — third-party event handler dispatch.
**Comment:** `# Intentional broad catch: third-party event handler may raise anything; instrumentation must never crash the simulation`

### 3. `game/core/roles.py:233` — `RoleRegistry._fire_invalidation_callbacks` callback loop
**Code:** `cb()` inside try; broad except logs via `logger.exception`, loop continues to next callback.
**Decision:** JUSTIFY
**Reason:** Invalidation callbacks are registered by arbitrary subscribers (UI panels, caches); one buggy subscriber must not abort the rest. Function docstring already says "log + swallow exceptions" — this is an intentional design contract.
**Comment:** `# Intentional broad catch: subscriber callbacks may raise anything; one bad subscriber must not abort the rest of the invalidation fan-out`

### 4. `game/ui/services/tkinter_utils.py:100` — `reset_tk_root` destroy call
**Code:** `_tk_root.destroy()` in try; pass on broad except. **Already commented:** "Intentional: destroy may fail if already destroyed".
**Decision:** JUSTIFY (verify quality — upgrade to canonical format)
**Reason:** The existing comment is specific and good ("destroy may fail if already destroyed"), but doesn't use the canonical `Intentional broad catch:` prefix. Upgrade for consistency.
**Comment:** `# Intentional broad catch: Tk widget .destroy() raises various TclError subclasses if already destroyed or interpreter is gone`

### 5. `game/ui/panels/system_tree_panel.py:393` — `_add_system_effects` failure path
**Code:** Block calls `collect_system_effects(system, empire_id, registries)` which traverses planet/empire data; broad except logs at debug level.
**Decision:** JUSTIFY
**Reason:** `collect_system_effects` walks empire data, registries, and effect collectors — many failure modes (missing registry entries, partial save state, attribute drift on legacy save data). Failed effect display in the tree must not crash the strategy UI.
**Comment:** `# Intentional broad catch: effect collection traverses empire/registry/save data — many drift-failure modes; tree panel must not crash on display`

### 6. `game/ui/panels/system_tree_panel.py:408` — `_add_sector_effects` failure path
**Code:** Same pattern as #5 but for sector-scope effects.
**Decision:** JUSTIFY
**Reason:** Same as #5 — sector effects collector traverses similar state.
**Comment:** `# Intentional broad catch: effect collection traverses empire/registry/save data — many drift-failure modes; tree panel must not crash on display`

### 7. `game/simulation/combat/telemetry.py:312` — weapon ability class extraction
**Code:** Imports `WeaponAbility`, iterates `abilities`, falls back to `damage_type` attr on broad except.
**Decision:** NARROW
**Reason:** The wrapped block has a knowable failure surface: `ImportError` (module load) and `AttributeError` (component shape drift). This is internal code with a clear contract — narrow catches are safer than swallowing arbitrary errors.
**New types:** `(ImportError, AttributeError)`

### 8. `game/simulation/combat/combat_events.py:161` — `CombatEventBus.publish` subscriber dispatch
**Code:** `cb(event)` in try; broad except logs via `logger.exception`. Docstring states "Subscriber exceptions are caught and logged."
**Decision:** JUSTIFY
**Reason:** Combat event subscribers are arbitrary observers (UI overlays, telemetry, AI). A single buggy subscriber must not break combat.
**Comment:** `# Intentional broad catch: subscribers may raise anything; one buggy observer must not break combat event dispatch`

### 9. `game/ui/panels/build_queue_controller.py:217` — design validator catch in queue panel
**Code:** Calls `design_library.load_design_data(...)` and `validator.validate(...)`; on any failure marks `design_valid = True` ("Can't validate, assume valid").
**Decision:** JUSTIFY
**Reason:** Validator is data-driven and recurses through a design's components and abilities; failures across the wide validator surface should not nuke the player's queue panel. The "assume valid" fallback is a deliberate UX choice (don't lock the user out of queueing).
**Comment:** `# Intentional broad catch: design validation traverses arbitrary registry/save data; queue panel must remain usable on validator failure`

### 10. `game/ui/screens/food_allocation_editor.py:109` — `resource_catalog.get(resource_id)`
**Code:** `definition = resource_catalog.get(resource_id)` in try; falls back to raw resource id.
**Decision:** NARROW
**Reason:** Catalog lookups have a small known failure surface (`KeyError`, `AttributeError` if catalog has unexpected shape). Docstring already says modders may have catalog/economy-config drift.
**New types:** `(KeyError, AttributeError)`

### 11. `game/ui/screens/battle_setup/controller.py:56` — `_get_default_registries`
**Code:** Calls `get_default_registry_provider()` then unpacks 5 sub-registries; returns None on broad except.
**Decision:** JUSTIFY
**Reason:** Provider may not be initialized in tests (docstring says so), and the chained provider getter calls can fail in many ways (uninitialized provider raises, partial init, type drift). Returning None is the documented test-path behavior.
**Comment:** `# Intentional broad catch: registry provider may be uninitialized (tests) or partially loaded; None signals "no registries" to callers`

### 12. `game/ui/screens/battle_setup/fleet_hierarchy_editor.py:190` — same provider unpack
**Code:** Identical to #11.
**Decision:** JUSTIFY
**Reason:** Same as #11.
**Comment:** `# Intentional broad catch: registry provider may be uninitialized (tests) or partially loaded; None signals "no registries" to callers`

### 13. `game/ui/screens/builder/stats_config.py:241` — `load_sections_config()` at module import
**Code:** Module-level `try: SECTIONS_CONFIG, ALWAYS_VISIBLE = load_sections_config()` with broad except logging warning and falling back to `{}, {}`.
**Decision:** NARROW
**Reason:** Loader reads JSON from disk; failure modes are file-not-found / JSON parse / schema mismatch. These are knowable types.
**New types:** `(OSError, ValueError, KeyError)` (OSError for file I/O, ValueError covers `json.JSONDecodeError` which subclasses it, KeyError for missing schema fields).

### 14. `game/ui/screens/species_selector_mixin.py:124` — `RaceLibrary.get_race(race_id)`
**Code:** `RaceLibrary().get_race(race_id)` in try; logs warning + returns None on broad except.
**Decision:** JUSTIFY
**Reason:** `RaceLibrary()` instantiation reads JSON files; `get_race()` may raise for missing/malformed data. The library's failure surface includes file I/O, JSON parse, and schema-validation errors — too varied to enumerate without lock-in to library internals (UI mixin shouldn't know library guts).
**Comment:** `# Intentional broad catch: RaceLibrary load surfaces I/O, JSON, and schema-validation errors; UI mixin must not crash species selection on bad data`

### 15. `game/ui/screens/strategy_detail_fmt.py:319` — `provider.get_components()` lookup
**Code:** `provider = get_default_registry_provider(); component_registry = provider.get_components()` in try; pass on broad except (component_registry remains None).
**Decision:** JUSTIFY
**Reason:** Provider may not be initialized (test/CLI paths); broad catch allows the formatter to fall back to inline-only ability detection. None-fallback is explicit several lines down.
**Comment:** `# Intentional broad catch: registry provider may be uninitialized; fall back to inline-ability inspection`

### 16. `game/ui/screens/strategy_detail_fmt.py:417` — `get_default_registry_manager()`
**Code:** Same pattern as #15.
**Decision:** JUSTIFY
**Reason:** Same as #15.
**Comment:** `# Intentional broad catch: registry manager may be uninitialized; fall back to inline-ability inspection`

### 17. `game/ui/screens/strategy_event_router.py:215` — race_config fetch for atmosphere editor
**Code:** Fetches `empire`, then either uses `empire.race_config` or falls back to `RaceLibrary().get_race(race_id)`. On broad except, race_config stays None.
**Decision:** JUSTIFY
**Reason:** Two failure surfaces composed: `scene.session.get_empire()` (save state lookup) and `RaceLibrary` load (I/O + JSON + schema). UI editor should still open with a None race_config.
**Comment:** `# Intentional broad catch: empire/race lookup may fail on save drift or library load errors; editor opens without race-specific UI`

### 18. `game/ui/screens/strategy_event_router.py:317` — resource_catalog fetch for food editor
**Code:** `get_default_registry_provider().get_resource_catalog()` in try; pass on broad except.
**Decision:** JUSTIFY
**Reason:** Same registry-provider-may-be-uninitialized story as #11/#15. Editor opens with None catalog.
**Comment:** `# Intentional broad catch: registry provider may be uninitialized; food editor opens without resource catalog`

### 19. `game/ui/screens/strategy_event_router.py:329` — RaceLibrary fallback in `resolve_race`
**Code:** `RaceLibrary().get_race(race_id)` in try; returns None on broad except.
**Decision:** JUSTIFY
**Reason:** Same library-load-surface story as #14.
**Comment:** `# Intentional broad catch: RaceLibrary load surfaces I/O, JSON, and schema-validation errors; resolver returns None on failure`

### 20. `game/ui/screens/strategy_event_router.py:360` — `_get_race_config` empire/race lookup
**Code:** Same shape as #17.
**Decision:** JUSTIFY
**Reason:** Same as #17.
**Comment:** `# Intentional broad catch: empire/race lookup may fail on save drift or library load errors; caller falls back to None`

### 21. `game/ui/screens/strategy_fleet_command_router.py:259` — provider component lookup
**Code:** Same pattern as #15.
**Decision:** JUSTIFY
**Reason:** Same as #15.
**Comment:** `# Intentional broad catch: registry provider may be uninitialized; ability-button handler falls back to no registry`

### 22. `game/ui/screens/strategy_window_manager.py:592` — provider component lookup
**Code:** Same pattern as #15, in `open_planet_abilities_window`.
**Decision:** JUSTIFY
**Reason:** Same as #15.
**Comment:** `# Intentional broad catch: registry provider may be uninitialized; abilities window opens without registry-backed lookups`

### 23. `game/ui/screens/transfer_dialog.py:426` — `_discover_pod_designs` design library load
**Code:** Builds `DesignLibrary(save_path, empire_id)` and filters; on broad except logs debug + returns `[]`.
**Decision:** JUSTIFY
**Reason:** DesignLibrary construction reads JSON design files from save_path; failure surface includes I/O, JSON parse, schema validation, and library invariants. Empty-list fallback is explicit ("falling back to empty list").
**Comment:** `# Intentional broad catch: DesignLibrary load surfaces I/O, JSON, and schema-validation errors; transfer dialog falls back to empty pod list`

### 24. `game/ui/screens/workshop_data_reloader.py:23` — module-level Tk init
**Code:** `tk_root = tk.Tk(); tk_root.withdraw()` in module-level try; sets `tk_root = None` on broad except. **Already commented:** "Intentional broad catch: Tkinter init is platform-dependent".
**Decision:** JUSTIFY (already in canonical format — no change needed)
**Reason:** Comment is specific and uses the canonical prefix. No-op.
**Comment:** unchanged.

---

## Sanity Check (Phase 1.2)

- Distribution: 4 narrow / 20 justify / 0 delete. Most are JUSTIFY (UI fire-and-forget, event/callback dispatch, registry-may-be-uninitialized) — matches the expected shape. NARROW used where the failure surface is small and well-known (telemetry attribute extraction, JSON file load, catalog lookup).
- DELETE was not chosen for any site. Per `decisions.md`, when in doubt JUSTIFY; the catches all wrap genuine failure surfaces (third-party callbacks, save-drift state, partial init).
- Every JUSTIFY reason names a specific failure mode (e.g., "save drift", "third-party handler", "uninitialized provider", "library load surfaces I/O + JSON + schema") rather than boilerplate.
