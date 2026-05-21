# Type Audit — Verification Report
## CRITICAL Findings Verification

| ID | Source | File:Line | Reported Issue | Verified? | Notes |
|----|--------|-----------|----------------|-----------|-------|
| TYP-01-051 | Shard 01 | `game/ui/screens/strategy_modal_window.py:273` | `check_clicked_inside_or_blocking(self, event)` missing return type | **CONFIRMED** | Returns `False` (L290) or `super().check_clicked_inside_or_blocking(event)` (L292) — always `bool`. Overrides pygame_gui `UIWindow` public method. Cross-layer (UI → pygame_gui). |
| CRITICAL-02-01 | Shard 02 | `game/strategy/engine/commands/order_metadata_view.py:76` | `_registry()` (static) missing return type | **CONFIRMED** | Returns `command_registry` (L94), a `CommandRegistry` singleton after lazy import + seeding. Used by public properties on `OrderMetadataView` (L100-106+). `_`-prefix makes it private by convention, but it is the sole cycle-break for the order_type/command_registry dependency. Suggested `-> CommandRegistry` is correct. |
| Shard 03 CRITICAL | Shard 03 | `game/strategy/engine/superweapon_order_processor.py:85` | `_get_nav_service(self)` missing return type | **CONFIRMED** | Returns `FleetNavigationService` (L90-91). Despite `_` prefix, it **is called from external modules**: `close_warp_point.py:102` and `open_warp_point.py:91` both call `processor._get_nav_service()`. Cross-module, cross-layer (strategy engine → superweapon handlers). Suggested `-> FleetNavigationService` is correct. |
| TYP-04-MR-001 | Shard 04 | `game/simulation/entities/stat_contributors/registry.py:298` | `iter_for(self, comp)` missing return type | **CONFIRMED** | Generator method yielding via `yield entry` (L318). Called externally via module-level `STAT_CONTRIBUTOR_REGISTRY.iter_for()` from `game/simulation/entities/ship_stats.py:307`. Cross-module within simulation layer. Suggested `-> Iterator[StatContributorEntry]` is correct. |
| TYP-04-MR-002 | Shard 04 | `game/strategy/data/star_system.py:85` | `primary_star` property missing return type | **CONFIRMED** | Returns `self.stars[0]` (`Star`) or `None` (L86). Public property on `StarSystem` — called from **15 locations** across strategy data (`galaxy_warp_generator.py`), strategy engine (`create_dyson_sphere.py`), facade DTOs (`system_dto.py`), and UI (`strategy_detail_fmt.py`, `strategy_render/systems.py`). Clearly cross-layer. Suggested `-> Star \| None` is correct. |

### Summary: 5/5 CRITICAL findings confirmed. Zero disputed. Zero inconclusive.

---

## MAJOR Sampling

| ID | Source | File:Line | Reported Issue | Verified? | Notes |
|----|--------|-----------|----------------|-----------|-------|
| TYP-01-011 | Shard 01 | `game/ui/screens/planet_list_filters.py:38` | `gather_planets() -> Any` — MAJOR, should be `-> list[Planet]` | **CONFIRMED** | Returns `planets` list (L87) built from planet objects (L84). Also returns cached list (L63). Always `list[Planet]`. Public function called by `PlanetListWindow`. |
| MAJOR-02-01 | Shard 02 | `game/strategy/engine/environmental_hazard_engine.py:65` | `_get_ship_mutator() -> Any` — MAJOR, should be `-> IShipInstanceMutator` | **CONFIRMED** | Returns `self._ship_mutator` (L71), set to `ShipInstanceWriteService()`. Correct narrowing. |
| Shard 03 MAJOR | Shard 03 | `game/strategy/engine/game_session.py:403` | `handle_command() -> Any` — MAJOR, should be `-> ValidationResult` | **CONFIRMED** | Docstring (L411) states "Returns: ValidationResult". Return path (L416): `self._command_registry.dispatch(...)` which returns `ValidationResult`. Public method on `GameSession`. |
| TYP-04-007 | Shard 04 | `game/ui/screens/battle_screen.py:211` | `ships` property `-> Any` — MAJOR, should be `-> list[Ship]` | **CONFIRMED** | Returns `self.engine.ships` (L212) — BattleEngine.ships is `list[Ship]`. Public property on BattleScreen. |
| TYP-01-029 | Shard 01 | `game/ui/screens/setup_data_io.py:34` | `get_base_path() -> Any` — MAJOR, should be `-> str` | **CONFIRMED** | Returns `Paths.ROOT_DIR` (L36) which is a `str`. Public module-level function. |

### Summary: 5/5 MAJOR spot-checks confirmed. Categorization correct.

---

## Cross-Shard Consistency Check

### Duplicate Findings
**None found.** The four shards cover disjoint file sets (184, 218, 208, 236 files respectively). No file appears in more than one shard.

### Severity Inconsistencies

**1. `_get_*_mutator()` pattern rated inconsistently**

Same pattern (private lazy-init helper resolving a mutator service) receives different severities:

| Finding | Shard | File | Severity |
|---------|-------|------|----------|
| TYP-01-002 | 01 | `harvesting_engine.py:196` `_get_planet_mutator` | **MINOR** |
| TYP-01-002 | 01 | `harvesting_engine.py:205` `_get_empire_mutator` | **MINOR** |
| TYP-01-003 | 01 | `order_handlers/base.py:143` `_get_planet_mutator` | **MINOR** |
| TYP-01-003 | 01 | `order_handlers/base.py:152` `_get_ship_mutator` | **MINOR** |
| MAJOR-02-01 | 02 | `environmental_hazard_engine.py:65` `_get_ship_mutator` | **MAJOR** |
| Shard 03 | 03 | `planet_modifier_effect_engine.py:34` `_get_planet_mutator` | **MAJOR** |
| Shard 03 | 03 | `production_spawner.py:103` `_get_planet_mutator` | **MAJOR** |
| Shard 03 | 03 | `superweapon_order_processor.py:77` `_get_empire_mutator` | **MAJOR** |
| TYP-04-024 | 04 | `atmosphere_engine.py:30` `_get_planet_mutator` | **MINOR** |

**Assessment:** These are identical patterns — private helpers that lazy-init and return a mutator service. Shard 02 and 03 rated them MAJOR, Shard 01 and 04 rated them MINOR. The consistent rating should be **MINOR** (private helpers, simple narrowing). The mutation surface is properly typed at the Protocol level; these are just accessor helpers.

**2. `_dismiss_button` type:ignore rated oppositely**

| Finding | Shard | File | Rating |
|---------|-------|------|--------|
| TYP-01-059 | 01 | `defeat_dialog.py:83` — `self._dismiss_button = None  # type: ignore[assignment]` | **MAJOR (unjustified)** |
| Shard 04 audit | 04 | `turn_failed_dialog.py:99` — `self._dismiss_button = None  # type: ignore[assignment]` | **VALID (justified)** |

**Assessment:** Both use identical code (`self._dismiss_button = None  # type: ignore[assignment]`) in a `_window_init_bypassed` test path. The same remediation (declare `Optional[UIButton]` in constructor) applies to both. Should be rated consistently — either both MAJOR or both VALID. The Shard 04 auditor considered the test bypass-init path justification sufficient; Shard 01 did not.

**3. `_button_handlers` missing return type rated inconsistently**

| Finding | Shard | File | Rating |
|---------|-------|------|--------|
| Shard 03 | 03 | `radiation_shield_editor.py:176` `_button_handlers` | **MAJOR** |
| Shard 02 | 02 | `gravity_target_editor.py:164`, `water_target_editor.py:173` | **False positive** (annotated) |
| TYP-04-MR-006 | 04 | `atmosphere_target_editor.py:223` `_button_handlers` | **MINOR** |

**Assessment:** Shard 03 rates `_button_handlers` as MAJOR but Shard 04 rates the same pattern as MINOR. Shard 02 considered them false positives (already annotated). The method is private (`_` prefix) and UI-internal — consistent MINOR rating is appropriate.

### Consistent Applications (correct)
- Protocol-level `-> Any`: consistently INFO/unavoidable across all shards
- `_precheck`/`_effect` inner closures: consistently MINOR across Shards 01 and 04
- Pygame event handler `process_event -> Any`: consistently INFO across shards
- `TYPE_CHECKING` hygiene: consistently clean across all shards
- No `cast()` usage found: consistent across all shards

---

## Summary
- **Total CRITICAL verified:** 5/5 (all confirmed)
- **Disputed:** 0
- **Inconclusive:** 0
- **MAJOR spot-checks verified:** 5/5 (all confirmed)
- **Cross-shard duplicates:** None (disjoint file sets)
- **Severity inconsistencies:** 3 patterns identified (mutator helpers, dismiss_button ignore, button_handlers)
- **Overall quality:** Reports are thorough and source-accurate. The identified inconsistencies are in severity judgment, not factual accuracy. All file references resolve correctly; all suggested narrowings are type-safe.
