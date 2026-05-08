# Verification Report — PROJ-380

**Source audit:** `Reviews/results/2026-05-07_220215_audit_shrink/`
**Run date:** 2026-05-08
**Batch summary:** 11 verified / 1 rejected / 1 uncertain (out of 13 audit verified-safe candidates)

The audit's "verified-safe" bucket consisted of 1 dead import (Section 3 Tier 4) plus 12 CRITICAL/MAJOR duplications (Section 4). The MINOR/INFO duplications (DUP-X-13 through DUP-X-22), the PRODUCT_DECISION items, and the complexity hotspots (Section 5) were excluded by protocol and never re-verified.

---

## Verified

| ID | File | Symbol / Sites | Recommendation |
|----|------|----------------|----------------|
| DCV-01 | `game/ai/controller.py:56,86` | `IControllableShip` import + string annotation | Remove import; rewrite annotation to `'ShipControllableAdapter'`. |
| DUP-X-01 | `game/strategy/engine/superweapon_command_handlers.py:252-438` | 5 mission command handlers | Extract `MissionCommandHandler` template. |
| DUP-X-02 | `game/services/llm/factory.py:52-87`, `game/ui/services/image/factory.py:47-79` | LLM + Image factory `create` | Extract shared `ProviderFactory` base. |
| DUP-X-05 (scope-reduced) | `game/simulation/components/modifier_manager.py:223-330` | `add_modifier_static`, `remove_modifier_static`, `get_modifier_static`, `get_all_effects_static`, `get_stat_summary_static` | Delete the 5 deprecated statics. **Preserve `remove_modifier_inplace`** unless re-grep confirms zero non-deprecated callers. |
| DUP-X-06 | `game/strategy/data/fleet_consumable_aggregator.py:291-341` | `load_cargo_to_fleet`, `unload_cargo_from_fleet` | Extract `_distribute_cargo_to_fleet` helper. |
| DUP-X-07 (with caveat) | `game/ui/screens/strategy_click_dispatcher.py:125-300` | 9 click-mode handlers | Extract `_handle_input_mode_click` base; route `_handle_edit_move_click`'s extra state resets via an `on_cancel` callback. |
| DUP-X-08 | `game/ui/screens/strategy_superweapons.py:78-309` (5 sites) + 11 `pixel_to_hex` sites across 5 files | 5 designation handlers, coord conversions | Add `Camera.hex_at_screen` + `_check_fleet_ability` validator. |
| DUP-X-09 | `game/ui/screens/event_log_data_source.py:150-194` | `get_cell_replay_id`, `get_cell_replay_unavailable_reason` | Extract `_get_cell_detail` helper. |
| DUP-X-10 (scope-reduced) | `game/ui/screens/strategy_fleet_ops.py:127,153,216` | `execute_move`, `execute_intercept`, `execute_join` error logging | Extract `_format_result_error` helper. **Cross-file claims in click_dispatcher / superweapons not confirmed.** |
| DUP-X-11 | `game/simulation/systems/battle_end_conditions.py` | 9 condition subclasses (`TickLimit`, `TeamEliminated`, `TeamIncapacitated`, `Escape`, `ShipDestroyed`, `Never`, `MassRatio`, `Any`, `All`) | Add base `_serialize_fields` + `to_dict` / `from_dict` dispatch. |
| DUP-X-12 | `game/strategy/services/ability_iterator.py:121-298` | 7 source providers | Extract `_iter_ability_sources` generator. |

---

## Rejected

Each row is a **potential false positive in `ocode-audit-shrink`**.

| ID | Original audit recommendation | Contrary evidence (file:line) | Rationale |
|----|------------------------------|--------------------------------|-----------|
| DUP-X-04 | Parameterize 3 hit-effect render functions into a single `_draw_radial_effect`. | `game/ui/effects/hit_effects.py:162` (stroke `int(2 * (1 - t))`) vs `:192` (`int(3 * (1 - t))`); `:166` vs `:196` line-length factor 1.3 vs 1.4; `:222-226` `_draw_ship_destroyed` has unique flash logic absent in the other two. | The three functions are NOT parameterizable duplicates. They are specialized renderings: different radiating-line counts (6 vs 8), different stroke widths, different radius multipliers, and `_draw_ship_destroyed` includes conditional flash logic absent elsewhere. The audit conflated structural similarity with consolidation feasibility. |

---

## Uncertain

| ID | Question for human reviewer | Recommended next step |
|----|-----------------------------|-----------------------|
| DUP-X-03 | Of the five `*Ability.__init__` classes the audit named (`ShieldModifierAbility`, `DamageModifierAbility`, `QualityImprovementAbility`, `RadiationShieldAbility` — *not* `SystemShieldingAbility` as the audit labelled it — and `ThrustModifierAbility`), only 2 are true twins. The remaining 3 use the same `if isinstance(data, dict):` guard but extract different field sets (2–4 fields, different defaults). Should we (a) consolidate only the 2 true twins for ≈ 12 LOC, (b) introduce a `_parse_data_fields(data, field_specs)` helper that all 5 use for ≈ 25 LOC, or (c) skip and rely on a future `SimpleMultiplierAbility` / `StaticValueAbility` base-class refactor? | Discuss with the user whether the 5 abilities should converge on a declarative `field_specs` schema (option b) or stay diverged (option c). Avoid (a) — partial consolidation would create an inconsistent pattern across one file. |
