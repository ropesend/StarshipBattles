# Phase 4 — UI Consumer Migration Map

> Audit pass for Task 4.1 of `phase_4_checklist.md`. Source-of-truth for the
> migration of `_legacy_provider_fields` (`system_effects_collector.py:415`)
> consumers to PROJ-300 universal DTO fields (`source_kind`, `source_label`,
> `source_id`, `owner_id`).

## Summary

Re-walking the 5 candidate sites listed in `findings/02_dependencies.md` shows
that **only 1 of the 5 actually consumes `_legacy_provider_fields`**:

| # | Site | Reads provider DTO from `_legacy_provider_fields`? |
|---|------|----------------------------------------------------|
| 1 | `game/ui/panels/system_tree_panel.py:9-20, 552, 582` | **YES** — reads `facility_name`, `planet_name` from provider dicts emitted by `collect_system_effects` / `collect_sector_effects`. |
| 2 | `game/ui/screens/planet_abilities_window.py:107-109, 113` | **NO** — reads `entry['facility_id']`, `entry['facility_name']`, `entry['component_key']` from `PlanetAbilitiesController.scan_abilities()`, which constructs its own dicts directly from `facility.instance_id` / `facility.name` (controller.py:161-163). Independent code path; values are real entity IDs used for command dispatch (`IssuePlanetOrderCommand`), not provider-DTO display labels. |
| 3 | `game/ui/screens/planet_abilities_controller.py:161-163` | **NO** — this is the *producer* of dicts described in (2). It writes `facility_id`, `facility_name`, `component_key` from facility attributes. Same code path as (2); not a consumer of the collector shim. |
| 4 | `game/ui/panels/planet_report_panel.py:474-483` | **NO** — `facility_name` is a local variable populated from `(f.name for f in self.planet.facilities ...)`. No provider-DTO read; counts complexes by `design_id`. |
| 5 | `game/ui/screens/strategy_detail_fmt.py:332, 335, 435-436` | **NO** — `result[ability_key] = {'status_text': ..., 'planet_name': planet.name}` is a local-dict key populated from `planet.name`. Not the same `planet_name` field as the collector shim emits. |

The original `findings/02_dependencies.md` table was a string-grep list, not a
data-flow analysis. The only file that reads provider dicts from the
`collect_system_effects` / `collect_sector_effects` return shape is
`system_tree_panel.py`.

Other consumers of the public collector API (`collect_system_effects`,
`collect_sector_effects`) — `conflict_resolution_engine.py:161-168`,
`environmental_hazard_engine.py:152-153`, `fleet_movement_engine.py:114-126`
— all read PROJ-300 universal fields (`source_kind`, `source_label`) and
aggregate values. None of them touch legacy keys.

## Migration map

### Site 1 — `game/ui/panels/system_tree_panel.py`

| Aspect | Detail |
|--------|--------|
| Helper | `_legacy_provider_label(provider)` (lines 9-20) |
| Legacy keys read | `provider.get('facility_name')`, `provider.get('planet_name')` |
| Used at | `:552`: `location_str = p.get('source_label') or _legacy_provider_label(p)` (single-provider effect leaf) |
|        | `:582`: `label = p.get('source_label') or _legacy_provider_label(p)` (per-provider sub-leaf in multi-provider effects) |
| Produced label | When source is a facility: `f"{facility_name} ({planet_name})"`. When non-facility (storm/planet/star/etc.): falls back to `facility_name or planet_name or "(unknown)"`. |
| Mapping to new DTO | `provider['source_label']` already carries the human-readable label for every source kind. The PROJ-300 facility adapter sets `source_label` to the facility name (or facility-name + planet combo when applicable). For non-facility sources (storms, planets, stars, warp points, system archetypes), `source_label` is the source's own label (e.g. "Crab Storm", "Tatooine", "Sol"). |
| New shape sufficient? | **Yes.** The current code already prefers `source_label` and only falls back to the legacy combo when `source_label` is empty. With the legacy shim removed, the fallback should be the literal string `"(unknown)"` — matching `_legacy_provider_label`'s final fallback when both keys are empty/None. |
| UI-side helper needed? | **No.** The fallback collapses to a single-line `or "(unknown)"`. The 11-line helper is dead-weight after migration. |
| Migration | Replace both `p.get('source_label') or _legacy_provider_label(p)` calls with `p.get('source_label') or "(unknown)"`. Delete the `_legacy_provider_label` helper and its module-level docstring. |

## Outcome

- 1 real consumer; 4 false positives in the original dependency map.
- No view-model helper needed. The new DTO already carries everything
  `system_tree_panel.py` needs.
- After migration, the `_legacy_provider_fields` function in
  `system_effects_collector.py:415` and the `**_legacy_provider_fields(source)`
  spread at `:195` can be deleted.
