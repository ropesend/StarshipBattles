# Validation Report: Validator 3

## Summary
- **Findings Reviewed:** 26
- **Confirmed:** 23
- **Downgraded:** 2
- **Rejected:** 1
- **Rejection Rate:** 3.8%

## Verdicts

#### Finding: DOCC-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `game/strategy/__init__.py` line 64 exports `FleetOrder` as a backward-compat alias in `__all__`, but the strategy_layer.md DTO/export list does not mention it.

#### Finding: DOCC-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** The package docstring at line 11-13 says `OrderType, FleetOrder - Fleet movement orders` which uses the old name and old description. The canonical name is now `Order` and orders apply to all entities, not just fleets.

#### Finding: DOCC-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `docs/03_CONVENTIONS.md` lines 133-134 state "Old backward compatibility alias modules have been deleted. All code must use the new names" yet `game/strategy/__init__.py` still exports `FleetOrder` at line 34 and 64. The alias contradicts the documented policy.

#### Finding: DOCC-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Files such as `planet_atmosphere.py`, `species_population.py`, `race_config.py`, `race_point_budget.py`, and many others exist in `game/strategy/data/` but are not mentioned in any architecture or system docs. Verified via grep against the docs directory.

#### Finding: DOCC-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `game/strategy/engine/empire_economy_calculator.py` exists on disk but is not mentioned in any docs file (confirmed by grep of the docs directory for "empire_economy_calculator").

#### Finding: DOCC-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** The DTO `__init__.py` exports `FleetOrderInfo`, `ShipInfo`, `WarpPointInfo`, `StarInfo`, `ColonySummary`, and `FleetSummary`, but `docs/systems/strategy_layer.md` lines 27-33 only list `FleetInfo`, `FleetSummary`, `StarInfo`, `SystemInfo`, `PlanetInfo`, `EmpireInfo`, `ColonySummary`. It omits `FleetOrderInfo`, `ShipInfo`, and `WarpPointInfo`.

#### Finding: DOCC-013
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `game/strategy/generation/star_image_registry.py` exists on disk. Grep of docs for "StarImageRegistry" or "star_image_registry" returns no matches. Only PlanetImageRegistry is documented.

#### Finding: DOCC-014
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** `docs/systems/orders_system.md` uses `FleetOrder` extensively in tutorial/example code (lines 17, 37, 40, 186, 364, 387, 410). The canonical class name is now `Order`.

#### Finding: DOCC-015
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** The module docstring in `game/strategy/engine/turn_engine.py` at line 42 shows `engine = TurnEngine()` but the constructor at line 111 requires `registries` as a keyword-only argument (`*, registries: GameRegistries`). The example is misleading. Note: the finding says this is in strategy_layer.md but it's actually in the source code docstring. The issue is real regardless.

#### Finding: DOCC-016
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** `docs/systems/orders_system.md` line 387 says "FleetOrder class" in the Key Files table. The canonical name is `Order`.

#### Finding: DOCC-017
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** The doc claims "Six components restricted to Planetary Complex" but `data/components.json` actually has 18 components exclusively restricted to Planetary Complex (including stabilizers, harvest boosters, build rate boosters, atmosphere modifier, quality improvers). The doc only lists the 5 harvesters + space_shipyard.

#### Finding: DOCC-018
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** I compared the facade query method table in strategy_layer.md against all `get_*`, `can_*`, and query methods in `strategy_session_facade.py`. Every method in the facade is listed in the table. The finding provides no specific missing method, and I found none.

#### Finding: ERR-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** The `process_turn` method at lines 369-370 iterates 100 ticks calling `_process_tick` with no try/except around the loop or individual ticks. An exception in any sub-engine phase would leave the turn partially processed with no rollback or recovery.

#### Finding: ERR-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Three `from_dict` deserialization methods use `except Exception as e` without the `# Intentional broad catch:` annotation: `fleet.py:394`, `empire.py:329`, and `order_serializer.py:57`. This is consistent with the project's convention requirement.

#### Finding: ERR-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The finding claims "six locations" but only 3 exist: `fleet_capability_calculator.py` lines 72 and 135, and `ship_instance.py` line 249. These raise `ValueError` for missing registry, which is arguably an infrastructure/configuration error rather than domain validation. While `ValidationException` exists in `game/core/exceptions.py`, using ValueError for "missing required argument" is a common Python convention. Downgraded due to overstated count and debatable severity.

#### Finding: ERR-004
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The `_log_empire_state` method at lines 223-224 catches `(AttributeError, TypeError)` with bare `pass`. However, this is a debug logging helper (BUG-109) that only runs at debug level. Silently ignoring logging failures in a debug helper is acceptable -- it should not crash the turn. Major is overstated for a non-critical debug path.

#### Finding: ERR-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** At lines 56-57, the `PermissionError` handler logs the error but does not fall back to a temp directory (unlike the `OSError` handler at lines 60-64 which does). The `designs_folder` remains set to the inaccessible path, causing all subsequent operations to fail.

#### Finding: ERR-006
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** At line 255-256, the `JSONDecodeError` handler returns `(False, "Design file is corrupted")` without logging. The subsequent `(PermissionError, OSError)` handler also doesn't log, but the `(KeyError, TypeError, ValueError, AttributeError)` handler at line 260 does use `logger.error`. Inconsistent error logging within the same method.

#### Finding: ERR-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `_load_production_rates` at lines 34-37 catches `(FileNotFoundError, ValueError)` and silently falls back to an empty dict without any logging. A missing or corrupt data file would be invisible.

#### Finding: ERR-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** At lines 218-219, an invalid `homeworld_type` KeyError is caught with bare `pass` and no logging. The comment "Keep existing type if invalid" documents intent but the silent failure could hide race config issues.

#### Finding: ERR-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** At lines 636-637, a `ValueError` from `int()` parsing is caught with bare `pass` in a loop that matches indexed component keys. This is actually a legitimate control flow pattern (testing if a suffix is numeric), but a comment would help clarify intent.

#### Finding: ERR-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** At lines 184-186 of `fleet_dto.py`, a `(ValueError, AttributeError)` from `fleet.capabilities.list_abilities()` is caught with an empty tuple fallback and no logging. A fleet with a broken registry would silently report no capabilities.

#### Finding: ERR-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** At lines 383-384 of `design_library.py`, the `PermissionError` handler returns `(False, "Failed to delete design: Permission denied")` but doesn't call `logger.error`, unlike the catch-all handler at line 388 which does log.

#### Finding: ERR-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** At lines 222-226 of `command_handlers.py`, `_resolve_build_entity` returns `None` for unknown `entity_type` values without logging. Callers could silently receive None for a typo in entity_type.

#### Finding: ERR-013
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Confirmed as dead code. `_resolve_fleet_required` and `_resolve_planet_optional` are defined at lines 140-205 of `command_handlers.py` but grep across the entire `game/` directory shows zero call sites (only the definition and a comment). They are documented in `strategy_layer.md` as part of BaseCommandHandler's API, suggesting they were intentionally added (PROJ-204 Phase 3) for future use but never adopted.

#### Finding: ERR-014
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** At lines 387-401 of `turn_engine.py`, the turn performance timing summary uses `logger.warning()` for routine performance data that should use `logger.info()`. Warning level is typically reserved for potential problems, not normal operational metrics.

