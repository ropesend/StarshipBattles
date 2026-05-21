# Independent Verification Report — PROJ-465

**Source audit:** `Reviews/results/2026-05-20_060020_audit_shrink/`
**Run date:** 2026-05-20
**Verifier:** Claude (independent reader; the `Agent` parallel-Explore tool was unavailable, so re-verification was performed directly by reading the live code — a different reader than the audit).

**Batch summary:** 17 verified / 0 rejected / 2 uncertain, out of 19 audit verified-safe candidates
(1 Section-3 dead file + 18 Section-4 CRITICAL/MAJOR duplication clusters).

All duplication sites were re-confirmed present at (or within one or two lines of) the
audit's claimed file:line in the live tree. A few audit *prose* labels were inaccurate
(corrected below) but the sites and extraction targets are real.

> **R = 0 caveat (per protocol Phase F):** zero rejections is normally suspicious because
> the audit's own verifier has produced false positives. Here all surviving items are
> *duplication consolidations* (refactors), not deletions — and the line/file evidence
> matched live code precisely on spot-checks across all 17. The one actual *deletion*
> candidate (`setup_renderer.py`) did **not** survive: it landed UNCERTAIN. So the
> skeptical pass did filter the highest-risk item; it simply found the refactor findings
> well-grounded.

---

## Verified

| ID | File(s) | Symbol / sites | Recommendation |
|----|---------|----------------|----------------|
| DUP-X-1 | order_handlers/{launch_fighters:240, launch_satellites:223, lay_mines:325, recover_fighters:233, recover_satellites:213} | `_find_ship` (5 copies) | Move to `BaseCommandHandler` (base.py:108) |
| DUP-X-7 | handlers/{launch_fighters:69, launch_satellites:70, lay_mines:78, recover_fighters:63, recover_satellites:65} | inline ship-resolution loop | Replace with `self._find_ship` |
| DUP-X-3 | handlers/{launch_fighters, launch_satellites, lay_mines, recover_fighters, recover_satellites} | `execute`/`_execute_fleet`/`_execute_planet` pipeline | `_handle_vehicle_order` template on base |
| Cluster 12+21 | order_handlers/{recover_fighters:139, recover_satellites:119, launch_fighters:147, launch_satellites:130} | `_run_with_issuer` | Shared parameterized skeleton |
| Cluster 11 | order_handlers/{recover_fighters:107, recover_satellites:90} | `execute_for_issuer` | Shared base |
| DUP-X-9 | order_handlers/{recover_fighters:261, recover_satellites:240} | `_*_ship_to_carried_vehicle` | Shared converter |
| DUP-X-6 | fleet_movement_engine:185, handlers/movement:241, fleet_navigation_service:56, galaxy_pathfinding_service:152, fleet_consumable_aggregator:217/241, fleet_dto:223 | `capabilities.can_use_warp()` | `Fleet.can_use_warp()` wrapper |
| DUP-X-2 | planet_order_validator:105, planet_menu_items:41, strategy_detail_formatter:303 | `facility_has_ability` (3 variants) | Canonical in `component_abilities.py` |
| DUP-X-5 | deployed_group:253/352/410 | `_from_dict_payload` | Template on `_ShipBearingDeployedGroup` |
| Cluster 2 | planetary/stat_modifiers:50/125 | `__init__`+`get_primary_value`+`get_ui_rows` | Inherit `SimpleMultiplierAbility` (base.py:480) |
| Cluster 8 | battle_engine:499/540 | `launch_*_in_battle` | Merge into one method |
| Cluster 9 | services/llm/background:182, ui/services/image/background:139 | `cancel` | `BackgroundCall.cancel()` base |
| Cluster 10 | hit_effects:146/176 | `_draw_armor_hit`/`_draw_component_destroyed` | `_draw_radial_hit` |
| Cluster 19 | stat_contributors/launch:25/69 | `contribute_*_launch` | `_contribute_launch` |
| Cluster 3 | strategy_superweapons:142/239/281 | designation handlers | `_handle_designation` |
| Cluster 6 | strategy_windows/selection_prompts:29/55/74 | `prompt_planet`/`open_system`/`prompt_fleet` | `_open_selection_modal` |
| Cluster 7 | defeat_dialog:107, turn_failed_dialog:123 | `process_event` (identical) | `DismissableDialog` base |

### Prose-label corrections (sites still verified)

- **Cluster 2:** Audit named classes `GlobalStatModifierAbility`/`FleetStatModifierAbility`
  in `stat_modifiers.py`. Live names are `ShieldModifierAbility` (line 20, `__init__` at 50)
  and `DamageModifierAbility` (line 95, `__init__` at 125), in
  `game/simulation/components/abilities/planetary/stat_modifiers.py` (audit omitted the
  `planetary/` subdir). Duplicated bodies at lines 50/125 confirmed.
- **Cluster 6:** Audit gave `ui/screens/selection_prompts.py`; live path is
  `ui/screens/strategy_windows/selection_prompts.py`. Methods confirmed at 29/55/74.
- **Cluster 8:** Audit gave `battle_engine.py` (no path); confirmed at
  `game/simulation/systems/battle_engine.py:499/540`.
- **DUP-X-2:** Third site method is named `_planet_has_ability` (not `facility_has_ability`)
  at `strategy_detail_formatter.py:303`; same concept, same line.

---

## Rejected

_None._ No candidate had contrary evidence (test/doc/data reference or dynamic dispatch)
that disproved its duplication claim. See the R=0 caveat above — interpret with the
understanding that all survivors are refactors, not deletions, and the one deletion
candidate was downgraded to UNCERTAIN.

---

## Uncertain

| ID | Question for a human | Recommended next step |
|----|----------------------|-----------------------|
| DCV-004 (`game/ui/screens/setup_renderer.py`, 216 LOC dead file) | The file has zero test/doc/data refs and its only importer is `setup_screen.py` (whose `BattleSetupScreen` has zero production callers — `screen_router.py` imports the live `FleetBattleSetupScreen` from `battle_setup/screen.py` instead). BUT `setup_screen.py` is itself tagged PRODUCT_DECISION (5 test imports + doc refs) and still does `from game.ui.screens.setup_renderer import (...)` at line 28. Deleting `setup_renderer.py` alone would break import of `setup_screen.py`, which tests load. Is the `setup_screen.py` migration considered complete (so both can be deleted together)? | Resolve the `setup_screen.py` PRODUCT_DECISION first. If migration to `battle_setup/` is complete, delete `setup_screen.py` + `setup_data_io.py` + `setup_renderer.py` together and migrate/remove their tests. Until then, this deletion is not safe in isolation — excluded from PROJ-465. |
| DUP-X-4 (canonical `bay_inventory` accessor, claimed 16 sites) | Audit claimed 16 `getattr(ship, "bay_inventory", None)` sites; live grep finds the exact pattern in only 3 files (`ai/carrier_controller.py`, `strategy/validation/colonize_validator.py`, `ui/screens/fleet_menu_items.py`). The proposed fix (`ShipInstance.get_bay_inventory()` / `has_bay_inventory()`) is a new API contract + caller migration, not a mechanical extraction. Is the 16-site claim stale, and is the API change in scope for a shrink pass? | Treat as a small design change rather than a shrink. Re-scope against current call sites before acting; excluded from PROJ-465's mechanical-consolidation scope. |
