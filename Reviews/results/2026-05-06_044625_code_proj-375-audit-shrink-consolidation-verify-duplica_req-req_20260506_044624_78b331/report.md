# PROJ-375 Consolidation Verification Report

**Request ID:** req_20260506_044624_78b331  
**Review Type:** code  
**Review Mode:** normal — full semantic equivalence walkthrough  
**Scope:** 3 commits on `feat/03c-phase-aware-execution` (2d2cc3566, a71b35944, c0f58bb0b)  
**Files Reviewed:** 11 production files, 3 test files (26 total)  
**Branch:** `feat/03c-phase-aware-execution` (tip c0f58bb0b)

---

## Verification Matrix

| Cluster ID | Verdict | Notes |
|---|---|---|
| DEEP-01-001 (`_find_shield_component_id`) | VERIFIED-CLEAN | Zero test references; `_find_ability_component_id` is the superseding caller |
| DUP-X-02+06 (`iter_facility_ability_entries`) | VERIFIED-CLEAN | 9 call sites checked; generator shape matches all original loops |
| DUP-X-01 (`_resolve_player_planet`) | VERIFIED-CLEAN | 7 handlers migrated; new helper adds active-empire null guard (improvement) |
| Cluster 5 (`_apply_planet_environmental_target`) | VERIFIED-CLEAN | 4 handlers merged; atmosphere clear/set detection correct via `isinstance(value, dict) and not value` |
| DUP-X-07 / Cluster 11 (`_emit_validated_order`) | VERIFIED-CLEAN | 4 mission handlers routed through; return value preserves ValidationResult (MAJ-001 below) |
| DUP-X-05 (`RaceDescriptionLLMController._fields`) | VERIFIED-CLEAN | 6 @property shims read dict identically; external callers in `race_description_panel.py` and `llm_dialog_service.py` confirmed |
| Cluster 29+30 (`_get_ability_info` / `_get_ability_data_from_registry`) | VERIFIED-CLEAN | 3 thin wrappers preserve return shape; inline-abilities-first-then-registry logic equivalent |
| DUP-X-03 (`_apply_resolver_dropdown` + `_apply_confirmation_dropdown`) | VERIFIED-CLEAN | 5 handlers routed through 2 strategies; role uses registry-loop resolver correctly parameterized |
| DUP-X-04 (`_run_update_template`) | VERIFIED-CLEAN | 4-step template identical to original `update()` bodies; slider keys passed per-window |
| Cluster 6 (`_rebuild_modifier_icons_for_item`) | VERIFIED-CLEAN | Module-level helper accesses only item attrs both subclasses expose; thin wrappers pass `self` |

---

## Findings

### CRITICAL — None

No correctness regressions, crashes, data-loss scenarios, or broken call sites found.

---

### MAJOR — 1

#### MAJ-001: Mission handler `_emit_validated_order` returns `result` instead of `ValidationResult.success()`

**Files:** `game/strategy/engine/superweapon_command_handlers.py:246-248, 280-282, 315-317, 344-346`  
**Cluster:** DUP-X-07 / Cluster 11

The 4 mission handlers (StellerateStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere) were routed through `_emit_validated_order`. The old code at these call sites returned `ValidationResult.success()` unconditionally after queuing the order — discarding any warnings on the validation `result`. `_emit_validated_order` (at `handlers/base.py:254-273`) returns the original `result` parameter.

If any `SuperweaponValidator.validate_*` method ever returns a valid-but-with-warnings `ValidationResult` (not currently observed, but the type system permits it), the mission handlers now propagate those warnings to the caller instead of suppressing them. The Direct command handlers (`ImplodePlanetCommandHandler` et al.) also use `_emit_validated_order` and exhibit the same behavior, so this is at least internally consistent within the file.

**Risk:** Low. Current validators return either clean-success or error. However, `_emit_validated_order`'s contract says "Returns the same `result` so callers can `return self._emit_validated_order(...)`" which conflicts with the old mission-handler pattern of `return ValidationResult.success()`.

**Recommendation:** Either (a) document in `_emit_validated_order`'s docstring that it intentionally preserves the passed result (including warnings), or (b) have `_emit_validated_order` return `result if not result.is_valid else ValidationResult.success()`. Option (a) is preferred — the direct command handlers already rely on this behavior and the consistency is worth preserving.

---

### MINOR — 3

#### MIN-001: `ImplodePlanetMissionCommandHandler` not consolidated — duplicate of DUP-X-07 pattern

**Files:** `game/strategy/engine/superweapon_command_handlers.py:189-219`  
**Cluster:** DUP-X-07 (partial coverage)

The audit's DUP-X-07 finding covered line range 222-353, which excluded `ImplodePlanetMissionCommandHandler` (lines 186-219). This handler has the identical `Order(...) + fleet.add_order(...) + logger.info(...)` inline pattern that was consolidated in the other 4 mission handlers. After this project, the file contains 4 handlers using `_emit_validated_order` and 1 handler still using the old inline pattern — a maintenance inconsistency within the same file.

**Risk:** Low. The handler works correctly; this is a code-hygiene finding.

**Recommendation:** Route `ImplodePlanetMissionCommandHandler` through `_emit_validated_order` in a follow-up (trivial, 3-line change). The handler already validates early and returns on failure, so the emit call is safe.

---

#### MIN-002: `_collect_staging_capacity` duplicates list-normalization logic in `iter_facility_ability_entries`

**Files:** `game/strategy/engine/harvesting_engine.py:238-249`  
**Cluster:** Cluster 29+30

`_collect_staging_capacity` was not migrated to `iter_facility_ability_entries` while `_collect_storage_from_facility` and `_process_facility` were. The staging method still manually calls `_get_staging_info`, normalizes the result to a list, and iterates. The `iter_facility_ability_entries` generator would collapse this boilerplate the same way it did for storage and harvesting.

**Risk:** Low. The staging method has additional logic (list-vs-dict normalization that `iter_facility_ability_entries` already handles), but no behavior change.

**Recommendation:** Migrate `_collect_staging_capacity` to `iter_facility_ability_entries` in a follow-up for consistency with the other two loops in the same file.

---

#### MIN-003: `_get_ability_info` / `_get_ability_data_from_registry` have no dedicated tests

**Files:** `game/strategy/engine/harvesting_engine.py:38-91`  
**Cluster:** Cluster 29+30

The two new generic functions that replaced 4 duplicated helpers have zero direct unit tests. They are exercised indirectly through the `HarvestingEngine` integration tests and the 3 thin wrappers (`get_harvester_info`, `_get_storage_info`, `_get_staging_info`), but the edge cases (string component ID, missing registry, scalar ability data, inline-abilities-then-registry fallback ordering) are not individually verified.

**Risk:** Low. The thin wrappers are tested through existing engine tests, and the consolidation is a refactor of identical logic.

**Recommendation:** Add 4-5 unit tests for `_get_ability_info` covering: dict with inline abilities, dict with registry fallback, string component ID, missing ability, and scalar ability data that falls through to registry.

---

### INFO — 8

#### INFO-001: DUP-X-02+06 (`iter_facility_ability_entries`) — VERIFIED-CLEAN

The generator at `component_inspector.py:303-355` correctly normalizes ability data (dict yielded once, list yielded per element, non-dict list elements wrapped as `{"value": x}`, scalars wrapped as `{"value": x}`). All 9 call sites verified:

- **water_engine.py:53-56** — sums `entry.get('modification_rate', 0.0)`. Entry is always a dict; behavior identical.
- **atmosphere_engine.py:68-71** — same pattern, `modification_rate`.
- **quality_engine.py:62-63** — reads `resource_type` and `improvement_rate` per entry.
- **planet_energy_engine.py:207-217** — reads `resource` and `amount`/`generation_rate`; two passes (ResourceStorage + StrategicResourceGeneration) both correct.
- **planet_action_engine.py:314-323** (`_get_energy_drain_rate`) — filters to `comp_id` match, reads `energy_drain_rate`.
- **planet_action_engine.py:326-338** (`_get_deactivation_time`) — same filter, reads `deactivation_time`.
- **planet_action_engine.py:372-381** (`_find_ability_component_id`) — returns first component ID with the ability; previously used `_find_ability_component_id` which was the superseding caller.
- **harvesting_engine.py** (`_collect_storage_from_facility`, `_process_facility`) — remain on old wrappers, not migrated (see design decision: harvesting_engine uses `get_harvester_info` et al. thin wrappers rather than direct generator calls).

The test at `test_component_inspector.py:374-465` covers 9 cases: empty, inline dict, inline list, scalar wrap, missing ability, registry lookup by ID, string component, non-dict list entries, multiple components.

---

#### INFO-002: DUP-X-01 (`_resolve_player_planet`) — VERIFIED-CLEAN

The helper at `handlers/base.py:186-209` combines `_resolve_planet` + ownership check. It adds an `active_empire is None` guard that the 7 original inline sites lacked (they would have crashed with `AttributeError` on `session.active_empire.id`). This is a correctness improvement.

7 handlers migrated:
- `IssuePlanetOrderCommandHandler` (line 42)
- `ClearPlanetOrdersCommandHandler` (line 102)
- `DeletePlanetOrderCommandHandler` (line 117)
- `SetAtmosphereTargetCommandHandler` → via `_apply_planet_environmental_target` (Cluster 5)
- `SetGravityTargetCommandHandler` → via `_apply_planet_environmental_target` (Cluster 5)
- `SetWaterTargetCommandHandler` → via `_apply_planet_environmental_target` (Cluster 5)
- `SetRadiationShieldTargetCommandHandler` → via `_apply_planet_environmental_target` (Cluster 5)

Tests at `test_base_command_handler.py:129-183` cover: no active empire, planet not found, wrong owner, success.

---

#### INFO-003: Cluster 5 (`_apply_planet_environmental_target`) — VERIFIED-CLEAN

The 4 handlers (`SetAtmosphereTargetCommandHandler`, `SetGravityTargetCommandHandler`, `SetWaterTargetCommandHandler`, `SetRadiationShieldTargetCommandHandler`) were merged into a parameterized helper at `planet_command_handlers.py:129-160`.

Key equivalence points:
- **Atmosphere:** Original code always assigned `planet.atmosphere_target = dict(...)`; when empty always logged "cleared". New code: `target = dict(...) if ... else {}`, then `_apply_planet_environmental_target(value=target)`. The helper's `is_clear = (value is None) or (isinstance(value, dict) and not value)` correctly detects empty-dict as "clear". The `set_log` f-string with `{gases}` is computed at the call site before `dict()` is converted, so the gas count reflects the original `cmd.atmosphere_target`, not the post-convert empty dict.
- **Gravity/Water/Radiation:** Original code checked `if cmd.X_target is not None` for set vs clear. The helper's `is_clear = (value is None)` catches None values correctly. The `set_log` with inline f-strings is computed only for the set branch.

---

#### INFO-004: DUP-X-05 (`RaceDescriptionLLMController._fields`) — VERIFIED-CLEAN

The 6 `@property` shims at `race_description_llm_controller.py:140-164` all read from `self._fields["bio"]` or `self._fields["socio"]` correctly:
- `bio_status` → `self._fields["bio"].status`
- `socio_status` → `self._fields["socio"].status`
- `bio_error` → `self._fields["bio"].error`
- `socio_error` → `self._fields["socio"].error`
- `bio_elapsed_seconds` → `self._fields["bio"].call.elapsed_seconds` (with null guard)
- `socio_elapsed_seconds` → `self._fields["socio"].call.elapsed_seconds` (with null guard)

External callers confirmed unaffected:
- `race_description_panel.py:281-296` — reads all 6 properties for UI rendering
- `llm_dialog_service.py:68-134` — reads `bio_status`, `socio_status`, `bio_elapsed_seconds`, `socio_elapsed_seconds`, `bio_error`, `socio_error` for dialog status checking
- All are read-only `@property` access with no setter paths — zero risk of broken writes.

No external setters exist on the properties; internal state transitions go through `_fields[field_name].status`, `._call`, `._error` — all mutated through the parameterized private methods.

---

#### INFO-005: DUP-X-07 / Cluster 11 (`_emit_validated_order` mission handlers) — VERIFIED-CLEAN

4 mission handlers (StellerateStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere) now route through `_emit_validated_order` at `handlers/base.py:254-273`. The `ImplodePlanetMissionCommandHandler` was outside the audit scope (see MIN-001).

Each handler's old code:
```python
action_order = Order(OrderType.X, target=T)
fleet.add_order(action_order)
logger.info(f"GameSession: Queued X mission for Fleet {fleet.id}")
return ValidationResult.success()
```

New code:
```python
return self._emit_validated_order(fleet, OrderType.X, T, result, "X mission")
```

`_emit_validated_order` creates `Order(order_type, target=target)`, calls `fleet.add_order()`, and logs `"Issued %s order for Fleet %s"` (cosmetic log difference: "Queued" → "Issued ... order"). The return value difference is covered in MAJ-001.

All target shapes preserved: `None` (StellerateStar, CreateDysonSphere), `target_dict` (OpenWarpPoint, CloseWarpPoint).

---

#### INFO-006: DUP-X-03 (workshop dropdown consolidation) — VERIFIED-CLEAN

5 dropdown handlers routed through 2 shared helpers at `workshop_event_router.py:441-498`:

- **`_apply_resolver_dropdown`** (movement, targeting, role): The resolver parameterization correctly handles both options-list lookup (movement/targeting via `next((pid for pid, n in OPTIONS if n == name), None)`) and registry-loop iteration (role via `next((r.id for r in registry.all() if r.display_name == name), None)`). The `setter` callable dispatches to `viewmodel.set_ship_movement_policy`, `.set_ship_targeting_policy`, or `.set_ship_design_role`. Warning logging is preserved.

- **`_apply_confirmation_dropdown`** (class, vehicle_type): Preserves the no-change early return, the `gui.pending_action` assignment, the `has_components()` guard, and the dialog sizing/message/title parameterization. The dialog sizes (600x400 vs 400x200) and messages (refit warning vs clear-design warning) are preserved as parameters from each handler.

---

#### INFO-007: DUP-X-04 (`_run_update_template`) — VERIFIED-CLEAN

The shared 4-step template at `data_list_window_mixin.py:90-130` is byte-for-byte identical to the removed inline bodies in `planet_list_window.py` and `star_list_window.py`. Both windows now call `self._run_update_template(slider_keys)` with their respective key lists:
- Planet: `['gravity', 'temp', 'mass']`
- Star: `('mass', 'temperature', 'luminosity', 'age', 'radius_hexes')`

The 3 column-swap tests in `test_planet_list_components.py:767-801` were properly rewired to call `DataListWindowMixin._run_update_template(stub, [])` directly instead of calling through `PlanetListWindow.update()`. The assertions (swap_column called, rebuild_headers called, refresh_list called) remain valid.

---

#### INFO-008: Cluster 6 (`_rebuild_modifier_icons_for_item`) — VERIFIED-CLEAN

The module-level helper at `structure_list_items.py:25-80` accesses only `item.modifier_icons`, `item.ctx` (with `modifier_icon_service`, `config`, `manager`), `item.component` (with `.modifiers`), `item.height`, and `item.panel`. Both `IndividualComponentItem` and `LayerComponentItem` expose all these attributes identically. The thin wrapper methods at lines 254-260 and 496-504 both call `_rebuild_modifier_icons_for_item(self)` — correct.

---

## Test Coverage Assessment

| Area | Tests | Coverage |
|---|---|---|
| `iter_facility_ability_entries` | 9 cases in `test_component_inspector.py` | Adequate — covers empty, inline dict, inline list, scalar, missing, registry lookup, string ID, non-dict list entries, multi-component |
| `_resolve_player_planet` | 4 cases in `test_base_command_handler.py` | Adequate — covers null empire, missing planet, wrong owner, success |
| Dead method deletion | 0 tests reference `_find_shield_component_id` | Clean — no orphaned tests |
| Column-swap through mixin | 3 cases rewired in `test_planet_list_components.py` | Adequate — directly tests the consolidated path |
| `_get_ability_info` / `_get_ability_data_from_registry` | 0 direct tests | MIN-003 — exercised indirectly through engine integration |
| `_apply_planet_environmental_target` | 0 direct tests | Exercised through 4 handler tests indirectly |
| `_apply_resolver_dropdown` / `_apply_confirmation_dropdown` | 0 direct tests | Exercised through workshop UI integration tests |
| `_run_update_template` | 3 column-swap tests | Core path covered; slider/preset branches tested indirectly |
| `_rebuild_modifier_icons_for_item` | 0 direct tests | Exercised through UI builder tests |

**No orphaned tests found.** `_find_shield_component_id` had zero test references and was cleanly deleted. The column-swap tests were properly rewired. No tests monkey-patched any of the deleted methods or asserted on now-removed call shapes.

---

## PROJ-370 Compatibility Assessment

PROJ-370 (data-layer mutator protocols) will touch `planet_command_handlers.py`, `harvesting_engine.py`, `handlers/base.py`. The new shared helpers:

- **`_resolve_player_planet` (handlers/base.py)** — Single resolution entry point for all planet handlers. Makes mutator routing *easier*: PROJ-370 can intercept at one method instead of 7 identical inline sites.
- **`_apply_planet_environmental_target` (planet_command_handlers.py)** — Single `setattr(planet, attribute, value)` site for target-setting. Makes mutator routing *easier*.
- **`_get_ability_info` / `_get_ability_data_from_registry` (harvesting_engine.py)** — Two generic data-extraction functions replacing 4 duplicated helpers. No impact on mutator routing — these are read-only extractors, not state-changers.

**Verdict:** PROJ-375 makes PROJ-370's work uniformly easier by reducing the number of sites that need mutator routing.

---

## Public Surface Preservation

- **DUP-X-05**: 6 `@property` shims preserved. All external call sites (`race_description_panel.py`, `llm_dialog_service.py`) confirmed reading properties only. Zero breakage.
- **All other consolidations**: No public API changes. The new helpers (`_resolve_player_planet`, `_apply_planet_environmental_target`, `iter_facility_ability_entries`, etc.) are either private (`_`-prefixed) or module-level utility functions in existing service modules. No public surface contraction.

---

## Band-aid / God-function Assessment

None of the new helpers exhibit god-function characteristics:
- **`iter_facility_ability_entries`** — Single responsibility: yield normalized ability entries. Callers keep their own field arithmetic. The callback-free design (yield component alongside entry) avoids parameter proliferation.
- **`_apply_planet_environmental_target`** — 6 parameters (5 + `self`/session context). Clean: resolve, set, log. No branching beyond the clear/set log choice.
- **`_apply_resolver_dropdown`** / `_apply_confirmation_dropdown`** — Each has a clear single strategy. The design intentionally split confirmation from resolution rather than forcing one god-dispatcher.
- **`_get_ability_info`** — Straightforward extractor with one branch (inline vs registry). Not over-parameterized.
- **`_rebuild_modifier_icons_for_item`** — Module-level function with duck-typed `item` parameter. Alternative (mixin) was considered and rejected in decisions.md for good reason (single method on two unrelated classes does not justify a mixin).

---

## Summary

| Severity | Count |
|---|---|
| CRITICAL | 0 |
| MAJOR | 1 |
| MINOR | 3 |
| INFO | 8 |

**Overall Verdict:** All 10 consolidated clusters are semantically correct. No regressions, no broken call sites, no orphaned tests. One MAJOR finding (return-value effect of `_emit_validated_order`) is low-risk and internally consistent. Three MINOR findings identify follow-up cleanup opportunities (the 5th mission handler, staging capacity migration, missing unit tests for `_get_ability_info`). PROJ-370 compatibility is improved by the consolidations.

**Recommendation:** PROJ-375 is safe to merge. Address MAJ-001 (docstring clarification) before closing. MIN-001 through MIN-003 are low-priority follow-ups.
