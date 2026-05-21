# Pattern Audit — Verification Report

> Verified: 2026-05-20 | Source files manually read at cited locations

---

## Cross-Agent Contradictions

### C1: SettingsWindow Classification — pattern_review_03 vs pattern_review_01 + pattern_hunter_cross_shard

- **Agent A (pattern_review_03:105-109):** Claims SettingsWindow is "Not strategy overlay" and "legitimate — not strategy modal." Places it alongside RaceSetupScreen and NewGameSetupScreen as a setup-level UIWindow.
- **Agent B (pattern_review_01:30-50):** Flags SettingsWindow as MAJOR — explicitly opened from strategy screen context via `EmpirePanelRegistrar`, should subclass `StrategyModalWindow`.
- **Agent C (pattern_hunter_cross_shard:189-207):** Same as Agent B — flags as MAJOR, notes it's "a strategy-screen modal opened from `EmpirePanelRegistrar`."

**Verdict: Agent A is DISPUTED.** SettingsWindow is opened from `SettingsRegistrar` in `empire_panel_ctrl.py:77-94`, which is part of `StrategyWindowManager` (`game/ui/screens/strategy_window_manager.py`). `SettingsRegistrar` is a peer of `EmpirePanelRegistrar` — both are strategy-screen registrar classes. SettingsWindow is a strategy-screen modal that should follow Pattern #31. The classification as "legitimate non-strategy overlay" in pattern_review_03 is incorrect.

---

## CRITICAL Findings Verification

| ID | Source | Location | Claim | Verdict | Notes |
|----|--------|----------|-------|---------|-------|
| **CRIT-H1** | pattern_hunter | 135+ import sites across `game/ui/` | UI imports strategy data objects bypassing facade read DTOs (Pattern #5) | **CONFIRMED** | Verified 10+ specific sites. `strategy_detail_fmt.py:290-291` imports `CarriedVehicle`/`DropPod`. `strategy_detail_fmt.py:396-398` imports `ActivationPhase`/`ComponentActivationState`. `strategy_detail_formatter.py:277` imports `colony_has_planetary_yard`. `fleet_menu_items.py:25` imports `FighterWing`/`SatelliteConstellation`. `planet_menu_items.py:24-25` imports `FighterWing`/`SatelliteConstellation` + `FacilityAbilitySource`. `build_queue_screen.py:23` imports `BuildQueueSource`/`collect_build_queues_at_hex`. `build_queue_panel_factory.py:18` imports `compute_planet_production`. `build_queue_controller.py:19-24` imports 6 strategy data types. `fleet_data_source.py:241-243` late-imports `FleetCapabilityCalculator`. Facade DTOs (`FleetInfo`, `PlanetInfo`, `SystemInfo`, etc.) do NOT cover these types. The facade is a write-path-only half-facade. **Severity CRITICAL is justified** — this is a structural architectural gap, not a single violation. |
| **CRIT-H2** | pattern_hunter | `build_queue_controller.py:19-24`, `build_queue_screen.py:23`, `fleet_data_source.py:241` | BuildQueueScreen + related UI directly construct commands AND import strategy internals for data reads | **CONFIRMED** | Verified. `build_queue_controller.py:19-24` imports `BuildContext`, `BuildQueueSource`, `Planet`, `Fleet`, `Galaxy`, `Empire` (all under `TYPE_CHECKING`). `build_queue_screen.py:23` imports `BuildQueueSource`/`collect_build_queues_at_hex` (runtime import). `fleet_data_source.py:241` imports `FleetCapabilityCalculator` (runtime import). Write path (commands) goes through `facade.handle_command()` per CQRS check in hunter report — that part is clean. The issue is data reads. **Severity CRITICAL is justified** — these are the densest single-file bypass sites. |

---

## MAJOR Findings Spot-Check

| ID | Source | Claim | Verdict | Notes |
|----|--------|-------|---------|-------|
| **MAJ-R1** | pattern_review_01:30-50 | `SettingsWindow` extends `UIWindow` directly rather than `StrategyModalWindow` (Pattern #31) | **CONFIRMED** | Verified: `settings_window.py:14` → `class SettingsWindow(UIWindow):`. Opened from strategy screen via `SettingsRegistrar.open()` at `empire_panel_ctrl.py:77-94`. Constructor has no `window_manager` param, no `is_blocking = True`, no modal registration. Manual `on_close_callback` lifecycle at `settings_window.py:106-109`. Result: background hover/click may leak through while SettingsWindow is open; not counted by `has_modal_open()`. **Severity MAJOR justified.** |
| **MAJ-R4** | pattern_review_04:23-28 | Facade Bypass via `StrategyScreen.session` property (Pattern #5) | **CONFIRMED** | Verified: `strategy_screen.py:242-257` exposes `self._session` as a public property. Docstring acknowledges "audit-residue delegate" with deferred PROJs U1/U2/U3. Active usage: `strategy_detail_formatter.py:112` reads `self.scene.session.registries`, `strategy_detail_formatter.py:395-396` accesses `self.scene.session.turn_engine`, `list_windows.py:69` passes `c.scene.session.empires`, `hex_outlines.py:30` reads `r.scene.session.active_empire.id`. These are all read-path bypasses of the facade. **Severity MAJOR justified** — known/tracked but actively used. |
| **MAJ-H3** | pattern_hunter:89-113 | Two incompatible EventBus implementations with stale cross-references | **CONFIRMED** | Verified: Core `EventBus` (`event_logging.py:40`) uses single-handler + `log_event(event_type, **kwargs)`. Workshop `WorkshopEventBus` (`builder/event_bus.py:19`) uses pub/sub + `emit(event_type, data)`. **Stale path confirmed**: `event_bus.py:5` references `game/core/events/event_bus.py` — that path does not exist; core EventBus is at `game/core/event_logging.py`. **Severity MAJOR justified** — stale doc reference is a maintainability hazard and the two buses share no contract. |
| **MAJ-H4** | pattern_hunter:210-215 | `RaceSetupScreen`, `NewGameSetupScreen` extend UIWindow directly instead of StrategyModalWindow | **DISPUTED (downgrade to MINOR)** | Verified: `race_setup/screen.py:63` → `class RaceSetupScreen(pygame_gui.elements.UIWindow):`. These are full-screen setup wizards that own the entire UI context — they are NOT strategy-screen modals. The hunter report itself notes they "may be out of strategy-screen scope." They run before a strategy session exists (race setup) or create a new game config (new game setup). The Pattern #31 doc specifies "for strategy-screen modals that should block input" — setup screens are not strategy-screen modals. **Severity should be MINOR or ADVISORY.** |
| **MAJ-H5** | pattern_hunter:182-184 | `IAbilitySource.source_kind` discriminator has no enum — string-typed with 7 known values | **CONFIRMED but downgrade to MINOR** | Verified: `strategy_entities.py:374` → `source_kind(self) -> str` with docstring listing 7 values. No `StrEnum` or `Literal` type. Adding an 8th source kind would not produce a type error. However: (a) all 7 adapters are in a single directory (`ability_sources/`), (b) the string values are stable and documented in the protocol, (c) `source_kind` is checked by `ability_iterator.py` registration logic, (d) this is a code-quality gap, not a runtime risk. **Severity should be MINOR** — a type-safety improvement, not an architectural drift requiring urgent action. |
| **MAJ-H1** | pattern_hunter:56-64 | Simulation layer calls `get_default_registry_provider()` through adapter boundary | **DISPUTED (downgrade to MINOR)** | The hunter report itself notes "This is architecturally correct (the strategy layer injects the provider, simulation doesn't resolve it)." `simulation_adapter.py:51-52` is strategy-layer code that constructs a provider to inject into simulation. The report's own CQRS-lite section confirms the injection pattern is correct. The adapter is the designated injection point per Pattern #29. **Not a violation — correctly implemented adapter pattern.** |

---

## Documentation Accuracy Disputes

| Pattern # | Accuracy Assessment | Verdict | Notes |
|-----------|-------------------|---------|-------|
| **#10 (Event Bus)** | MINOR_DIFF — WorkshopEventBus renamed from EventBus, doc not updated with class name | **CONFIRMED** | The doc (`02_PATTERNS.md:252-265`) correctly references the file location and contract but uses "Workshop event bus" generically without the actual class name `WorkshopEventBus`. More importantly, the code's docstring (`builder/event_bus.py:5`) has a **stale path** referencing `game/core/events/event_bus.py` — the core EventBus was moved to `game/core/event_logging.py` (PROJ-390). This stale reference is the bigger problem. Validator correctly flags the omission. |
| **#32 (Compositional Construction)** | MINOR_DIFF — only one production consumer (StrategyScreen) | **CONFIRMED** | Doc at `02_PATTERNS.md:698` says "Use for classes that construct three or more stable, heavy collaborators" but only `StrategyScreen` uses it. The pattern is well-defined and functional, just not widely adopted. Validator's observation is accurate. |
| **#36 (Re-Export Shim)** | MINOR_DIFF — line numbers say 395-405, actual is 392-405 | **CONFIRMED (trivial)** | A 3-line offset in a comment. No functional impact. |

---

## Overall Assessment

- **Total CRITICAL claims:** 2
- **CONFIRMED:** 2 | **DISPUTED:** 0 | **INCONCLUSIVE:** 0

- **Total MAJOR claims sampled:** 6 (all major findings across reports)
  - CONFIRMED as MAJOR: 3 (MAJ-R1, MAJ-R4, MAJ-H3)
  - DISPUTED (downgrade to MINOR): 3 (MAJ-H1, MAJ-H4, MAJ-H5)

- **Cross-agent contradictions:** 1 (SettingsWindow classification — pattern_review_03 vs pattern_review_01/hunter)

- **Documentation disputes:** 3 MINOR_DIFFs — all CONFIRMED, all trivial

### Summary of Most Important Confirmed Issues

1. **CRIT-H1 / CRIT-H2: Facade read-path DTO gap.** The facade exposes write-path commands and a partial set of read DTOs (`FleetInfo`, `PlanetInfo`, `SystemInfo`, `ColonyDemographicView`, `ContainerSnapshotInfo`, `EmpireInfo`), but UI code needs `BuildQueueSource`, `FleetCapabilityCalculator`, `CarriedVehicle`, `DropPod`, `FighterWing`, `SatelliteConstellation`, `ActivationPhase`, `ComponentActivationState`, `ContainableKind`, `FacilityAbilitySource`, `RaceConfig`, and others — none of which are available through the facade's grouped namespaces. This makes the facade a write-path-only half-facade. 135+ import sites in `game/ui/` reach past the facade. Either add DTOs for all data the UI needs, or formally document which types are UI-safe for read access.

2. **MAJ-R1: SettingsWindow bypasses Pattern #31.** Opened from the strategy screen via `SettingsRegistrar`, but extends `UIWindow` directly — no modal registration, no `is_blocking`, not counted by `has_modal_open()`. Background hover/click can leak through while settings are open. Fix is straightforward (subclass `StrategyModalWindow`, add `window_manager` param).

3. **MAJ-H3: EventBus fragmentation.** Two buses with different architectures, different payload signatures, and a stale doc-reference path (`game/core/events/event_bus.py` in `WorkshopEventBus` docstring). At minimum, fix the stale path reference. Ideally, document whether the divergence is intentional or create a shared `EventBusProtocol`.

4. **MAJ-R4: StrategyScreen.session read-path bypass.** 4+ production sites read strategy domain objects directly through `screen.session.*` rather than through the facade. Known issue tracked by deferred PROJs U1/U2/U3, but the AST guard only protects the write path.
