# Validation Report: Validator 1

## Summary
- **Findings Reviewed:** 15
- **Confirmed:** 9
- **Downgraded:** 4
- **Rejected:** 2
- **Rejection Rate:** 13.3%

## Verdicts

#### Finding: CQ-01
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** The `clamp()` function exists at `game/core/math.py:187`, is exported via `game/core/__init__.py`, and zero production modules import it. Grep confirms exactly 66 occurrences of `max(min_val, min(max_val, value))` across 40 files in `game/`. This is a clear utility underutilization issue.

#### Finding: CQ-02
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**New Severity:** Minor
**Reason:** The identical `_get_registries()` function is copy-pasted in `ship_io.py:41-53` and `strategy_build_queue_manager.py:37-49` -- confirmed identical code. However, `ship_factory.py:59` has a completely different `_get_registries()` that simply returns `self._registry_provider` (a one-liner accessor, not the same lazy init pattern). The finding claims 3 files but only 2 have the actual duplication. This is real but overstated; with only 2 duplicates, severity should be Minor.

#### Finding: CQ-03
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `stats_config.py:140-154` reimplements the exact same formula as `FleetSpeedCalculator.calculate_ship_speed()`, including hardcoded constants `K_STRATEGIC = 25`, `MAX_HEXES = 10`, `MIN_HEXES = 0`, and the same `(movement_points * K_STRATEGIC) / mass` calculation with identical clamping. The comment even says "Uses same formula as FleetSpeedCalculator" but doesn't import from it.

#### Finding: CQ-04
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**New Severity:** Minor
**Reason:** `ship_stats_calculator.py:43` defines `DEFAULT_DAMAGE_THRESHOLD = 0.5` with comment "aligned with simulation layer", while `core/constants.py:57` has `CombatConstants.DEFAULT_DAMAGE_THRESHOLD = 0.5`. The duplication is real. However, this is a single constant with a clear alignment comment, and changing one without the other would be caught by tests. The risk is low, making Minor more appropriate than Major.

#### Finding: CQ-05
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Grep finds 18 occurrences of the `if registries is None: raise ValidationException(...)` pattern across 10 files (with some files having multiple occurrences). The pattern is nearly identical each time, varying only in the `context` dict values. The Minor severity is appropriate -- it is boilerplate but each guard serves a legitimate purpose and a shared helper would only marginally reduce complexity.

#### Finding: CQ-06
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The `iter_layers_and_components()` utility in `core/patterns/layer_iterator.py` operates on `design_data` dicts (JSON-like data with list/dict layer formats). The 11 manual `for layer_type, layer_data in ship.layers.items()` iterations operate on `Ship` objects (where `.layers` is a dict of `LayerType` to `LayerData` objects with `.components` attributes). These are fundamentally different data structures and the utility cannot replace the manual iterations. Furthermore, the finding claims "only 2 production modules" use the utility, but grep shows 6 production modules importing from it. The finding misidentifies the problem.

#### Finding: CQ-07
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Two distinct `ICombatShip` Protocol classes exist: `game/core/protocols.py:601` (with `name`, `team_id`, `is_alive`, `is_derelict`, `hp`, `max_hp`, `position`, `layers`, `resources`, `current_target`, `secondary_targets`, `max_targets`, `total_defense_score`, `get_total_sensor_score`) and `game/simulation/interfaces/entity_protocols.py:43` (with `name`, `team_id`, `angle`, `position`, `velocity`, `radius`, `mass`, `hp`, `max_hp`, `is_alive`, `is_derelict`, `current_shields`, `max_shields`, and many more). Having two protocols with the same name and overlapping but different member sets in different layers is a genuine architectural issue.

#### Finding: CQ-08
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**New Severity:** Minor
**Reason:** The `handle_event` method is used by IScene implementations (scenes/screens that conform to the IScene protocol). The `process_event` method is used by UIWindow/Dialog/Panel classes (pygame_gui-based windows). These are two different class hierarchies with different purposes: IScene defines the scene lifecycle, while UIWindow classes are overlay widgets. The naming difference reflects a genuine architectural distinction rather than inconsistency. The finding mischaracterizes these as "the same event-handling pattern."

#### Finding: CQ-09
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `component.py:566,672` raises `ValueError("registry_provider is required")` while `component.py:96` raises `ValidationException(...)` for the exact same check in the same file. Similarly, `ship_loader.py:136` raises `ValueError` while `ship.py:51` uses `ValidationException` for the same registries-is-None guard. `command_handlers.py:175,178,219` raises `ValueError` for entity-not-found errors. Using raw `ValueError` when a custom `ValidationException` hierarchy exists (and is used elsewhere for identical checks) is genuinely inconsistent.

#### Finding: CQ-10
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `game/strategy/interfaces/engines.py` uses `ABC` with `@abstractmethod` for 10+ engine interfaces (`IMovementEngine`, `IProductionEngine`, etc.), while `game/core/protocols.py` uses `Protocol` for structural typing (`IRegistryProvider`, `ICombatShip`, `IScene`, etc.). This is a real stylistic split between layers. Minor severity is appropriate since both approaches work correctly and the strategy ABCs serve a legitimate purpose (enforcing implementation via inheritance).

#### Finding: CQ-11
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**New Severity:** Major
**Reason:** The `IScene.handle_event` protocol at `core/protocols.py:776` declares `-> None`, but 6 classes return `bool`: `ScrollableJsonPanel`, `ModifierImpactGrid`, `ComponentModifierGridPanel`, `BattleStateViewer`, `RaceIdentityPanel`, and `WorkshopEventRouter`. Critically, `WorkshopScreen.handle_event` (which is an actual IScene implementation per its docstring) delegates to `WorkshopEventRouter.handle_event` and returns the bool result. However, the 5 widget/panel classes are NOT IScene implementations -- they just share the method name. Only the WorkshopScreen chain is a true protocol violation. This is Major (contract mismatch) but not Critical since Python does not enforce return types at runtime and no caller depends on the bool return from the protocol.

#### Finding: CQ-12
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Five modules use module-level global caches with no invalidation: `ship_io.py` (`_cached_registries`), `strategy_build_queue_manager.py` (`_cached_registries`), `setup_data_io.py` (`_ship_factory`), `setup_screen.py` (`_ship_factory`), `build_queue_source.py` (`_production_rates_cache`). One of the 6 claimed modules, `homeworld_presets.py`, actually HAS a `clear_cache()` invalidation function, so it is a partial exception. Nonetheless, the core claim is valid for 5 modules with no way to reset stale caches.

#### Finding: CQ-13
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `formation_editor.py:823` uses `handle_resize(self, w: int, h: int)` while the `IScene` protocol at `core/protocols.py:788` and all other implementations use `handle_resize(self, width: int, height: int)`. Verified at the exact stated location. Minor severity is correct -- parameter names don't affect runtime behavior in Python but harm readability and IDE tooling consistency.

#### Finding: CQ-14
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Line counts verified: `strategy_renderer.py` (1102 lines), `test_lab/renderer.py` (1040 lines), `race_setup_screen.py` (1029 lines). All three exceed 1000 lines as claimed. Major severity is appropriate for maintainability concerns in a codebase that targets <50-line functions and has active god class decomposition projects.

#### Finding: CQ-15
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `ship_instance.py` is exactly 755 lines with exactly 47 methods verified by grep. The methods span design data access, damage tracking, stat calculation, serialization, cargo management, and resource management. Minor severity is appropriate given that PROJ-87 (Strategy Data Tier god class decomposition) already exists in active projects and lists ShipInstance decomposition.
