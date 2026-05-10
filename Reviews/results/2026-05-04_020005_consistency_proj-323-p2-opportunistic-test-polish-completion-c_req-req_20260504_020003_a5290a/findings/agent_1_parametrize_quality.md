# Agent 1 Report: Parametrize Sweep Quality & Threshold Rule

## 1. Parametrize Consolidation Spot-Checks

### Task 3.13: test_defense_isolation.py — ToHitAttackModifier/ToHitDefenseModifier collapse

- **Quality assessment:** GOOD
- **Discoverability:** Class-level parametrize with `id='ToHitAttackModifier'` / `id='ToHitDefenseModifier'`. Pytest output shows as `TestToHitModifier::test_init_with_positive_value[ToHitAttackModifier]` — trivially greppable by ability class name.
- **Error message preservation:** Each test receives distinct `label` and `color_hint` values from the parametrize. If one ability class diverges (e.g. ToHitAttackModifier changes its `ui_label` but ToHitDefenseModifier does not), pytest flags only the failing variant by ID. The `TestToHitAttackModifierExtras` class (line 424, 1 test) cleanly isolates the sole divergent behavior (`test_init_with_float_value`).
- **Hidden cases risk:** Low. The IDs map directly to class names. No shared fixture mutation between variants.

```python
@pytest.mark.parametrize("ability_cls,label,color_hint", [
    pytest.param(ToHitAttackModifier, 'Targeting', HINT_DAMAGE, id='ToHitAttackModifier'),
    pytest.param(ToHitDefenseModifier, 'Evasion', HINT_EVASION, id='ToHitDefenseModifier'),
])
class TestToHitModifier:
    def test_get_ui_rows_positive_value(self, mock_component, ability_cls, label, color_hint):
        ability = ability_cls(mock_component, 5)
        rows = ability.get_ui_rows()
        assert rows[0]['label'] == label
        assert rows[0]['color_hint'] == color_hint
```

---

### Task 3.16: test_system_stabilizers.py — Stellar/Warp Stabilizer collapse

- **Quality assessment:** GOOD
- **Discoverability:** IDs are full class names (`StellarStabilizer`, `WarpFieldStabilizer`). Clear and searchable.
- **Error message preservation:** Each variant carries its own numeric defaults (drain, activation, deactivation). `test_construction_from_dict` asserts per-variant expected values; `test_defaults` asserts shared defaults (0.0, `AbilityScope.SYSTEM`). Failures are correctly scoped to the variant.
- **Hidden cases risk:** Negligible. The two stabilizers differ only in defaults; behavioral logic is identical. No special-case test class needed post-parametrize (both stabilizers share all 6 test methods).

```python
@pytest.mark.parametrize(
    "ability_cls,drain,activation,deactivation",
    [
        pytest.param(StellarStabilizerAbility, 250.0, 100, 20, id="StellarStabilizer"),
        pytest.param(WarpFieldStabilizerAbility, 150.0, 75, 15, id="WarpFieldStabilizer"),
    ],
)
class TestStabilizerAbility:
    def test_construction_from_dict(self, ability_cls, drain, activation, deactivation):
        ...
        assert ability.energy_drain_rate == drain
```

---

### Task 3.19: test_modifier_service.py — turret_mount initial-value & min/max parametrization

- **Quality assessment:** GOOD
- **Discoverability:** Four separate parametrize blocks, each with descriptive IDs (`projectile_weapon_ability`, `beam_weapon_ability`, `root_firing_arc`, `fallback_to_min_val`). Clear what each case tests.
- **Error message preservation:** Good. Identical `projectile_weapon_ability` / `beam_weapon_ability` ID pairs appear in both the initial-value and min/max blocks, so a cross-method failure is easy to correlate.
- **Hidden cases risk:** None. The parametrized blocks test the two standard weapon types (projectile/beam) and the data-fallback paths. Non-parametrized tests (`test_turret_mount_finds_firing_arc_in_novel_weapon_ability`, the entire `TestArcSetEffectDetection` class) cover generic effect-based arc detection, including custom modifiers — cases the parametrize blocks intentionally don't cover. No gap.
- **Minor naming inconsistency:** The initial-value fallback ID is `fallback_to_min_val` while the min/max fallback ID is `fallback_to_modifier_min`. Same conceptual case; cosmetic divergence only.

```python
# Two of four turret_mount parametrize blocks (initial_value + min/max):
@pytest.mark.parametrize("comp_fixture,expected_value", [
    pytest.param("mock_weapon_component", 30.0, id="projectile_weapon_ability"),
    pytest.param("mock_beam_component", 45.0, id="beam_weapon_ability"),
])
def test_turret_mount_uses_ability_firing_arc(self, full_registry, request, comp_fixture, expected_value):
    comp = request.getfixturevalue(comp_fixture)
    service = ModifierService(modifier_registry=full_registry)
    assert service.get_initial_value('turret_mount', comp) == expected_value

@pytest.mark.parametrize("data,expected_value", [
    pytest.param({'firing_arc': 60, 'abilities': {}}, 60.0, id="root_firing_arc"),
    pytest.param({'abilities': {}}, 15.0, id="fallback_to_min_val"),
])
def test_turret_mount_initial_value_from_data(self, full_registry, data, expected_value):
    ...
```

---

### Task 3.33: test_modifier_resolver.py — 7 resolve_size_multiplier cases

- **Quality assessment:** GOOD
- **Discoverability:** Seven distinct IDs: `size_mount_0_2`, `size_mount_1_0`, `no_modifiers_key`, `empty_modifiers_list`, `other_modifiers_only`, `string_entry`, `multiple_modifiers`. Each ID describes the fixture shape, not just the expected value — good practice.
- **Error message preservation:** Each case has a unique expected value and unique input shape. Pytest clearly identifies which ID failed and its parameters.
- **Hidden cases risk:** The `string_entry` case (passing bare `"metal_harvester"` string instead of dict) is a regression-significant edge case. The parametrize makes it explicit and visible alongside the other cases; it would be easy to overlook if it were a standalone test. The `multiple_modifiers` case (hardened_mount + simple_size_mount in list) verifies correct extraction from mixed modifier lists. No hidden cases.

```python
@pytest.mark.parametrize("comp_entry,expected", [
    pytest.param({"id": "metal_harvester", "modifiers": [{"id": "simple_size_mount", "value": 0.2}]}, 0.2, id="size_mount_0_2"),
    pytest.param({"id": "metal_harvester"}, 1.0, id="no_modifiers_key"),
    pytest.param({"id": "metal_harvester", "modifiers": []}, 1.0, id="empty_modifiers_list"),
    pytest.param("metal_harvester", 1.0, id="string_entry"),
    pytest.param({..., "modifiers": [{"id": "hardened_mount", ...}, {"id": "simple_size_mount", "value": 0.5}]}, 0.5, id="multiple_modifiers"),
])
def test_resolve_size_multiplier(self, fresh_registries, comp_entry, expected):
    result = resolve_size_multiplier(comp_entry)
    assert result == pytest.approx(expected)
```

---

### Task 3.44: test_superweapon_input_modes.py — mode-setting & click-routing clusters

- **Quality assessment:** GOOD
- **Discoverability:** Mode-setting and click-routing parametrize blocks use descriptive IDs matching superweapon names (`implode_planet`, `stellerate_star`, etc.). Cancel-mode parametrize blocks use bare mode strings (pytest auto-generates IDs from them — acceptable since mode names are distinctive).
- **Error message preservation:** If a new superweapon mode diverges in behavior, only its parametrize variant fails. The mode-setting block tests `input_mode` assignment; the click-routing block tests delegation + reset. Failures in either are clearly scoped.
- **Hidden cases risk:** None. `test_self_destruct_calls_handler` (line 70, NOT parametrized) correctly isolates SELF_DESTRUCT (which calls a handler directly, not a target-input mode). The 4 parametrize blocks cover distinct behavioral dimensions (mode set, ESC cancel, left-click route, right-click cancel) — no overlap confusion.
- **Minor note:** The cancel-mode parametrize blocks (lines 94-100 and 145-151) use bare strings instead of `pytest.param(..., id=...)`. Same effect because mode strings are unique, but inconsistent with the style used in blocks 1 and 3 of the same file.

```python
@pytest.mark.parametrize("input_action,expected_mode", [
    pytest.param(InputAction.FLEET_IMPLODE_PLANET, 'IMPLODE_PLANET_TARGET', id="implode_planet"),
    pytest.param(InputAction.FLEET_STELLERATE_STAR, 'STELLERATE_STAR_TARGET', id="stellerate_star"),
    # ... 5 total
])
def test_input_action_sets_corresponding_mode(self, handler_with_mapper, input_action, expected_mode):
    ...

@pytest.mark.parametrize("mode,handler_attr", [
    pytest.param('IMPLODE_PLANET_TARGET', 'handle_implode_planet_designation', id="implode_planet"),
    # ... 5 total, same IDs across both blocks
])
def test_click_delegates_to_superweapons(self, handler, mode, handler_attr):
    ...
```

---

## 2. ≥3-Member Threshold Rule Audit

### Task 3.15: test_static_value_ability.py

- **Original cluster:** Two concrete-subclass test classes — `TestToHitAttackModifierIsStaticValue` (4 tests) and `TestToHitDefenseModifierIsStaticValue` (3 tests). Both verify identical properties (inheritance, class attributes, UI format) but for different concrete subclasses. They mirror the pattern already parametrized in Task 3.13 (`TestToHitModifier` in `test_defense_isolation.py`).
- **Assessment:** CORRECTLY LEFT — borderline, but defensible.
- **Rationale:** Only 2 subclasses. While they share 3 test patterns (`test_inherits_from_...`, `test_class_attributes`, `test_positive_value_format`), the third subclass (`TestEmissiveArmorIsStaticValue`, 4 tests) tests genuinely different behaviors (`int_result`, `test_int_cast`, `test_ui_format`) and cannot share the same parametrize template. Collapsing only the 2 Attack/Defense classes would create an inconsistent split (2-in-1 parametrize + 1 standalone). The cleaner choice is keeping all three as separate test classes, consistent with the ≥3 rule. However, the earlier Task 3.13 precedent (parametrizing exactly 2 ability classes) suggests a 2-member parametrize CAN work well, so this is a judgment call.

---

### Task 3.27: test_population_model.py

- **Original cluster:** Two `max_population` tests — `test_planet_max_population_earth_like` (line 102) and `test_planet_max_population_small_body` (line 112). Both test `planet.max_population` with different planet fixtures and expected values.
- **Assessment:** CORRECTLY LEFT — with a note.
- **Rationale:** Only 2 planet types. However, each test has formula-derivation comments (lines 103-106 and 113-116 explaining `surface_area / 1_000_000 * 100 / 1000`) that provide essential context for the expected values. Parametrizing would lose per-case docstring/comment context or force it into less-readable parametrize IDs. A third planet type would make parametrization clearly preferable. As-is the two standalone tests are clear and self-documenting.

---

### Task 3.37: test_fleet_consumable_aggregator.py

- **Original cluster:** Multiple True/False and zero/negative variant pairs throughout the file:
  1. `test_has_resources_for_movement_true` / `test_has_resources_for_movement_false` (lines 84, 93)
  2. `test_has_resources_for_warp_true` / `test_has_resources_for_warp_false` (lines 191, 200)
  3. `test_consume_returns_true_on_success` / `test_consume_returns_false_when_insufficient` (lines 118, 127)
  4. `test_consume_warp_returns_true_on_success` / `test_consume_warp_returns_false_when_insufficient` (lines 217, 226)
  5. `test_verify_only_returns_true_...` / `test_verify_only_returns_false_...` (lines 659, 675)
  6. `test_load_cargo_zero_amount_returns_zero` / `test_load_cargo_negative_amount_returns_zero` (lines 370, 379)
  7. `test_unload_cargo_zero_amount_returns_zero` / `test_unload_cargo_negative_amount_returns_zero` (lines 397, 406)
- **Assessment:** SHOULD PARAMETRIZE (minor) — pairs 6 and 7 are the strongest candidates.
- **Rationale:** Pairs 1-5 test boolean outcomes (True/False) from resource verification. Arguably these could be parametrized, BUT: (a) the True/False cases often have different docstring narratives and assertion semantics (e.g. `assert result is True` vs `assert result is False` are trivially parametrizable, but the surrounding narrative differs), and (b) several have a third variant (empty fleet) that cannot share the same parametrize without contortions. However, pairs 6 and 7 (zero/negative cargo amounts) are textbook 2-member parametrize candidates — identical logic, only differing by the sentinel value. These would be cleaner as:

  ```python
  @pytest.mark.parametrize("amount", [0, -50], ids=["zero", "negative"])
  def test_load_cargo_invalid_amount_returns_zero(self, resource_aggregator, mock_fleet, mock_ship, amount):
      ...
      assert result == 0
      mock_ship.load_cargo.assert_not_called()
  ```

  The ≥3 threshold rule deterred this consolidation; the result is 4 nearly-identical test methods where 2 would suffice.

---

## 3. Findings Summary

| ID | Severity | Description |
|----|----------|-------------|
| FND-P1-001 | MIN | Task 3.19: `fallback_to_min_val` vs `fallback_to_modifier_min` — inconsistent IDs for the same conceptual fallback case across initial_value and min/max parametrize blocks in `test_modifier_service.py`. |
| FND-P1-002 | MIN | Task 3.44: Cancel-mode parametrize blocks use bare strings without `pytest.param(..., id=...)`, inconsistent with the mode-setting and click-routing blocks in the same file (`test_superweapon_input_modes.py:94-110`, `test_superweapon_input_modes.py:145-158`). |
| FND-P1-003 | MIN | Task 3.37: zero/negative cargo amount pairs (4 tests across load/unload in `test_fleet_consumable_aggregator.py:370-413`) are ideal 2-member parametrize candidates. The ≥3 threshold prevented consolidation that would improve clarity and reduce line count without losing discoverability. |
| FND-P1-004 | INFO | All 5 parametrize spot-checks pass quality review. Discoverability and error message preservation are preserved in every case. No regression-significant case is hidden behind an un-greppable parametrize ID. The pattern of `pytest.param(..., id=<descriptive_name>)` is consistently applied in the core blocks. |
| FND-P1-005 | INFO | Tasks 3.15 and 3.27 correctly enforce the ≥3 threshold. The two borderline cases have defensible rationales for keeping standalone tests (subclass divergence in 3.15, formula-documentation context in 3.27). Task 3.37's cargo zero/negative pairs are the only clear missed opportunity. |
