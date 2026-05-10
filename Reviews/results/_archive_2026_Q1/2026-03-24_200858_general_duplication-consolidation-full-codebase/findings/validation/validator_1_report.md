# Validation Report: Validator 1

## Summary
- **Findings Reviewed:** 29
- **Confirmed:** 20
- **Downgraded:** 5
- **Rejected:** 4
- **Rejection Rate:** 13.8%

## Verdicts

#### Finding: DUP-CEA-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `_has_attrs` is identically defined in 4 files: `game/core/protocols.py:694`, `game/ai/protocols.py:174`, `game/simulation/interfaces/entity_protocols.py:480`, and `game/simulation/interfaces/ability_protocols.py:315`. All are identical one-liners. The finding understated the count (said 3, it's actually 4), making the duplication worse than reported.

#### Finding: DUP-CEA-002
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Two behavior classes in `game/ai/behaviors.py` (lines 192 and 274) define `TICK_DURATION: float = PhysicsConfig.TICK_RATE` as class constants. This is a minor alias duplication since both resolve to the same value.

#### Finding: DUP-CEA-003
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `SimulationConstants.TICKS_PER_SECOND = 100` at `game/core/constants.py:65` and `PhysicsConfig.TICK_RATE = 0.01` at `game/core/config.py:97` represent the same concept (1/100 = 0.01) without either being derived from the other.

#### Finding: DUP-CEA-004
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** `game/core/resources.py` imports `json` at line 11 but does NOT use `json.load()` anywhere in the file. It uses `load_json_required` from `json_utils`. The `json` import appears unused/vestigial, which is a dead import issue, not a duplication issue.

#### Finding: DUP-CEA-005
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** The projectile.py angle normalization (lines 160-165) uses an if/elif pattern to normalize to [-180, 180], not `% 360`. This is standard guidance math, not a reusable utility. No other file in the codebase uses this exact pattern. The normalization is tightly coupled to Pygame's `angle_to` return values.

#### Finding: DUP-CEA-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `game/strategy/quickstart_builder.py` (not `game/ui/screens/builder/` as stated - wrong path) uses raw `json.load()` at line 258 and `json.dump()` at line 262, despite importing `load_json` from `game.core.json_utils` at line 18. The file path in the finding is wrong but the issue exists.

#### Finding: DUP-CEA-007
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** `_flee_direction` is defined once as a module-level function at line 71 and called from 3 different places (lines 115, 163, 227). This is proper code reuse within a single module, not duplication. The function is already factored out.

#### Finding: DUP-XL-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Firing arc check logic (angle difference calculation with `(angle - facing + 180) % 360 - 180` and `abs(diff) <= firing_arc/2`) appears in `game/ai/combat_utils.py:227-229`, `game/simulation/combat/weapon_firing_system.py:254-256`, and `game/simulation/components/abilities/weapons.py:232-241`. Three independent implementations of the same geometric check.

#### Finding: DUP-XL-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** K/M suffix formatting is independently implemented in at least 4 locations: `game/ui/panels/planet_report_panel.py:311-318`, `game/ui/screens/empire_build_queue_formatter.py:188-192`, `game/ui/screens/planet_list_filters.py:301-306`, and `game/ui/screens/strategy_detail_fmt.py:109-121`. All use the same >= 1M / >= 1K thresholds with slight formatting variations.

#### Finding: DUP-XL-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `_get_ship_factory()` with identical lazy-init pattern (global `_ship_factory = None`, deferred import of `get_default_registry_provider` and `GameRegistries`, identical body) is copy-pasted between `game/ui/screens/setup_data_io.py:24-40` and `game/ui/screens/setup_screen.py:36-50`.

#### Finding: DUP-XL-004
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The finding claims a "4-layer delegation chain" for entity lookup, but the code shows different methods serving different purposes (battle controller `get_ship_by_id`, UI service `get_projectiles`, panel `_get_projectile_id`). These are not duplicating the same logic - they operate at different layers with different inputs/outputs. This is normal layered architecture, not harmful delegation duplication.

#### Finding: DUP-XL-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** HP-to-color mapping using the same threshold pattern (`> 0.5 = HP_HEALTHY, > 0.2 = HP_DAMAGED, else HP_CRITICAL`) appears inline at `game/ui/panels/battle_panels.py:405` and `game/ui/panels/ship_stats_renderer.py:290`. A proper function `get_hp_bar_color` exists at `ship_stats_renderer.py:90` but battle_panels.py doesn't use it.

#### Finding: DUP-XL-006
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** `_format_radiation` in `race_environment_panel.py:407` and `_format_radiation_summary` in `race_summary_panel.py:330` are not truly duplicated - they produce different output formats. The environment panel formats as "+N Res"/"-N Sens" while the summary panel formats as "Radiation: +N (Resistant)". Different display contexts with different outputs.

#### Finding: DUP-XL-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `math.degrees(math.atan2(y, x))` pattern appears inline in multiple files: `game/ai/controller.py:445`, `game/ai/combat_utils.py:223`, `game/simulation/combat/weapon_firing_system.py:254`, and `game/simulation/components/abilities/weapons.py:232`. While each has different variable names, the core pattern is the same angle-to-target calculation.

#### Finding: DUP-XL-008
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** The three `_format_value` methods in `scrollable_json_panel.py:242`, `empire_treasury_panel.py:233`, and `modifier_impact_grid.py:247` have completely different signatures, parameters, and logic. They are not duplicates - they just share a common method name for formatting values in their respective contexts.

#### Finding: DUP-XL-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `replace('_', ' ').title()` appears in 11+ locations across the codebase for converting snake_case identifiers to display names. While each is a one-liner, the pattern is repeated enough to warrant a shared utility function.

#### Finding: DUP-XL-010
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The file `game/ui/screens/builder/component_cache_manager.py` does not exist. The finding references a non-existent file.

#### Finding: DUP-PAT-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Scrollable panel patterns (scroll_offset tracking, mouse wheel handling, clipping, draw loops) appear in 18+ files across the UI layer. While not all are identical, the core scroll management logic is reimplemented repeatedly rather than using a shared base or mixin.

#### Finding: DUP-PAT-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** 62 `to_dict`/`from_dict` method occurrences across 23 files, with no shared serialization base class or mixin. Each class independently implements the dict conversion pattern. The count of 33+ classes in the finding is conservative.

#### Finding: DUP-PAT-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The test lab classes (ResultsPanel, TestRunDetailsPanel, ShipPanel, ComponentPanel, etc.) each have `draw()` and `handle_event()` methods but they serve very different purposes with different rendering logic. They share a loose structural pattern but not significant duplicated code. This is more of a missing interface/protocol issue than code duplication.

#### Finding: DUP-PAT-004
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The three sidebar classes (EmpireBuildQueueSidebar, EventLogSidebar, FleetReportSidebar) share a structural pattern (container panel, column toggles, button management) but have significantly different implementations. EmpireBuildQueueSidebar has tri-state filters and search, FleetReportSidebar has summary stats and action buttons. The shared pattern is more about architecture conventions than copy-paste duplication.

#### Finding: DUP-PAT-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** 12+ screen/scene classes without a shared base class. BattleScreen, StrategyScreen, DesignWorkshopScreen, TestLabScreen, MenuScene, KeybindingsScene, etc. all independently implement screen lifecycle (handle_event, draw, update patterns) without inheriting from a common Screen protocol or base.

#### Finding: DUP-PAT-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** 12 UIWindow subclasses each independently implement initialization patterns (window sizing, panel creation, column management setup). While each window has unique content, the boilerplate setup code is repeated.

#### Finding: DUP-PAT-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** FleetSelectionWindow, PlanetSelectionWindow, SystemSelectionWindow, and SaveSelectionWindow all follow a similar pattern of presenting a filterable/scrollable list for user selection from UIWindow base.

#### Finding: DUP-PAT-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** WeaponsInputHandler, FormationInputHandler, StrategyInputHandler, TestLabInputHandler are independent classes with no shared interface or base class, each implementing event routing logic independently.

#### Finding: DUP-PAT-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** ResearchRenderer, BuildQueueRenderer, WeaponsRenderer, FormationRenderer, StrategyRenderer, TestLabRenderer all independently implement rendering without a shared interface. Each has a `draw()` method but no formal contract.

#### Finding: DUP-PAT-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** BuildQueueFilterManager and PlanetListFilterManager in the screens directory, plus FilterStateManager in the filters directory, show parallel filter management structures without sharing a common base.

#### Finding: DUP-PAT-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** RaceAptitudesPanel, RaceDescriptionPanel, RaceEnvironmentPanel, RaceIdentityPanel, and RaceSummaryPanel share structural patterns (panel creation, label management, update callbacks) without a shared base class.

#### Finding: DUP-PAT-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Value formatting methods (_format_compact_number, K/M formatting, radiation formatting) are scattered across multiple UI files. This overlaps with DUP-XL-002 but is broader in scope, covering general value formatting beyond just K/M suffixes.
