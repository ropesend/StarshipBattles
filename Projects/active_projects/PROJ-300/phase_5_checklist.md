# Phase 5: Storm dataclass + JSON schema migration

**Status:** Not Started
**Objective:** Replace `Storm.effects: StormEffect` with `Storm.abilities: Dict[str, Any]`. Rewrite `data/storms.json` → `data/storm_types.json` with the v2.0 abilities-shaped schema. Update generator and roundtrip tests. After this phase, the storm path is fully expressed in abilities-dict form (but old AreaEffectManager code still exists; Phase 6/7 remove it).

---

## Tasks

### Task 5.1: Rename and rewrite `data/storms.json` → `data/storm_types.json` [Simple]
**File:** `data/storm_types.json` (NEW); delete `data/storms.json` after rewrite.
**Tests:** Manual JSON validation; covered by 5.3.

- [ ] Copy `data/storms.json` to `data/storm_types.json`.
- [ ] For each of the 5 storm types, replace the `effects` block with an `abilities` block per the schema in [design.md](design.md). E.g. for `ion_storm`:
  ```json
  "abilities": {
    "ShieldModifier":         {"multiplier": 0.5, "scope": "sector"},
    "StrategicSpeedModifier": {"multiplier": 0.8, "scope": "sector"}
  }
  ```
- [ ] Bump `"version"` to `"2.0"` and update the `description` to reflect "abilities-shaped storm types".
- [ ] **Do not delete `data/storms.json` yet** — keep until Task 5.4 confirms generator works against the new file.

**Notes:**

### Task 5.2: Update `Paths` constant for the storms file [Simple]
**File:** `game/core/paths.py`
**Tests:** `pytest tests/unit/core/test_paths.py` (if exists)

- [ ] If `Paths.STORMS_FILE` exists, rename to `Paths.STORM_TYPES_FILE` and point to `data/storm_types.json`.
- [ ] If callers reference the old constant, update them (rg `STORMS_FILE`).

**Notes:**

### Task 5.3: Replace `StormEffect` with `abilities: Dict[str, Any]` on `Storm` [Medium]
**File:** `game/strategy/data/storm.py`
**Tests:** `pytest tests/unit/strategy/data/test_storm.py`

- [ ] Failing tests first (rewrite existing roundtrip tests):
  - [ ] `test_storm_carries_abilities_dict_not_storm_effect`
  - [ ] `test_storm_to_dict_roundtrips_abilities`
  - [ ] `test_storm_from_dict_reads_abilities` — new fixture data uses abilities shape.
  - [ ] `test_storm_from_dict_rejects_legacy_effects_field` (per decisions.md: saves are disposable, no shim).
- [ ] Modify `Storm` dataclass: `effects: StormEffect` → `abilities: Dict[str, Any]`.
- [ ] Delete the `StormEffect` class entirely (lines 16-63). Note: this leaves `area_effect_manager.py` broken — the broken state is acceptable until Phase 7 deletes that file. Mark Phase 7 as a hard prerequisite for any push.
- [ ] Update `Storm.to_dict` / `from_dict` to serialize `abilities`. New shape:
  ```python
  {'name': ..., 'storm_type': ..., 'location': ..., 'hex_offsets': ..., 'abilities': {...}, ...}
  ```
- [ ] Update `IStorm` protocol in `game/core/protocols.py` (lines 440-461): replace `effects` attribute with `abilities`. Update `is_storm()` TypeGuard's attribute check.
- [ ] Update `StormAbilitySource` (created in Phase 3) to read `storm.abilities` directly — drop any temporary `effects` translation.
- [ ] Run tests — confirm new tests green; old `effects`-based tests removed.

**Notes:**

### Task 5.4: Update `StormGenerator` to produce `abilities`-shaped storms [Medium]
**File:** `game/strategy/generation/storm_generator.py`
**Tests:** `pytest tests/unit/strategy/generation/test_storm_generator.py`

- [ ] Failing tests:
  - [ ] `test_generated_storm_has_abilities_dict_not_effects`
  - [ ] `test_generator_reads_storm_types_json` — confirm new file path.
  - [ ] `test_generated_ion_storm_has_shieldmodifier_and_strategicspeedmodifier`
- [ ] Update generator to:
  - Load `data/storm_types.json` (using `Paths.STORM_TYPES_FILE`).
  - Copy the type's `abilities` dict into the new Storm instance (deep copy — don't share dict references between instances).
  - Drop all `StormEffect` construction code.
- [ ] Run tests — green.
- [ ] Now safe to delete `data/storms.json` (the old file).

**Notes:** Future projects (PROJ-301..304) may add roll-time random ranges for ability values. Current storms.json doesn't use them — keep generator simple and deterministic for this project; ranges are an additive feature.

### Task 5.5: Update save/load roundtrip integration tests [Simple]
**File:** `tests/integration/save_load/test_roundtrip_storms.py`
**Tests:** `pytest tests/integration/save_load/test_roundtrip_storms.py`

- [ ] Update fixture data and assertions to the new abilities shape.
- [ ] Confirm a generated galaxy with storms saves and loads cleanly.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/unit/strategy/data/test_storm.py tests/unit/strategy/generation/test_storm_generator.py tests/integration/save_load/test_roundtrip_storms.py` all green
- [ ] `pytest tests/ --testmon` — note: `area_effect_manager.py` and `_entries_from_environmental_effects` are now BROKEN (they reference deleted `StormEffect`). This is expected; Phase 6/7 fix the consumers and delete AreaEffectManager. Do NOT push between phases — implement 5+6+7 contiguously.
- [ ] Update status to `Complete`
- [ ] Update plan.md
