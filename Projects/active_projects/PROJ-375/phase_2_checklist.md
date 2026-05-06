# Phase 2: Strategy-layer duplication consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-375 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate 6 verified duplication clusters in the strategy layer (DUP-X-01, DUP-X-02+06, DUP-X-05, DUP-X-07 + Cluster 11, Cluster 5, Cluster 29+30) identified by audit `2026-05-05_185819_audit_shrink`.

Recommended task order: Task 2.1 (DUP-X-02+06) creates the generic ability-field helper that the rest of the file-level cleanup in `planet_action_engine.py` builds on; Task 2.2 (DUP-X-01) creates the `_resolve_player_planet` helper that Task 2.3 (Cluster 5) reuses. The other tasks are independent.

---

## Tasks

### Task 2.1: Generic ability-field helper (DUP-X-02 + DUP-X-06) [Medium]
**File:** `game/strategy/services/component_inspector.py` (new helper) + 8 call-site files
**Tests:** `pytest tests/unit/strategy/services/test_component_inspector.py tests/unit/strategy/engine/`

Add `get_ability_field_from_facility(facility, ability_name, field_name, default, registries)` to `component_inspector.py` (already hosts the related `extract_abilities_from_component`). Migrate the 8 sites that hand-roll the iterate→extract→read-field pattern. Folds DUP-X-06 (the 4 ability-extraction variants in `planet_action_engine.py`) into the same migration since they are the same pattern in one file.

**Migration nuances flagged by second-pass verification (see [findings/verification_report.md](findings/verification_report.md)):**
- `harvesting_engine.py` sites go through `_get_staging_info` / `_get_storage_info` wrappers — **sequence Task 2.1 BEFORE Task 2.6** (Cluster 29+30 consolidation), or fold the harvesting migrations into Task 2.6.
- `harvesting_engine.py:258` applies `resolve_size_multiplier()` to the component before reading the field. The new helper must accept either a multiplier callback OR the caller pre-applies — record the choice in `decisions.md` before implementing.
- `build_queue_source.py:142` is a boolean "any component has X" check, NOT field extraction. **Removed from this task's scope** — fits a separate `facility_has_ability(...)` helper if a follow-up wants to add it.
- `empire_economy_calculator.py:229` and `strategy_detail_formatter.py:314` were not directly read by either verification pass — re-confirm the pattern matches before migrating each.

- [ ] Add `get_ability_field_from_facility` to `game/strategy/services/component_inspector.py` with unit tests in `tests/unit/strategy/services/test_component_inspector.py`
- [ ] Decide multiplier-callback vs caller-pre-applies shape for `harvesting_engine.py:258`; record in `decisions.md`
- [ ] Migrate `game/strategy/engine/planet_action_engine.py:296-340, 376-380` — collapses `_get_energy_drain_rate`, `_get_deactivation_time`, and the 2 other ability-extraction variants (DUP-X-06)
- [ ] Migrate `game/strategy/engine/water_engine.py:53,82`
- [ ] Migrate `game/strategy/engine/quality_engine.py:62,94`
- [ ] Migrate `game/strategy/engine/atmosphere_engine.py:68,142`
- [ ] Migrate `game/strategy/engine/planet_energy_engine.py:206`
- [ ] Migrate `game/strategy/engine/harvesting_engine.py:218,258,357` — coordinate with Task 2.6
- [ ] Migrate `game/strategy/engine/empire_economy_calculator.py:229` — re-confirm pattern first
- [ ] Migrate `game/ui/screens/strategy_detail_formatter.py:314` — re-confirm pattern first
- [ ] Verify: full sharded suite passes
- [ ] Verify: LOC delta ≈ -90 (DUP-X-02 ~70 net of dropped site + DUP-X-06 ~20)

**Notes:**

---

### Task 2.2: `_resolve_player_planet` helper (DUP-X-01) [Simple]
**File:** `game/strategy/engine/handlers/base.py` + `game/strategy/engine/planet_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_command_handlers.py tests/unit/strategy/engine/handlers/`

Add `BaseCommandHandler._resolve_player_planet(session, planet_id)` mirroring the existing `_resolve_player_fleet` (defined at `handlers/base.py:135-156`). Refactor 7 handlers in `planet_command_handlers.py` to use it.

- [ ] Add `_resolve_player_planet` to `game/strategy/engine/handlers/base.py` with unit tests in `tests/unit/strategy/engine/handlers/test_base.py`
- [ ] Refactor handler at `planet_command_handlers.py:47` (IssuePlanetOrder) to use `_resolve_player_planet`
- [ ] Refactor handler at `planet_command_handlers.py:110` to use `_resolve_player_planet`
- [ ] Refactor handler at `planet_command_handlers.py:128` to use `_resolve_player_planet`
- [ ] Refactor handler at `planet_command_handlers.py:149` (SetAtmosphereTarget) to use `_resolve_player_planet`
- [ ] Refactor handler at `planet_command_handlers.py:170` (SetGravityTarget) to use `_resolve_player_planet`
- [ ] Refactor handler at `planet_command_handlers.py:191` (SetWaterTarget) to use `_resolve_player_planet`
- [ ] Refactor handler at `planet_command_handlers.py:212` to use `_resolve_player_planet`
- [ ] Verify: `pytest tests/unit/strategy/engine/test_planet_command_handlers.py` passes
- [ ] Verify: LOC delta ≈ -14

**Notes:**

---

### Task 2.3: Merge 3 SetPlanetEnvironmentalTarget handlers (Cluster 5) [Medium]
**File:** `game/strategy/engine/planet_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_command_handlers.py`

`SetAtmosphereTargetCommandHandler`, `SetGravityTargetCommandHandler`, and `SetWaterTargetCommandHandler` (lines 142-199) are identical except for the attribute name and log format. Merge into a single `SetPlanetEnvironmentalTargetCommandHandler` parameterized by attribute. Builds on Task 2.2 (will use `_resolve_player_planet`).

- [ ] Introduce parameterized `SetPlanetEnvironmentalTargetCommandHandler` (or attribute-driven helper) consolidating the 3 handlers at `planet_command_handlers.py:142-199`
- [ ] Update command-handler registration / dispatch table for the 3 command types
- [ ] Update or replace tests covering each of the 3 commands in `tests/unit/strategy/engine/test_planet_command_handlers.py`
- [ ] Verify: `pytest tests/unit/strategy/engine/test_planet_command_handlers.py` passes
- [ ] Verify: LOC delta ≈ -30

**Notes:**

---

### Task 2.4: Refactor superweapon handlers to use `_emit_validated_order` (DUP-X-07 + Cluster 11) [Simple]
**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

The helper `BaseCommandHandler._emit_validated_order` already exists at `handlers/base.py:228-247` (added by PROJ-319 specifically for this pattern), but the 4 superweapon mission handlers still manually create `Order(...)` and call `fleet.add_order(...)`. Cluster 11 is the same 4 handlers grouped by `target` shape (None vs dict) and is resolved automatically as part of this refactor — no separate task needed.

- [ ] Refactor `StellerateStarMissionCommandHandler.execute` (lines 222-250) to call `self._emit_validated_order(...)`
- [ ] Refactor `OpenWarpPointMissionCommandHandler.execute` (lines 253-286) to call `self._emit_validated_order(...)`
- [ ] Refactor `CloseWarpPointMissionCommandHandler.execute` (lines 289-322) to call `self._emit_validated_order(...)`
- [ ] Refactor `CreateDysonSphereMissionCommandHandler.execute` (lines 325-353) to call `self._emit_validated_order(...)`
- [ ] Verify: `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py` passes
- [ ] Verify: LOC delta ≈ -45

**Notes:**

---

### Task 2.5: Unify race description bio/socio axis (DUP-X-05) [Simple]
**File:** `game/strategy/services/race_description_llm_controller.py`
**Tests:** `pytest tests/unit/strategy/services/test_race_description_llm_controller.py tests/unit/ui/panels/test_race_description_panel.py tests/unit/ui/screens/race_setup/test_llm_dialog_service.py`

`_start_bio` / `_start_socio` (lines 198-237) and `_apply_bio_transition` / `_apply_socio_transition` (lines 266-308) are mirror methods. Replace the mirrored attribute pairs (`_bio_call`/`_socio_call`, `_bio_status`/`_socio_status`, `_bio_error`/`_socio_error`) with a `_fields: dict[str, FieldState]` dict; collapse start/transition to field-parameterized methods.

**Public API preservation (mandatory — flagged by second-pass verification):** The controller exposes 6 `@property` accessors at lines 107-128 (`bio_status`, `socio_status`, `bio_error`, `socio_error`, `bio_elapsed_seconds`, `socio_elapsed_seconds`). These are read by `game/ui/panels/race_description_panel.py` (set_state + update) and `game/ui/screens/race_setup/llm_dialog_service.py` (check_dialog_thresholds + check_error_popups). The 6 public properties MUST remain after the refactor — they should become thin shims reading from `_fields["bio"]` / `_fields["socio"]`.

- [ ] Define `FieldState` dataclass (call, status, error, prompt_builder, race attribute name)
- [ ] Replace 6 mirrored underscore attributes with `_fields: dict[str, FieldState]`
- [ ] Keep all 6 public properties (`bio_status`, `socio_status`, `bio_error`, `socio_error`, `bio_elapsed_seconds`, `socio_elapsed_seconds`) as thin shims reading from `_fields`
- [ ] Collapse `_start_bio` + `_start_socio` to `_start_field(field_name)`
- [ ] Collapse `_apply_bio_transition` + `_apply_socio_transition` to `_apply_field_transition(field_name, ...)`
- [ ] Verify: existing call sites still work — `pytest tests/unit/ui/panels/test_race_description_panel.py tests/unit/ui/screens/race_setup/test_llm_dialog_service.py` passes
- [ ] Verify: `pytest tests/unit/strategy/services/test_race_description_llm_controller.py` passes
- [ ] Verify: LOC delta ≈ -55

**Notes:**

---

### Task 2.6: Generic ability-info helper in harvesting engine (Cluster 29+30) [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

`get_harvester_info` (line 38) and `_get_storage_info` (line 274) are top-level wrappers that differ only in the ability key (`ResourceHarvester` vs `LocalStorage`). Same applies to `get_harvester_from_registry` (line 67) and `_get_storage_from_registry` (line 301). Consolidate into a generic `_get_ability_info(comp, ability_name, registries)` plus a registry-lookup variant.

- [ ] Introduce generic `_get_ability_info(comp, ability_name, registries)` and `_get_ability_data_from_registry(comp_id, registries, ability_name)` helpers
- [ ] Replace `get_harvester_info` (line 38) and `_get_storage_info` (line 274) with thin wrappers
- [ ] Replace `get_harvester_from_registry` (line 67) and `_get_storage_from_registry` (line 301) with thin wrappers
- [ ] Verify: `pytest tests/unit/strategy/engine/test_harvesting_engine.py` passes
- [ ] Verify: LOC delta ≈ -25

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-05_185819_audit_shrink/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
