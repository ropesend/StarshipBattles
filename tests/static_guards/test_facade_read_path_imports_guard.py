"""PROJ-472 Phase 1A — AST static-guard against facade READ-path imports.

Companion to the write-path guard
(``tests/static_guards/test_facade_bypass_guard.py``) and the read-path
*session* guard
(``tests/static_guards/test_facade_read_path_session_guard.py``).

Pattern #5's read-path policy (option b, ``docs/02_PATTERNS.md``) governs which
``game.strategy.*`` symbols UI code may import directly. The intended write
path — ``game.strategy.facade.*`` and ``game.strategy.engine.commands`` — is
always allowed. Everything else must be on an **exact**
``(file, module, member)`` allowlist; there are deliberately NO subpackage
wildcards, because ``game.strategy.data.*`` mixes UI-safe value/enum types
(``ContainableKind``, ``ActivationPhase``) with live domain/session traversal
helpers (``BuildQueueSource``, ``collect_build_queues_at_hex``,
``FleetCapabilityCalculator``) that must NOT leak into the UI as a read surface.

Key behaviours (mirroring the write-path guard structurally):
- AST walk over every ``game/ui/**/*.py``.
- ``if TYPE_CHECKING:`` imports are IGNORED — type-only references (e.g.
  ``build_queue_controller.py``) are not runtime bypasses and must not be
  churned by this guard.
- ``import game.strategy...`` (module imports) and
  ``from game.strategy... import ...`` (member imports) are both parsed.
- A positive-control test pins the matcher classifications so a future refactor
  cannot silently widen the always-allowed prefixes.

The documented UI-safe config/value/enum surface (Pattern #5) is enforced as
symbol-level data in ``_UISAFE_SYMBOLS`` (a ``frozenset[(module, member)]``),
NOT as an allowlist category. A UISAFE symbol is allowed for ANY UI file
(membership is a property of the symbol, not the file). The transitional
file-scoped ``_IMPORT_ALLOWLIST`` below enumerates the remaining runtime
``game.strategy.*`` imports under ``game/ui`` so the guard is GREEN on commit;
its value is blocking *net-new* non-allowlisted imports. Transitional entries
are categorised:

  CLUSTER  — build-queue cluster live-domain imports; PROJ-472 1B removes these
             as the cluster migrates onto facade queries. (TEMPORARY)
  FLEETCAP — FleetCapabilityCalculator late-imports; deferred to PROJ-475
             (no facade query exists yet).
  TAIL     — the deferred service-helper / save-game / misc live-read tail
             allowlisted-with-reason so the guard is green and net-new bypasses
             are still caught.

PROJ-476: the tooling/editor/sandbox-screen residue formerly parked in TAIL
(battle_setup / galaxy_test / race_setup / builder + the design-editor
screens-root files) is now codified in the first-class, machine-checkable
``_TOOLING_EXEMPTIONS`` category (exact ``(file, module, member, tag, reason)``
5-tuples; tags: prebattle-editor / sandbox-harness / race-authoring /
design-editor). Those imports are detached pre-session editors, standalone
sandbox harnesses, pre-session authoring services, and design-editor
metadata/catalog loaders that read NO live ``GameSession`` — they intentionally
stay outside the facade DTO boundary rather than awaiting migration.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
UI_DIR = REPO_ROOT / "game" / "ui"

# The intended write path is always allowed. A module is allowed outright if it
# is exactly ``game.strategy.engine.commands`` or starts with
# ``game.strategy.facade``. Everything else must be on _IMPORT_ALLOWLIST.
_ALWAYS_ALLOWED_EXACT: frozenset[str] = frozenset({"game.strategy.engine.commands"})
_ALWAYS_ALLOWED_PREFIX: str = "game.strategy.facade"

# PROJ-474: The documented UI-safe read surface is now first-class symbol-level
# data, NOT a comment category. A ``(module, member)`` pair in
# ``_UISAFE_SYMBOLS`` is allowed for ANY UI file (membership is a property of the
# symbol — a pure enum / constant / frozen-static-metadata table / detached
# config-or-value type / static-data loader — not of the file). The matcher
# consults this set BEFORE the exact file-scoped transitional triple check.
#
# Symbol-level, NOT module prefixes: ``game.strategy.data.*`` and several service
# modules are MIXED. ``race_description_llm_controller`` carries a safe
# ``FieldStatus`` enum AND a live ``RaceDescriptionLLMController`` state machine;
# ``economy_config`` has a safe ``get_default_economy_config`` getter AND a
# mutating ``set_default_economy_config`` setter. A module prefix would wrongly
# bless the live members.
#
# Two invariants pin this surface:
#   - ``test_uisafe_symbols_match_pattern5_token_list`` (parity): this set must
#     equal the parseable fenced token block under Pattern #5 in
#     ``docs/02_PATTERNS.md`` — neither can drift.
#   - ``test_uisafe_symbols_not_also_in_transitional_allowlist`` (no-misfile):
#     no UISAFE symbol may also appear (module, member)-projected in the
#     transitional file-scoped ``_IMPORT_ALLOWLIST``.
#
# Membership criteria (see Projects/active_projects/PROJ-474/design.md): usable
# before/independent of a live ``GameSession``; does not require/return live
# strategy-graph or session-bound objects; is an enum/const/frozen-static
# table / detached config-or-value type / static-data loader; exposes no live
# owner refs. A pure helper that TAKES a live domain object is NOT UI-safe.
_UISAFE_SYMBOLS: frozenset[tuple[str, str]] = frozenset({
    # game_config scalars / config dataclasses (pre-session new-game setup)
    ('game.strategy.engine.game_config', 'DEFAULT_SYSTEM_COUNT'),
    ('game.strategy.engine.game_config', 'GameConfig'),
    ('game.strategy.engine.game_config', 'PlayerConfig'),
    ('game.strategy.engine.game_config', 'THEME_DEFAULTS'),
    ('game.strategy.engine.game_config', 'MAX_SYSTEM_COUNT'),
    ('game.strategy.engine.game_config', 'MIN_SYSTEM_COUNT'),
    ('game.strategy.engine.game_config', 'VALID_GALAXY_TYPES'),
    # Environmental preference value type + habitability factor iterators (static)
    ('game.strategy.data.environmental_preference', 'EnvironmentalPreference'),
    ('game.strategy.data.habitability_factors', 'iter_gas_factors'),
    ('game.strategy.data.habitability_factors', 'iter_scalar_factors'),
    # Homeworld preset loaders/applicators (repo data + detached RaceConfig)
    ('game.strategy.data.homeworld_presets', 'apply_preset_to_config'),
    ('game.strategy.data.homeworld_presets', 'get_preset_for_planet_type'),
    ('game.strategy.data.homeworld_presets', 'get_preset_id_from_name'),
    ('game.strategy.data.homeworld_presets', 'load_homeworld_presets'),
    # Detached race config dataclass + label tuples + cost authority
    ('game.strategy.data.race_config', 'RaceConfig'),
    ('game.strategy.data.race_config', 'GOVERNMENT_ORGANIZATIONS'),
    ('game.strategy.data.race_config', 'GOVERNMENT_TYPES'),
    ('game.strategy.data.race_config', 'LEADER_TITLES'),
    ('game.strategy.data.race_config', 'PHYSICAL_TYPES'),
    ('game.strategy.data.race_config', 'SOCIETY_TYPES'),
    ('game.strategy.data.race_point_budget', 'RacePointBudget'),
    # Containable kind enum
    ('game.strategy.data.containable', 'ContainableKind'),
    # Component activation: phase enum + detached scalar dataclass
    ('game.strategy.data.component_activation_state', 'ActivationPhase'),
    ('game.strategy.data.component_activation_state', 'ComponentActivationState'),
    # Pure enums / detached scalar dataclasses (promoted from TAIL, PROJ-474)
    ('game.strategy.data.order_types', 'OrderType'),
    ('game.strategy.data.planet', 'PlanetType'),
    ('game.strategy.data.fleet_hierarchy', 'BattleRole'),
    ('game.strategy.data.fleet_hierarchy', 'CombatPolicy'),
    # Cached static-config getter (NOT the mutating setter)
    ('game.strategy.config.economy_config', 'get_default_economy_config'),
    # Pure enum from a mixed module (the controller class stays TAIL)
    ('game.strategy.services.race_description_llm_controller', 'FieldStatus'),
    # Static ability metadata enum + frozenset query over prebuilt tables
    ('game.strategy.services.ability_metadata', 'StrategicKind'),
    ('game.strategy.services.ability_metadata', 'abilities_with_kind_tag'),
    # Immutable static superweapon spec table
    ('game.strategy.services.superweapon_registry', 'SUPERWEAPONS'),
})

# PROJ-476: First-class, machine-checkable TOOLING-EXEMPTION category.
#
# These are the tooling/editor/sandbox-screen ``game.strategy.*`` imports that
# are NOT live-session reads and NOT pure UI-safe symbols. They are detached
# pre-session editors / standalone sandbox harnesses / pre-session authoring
# services / design-editor metadata-catalog loaders that legitimately stay
# OUTSIDE the facade DTO boundary (no live ``GameSession`` is read). PROJ-476
# replaces PROJ-472's comment-only ``TAIL`` parking of these imports with this
# enforced category: each entry is an exact
# ``(file, module, member, category_tag, reason)`` 5-tuple. The category is
# exact-triple scoped — NOT a folder/subpackage waiver — because the tooling
# dirs MIX promotable pure symbols (``PlanetType``, ``RaceConfig``,
# ``VALID_GALAXY_TYPES``, ``FieldStatus`` …, now in ``_UISAFE_SYMBOLS``) with
# these genuine tooling imports.
#
# category_tag ∈ {prebattle-editor, sandbox-harness, race-authoring, design-editor}.
#
# Invariants pin this surface:
#   - ``test_tooling_exemptions_are_disjoint_from_uisafe_and_tail`` (no-misfile):
#     (module, member) projection disjoint from ``_UISAFE_SYMBOLS``; the
#     (file, module, member) set disjoint from the residual ``_IMPORT_ALLOWLIST``.
#   - ``test_tooling_exemption_allows_exact_triple_not_folder`` (positive control):
#     a real tooling triple is allowed; a non-exempt live ``GameSession`` import
#     in a tooling dir is still flagged.
#   - ``test_tooling_exemption_tags_match_pattern5`` (doc<->guard parity).
#
# Membership criteria (Projects/active_projects/PROJ-476/design.md): does NOT
# read/traverse a live ``GameSession``; is NOT a pure UI-safe symbol; and is one
# of a detached pre-session editor / standalone sandbox harness / pre-session
# authoring service / design-editor metadata-catalog loader.
_TOOLING_EXEMPTIONS: frozenset[tuple[str, str, str, str, str]] = frozenset({
    # --- prebattle-editor: battle_setup detached pre-battle fleet editor; holds
    #     real Fleet/ShipInstance/TaskForce/Squadron objects + mutates the
    #     hierarchy directly. No GameSession exists yet at edit time. ---
    ("game/ui/screens/battle_setup/fleet_hierarchy_editor.py", "game.strategy.data.ship_instance", "ShipInstance",
     "prebattle-editor", "detached pre-battle fleet editor builds real ShipInstance objects (runtime-local at :165)"),
    ("game/ui/screens/battle_setup/fleet_hierarchy_editor.py", "game.strategy.data.squadron", "Squadron",
     "prebattle-editor", "edits the detached fleet hierarchy's Squadron groupings before any session"),
    ("game/ui/screens/battle_setup/fleet_hierarchy_editor.py", "game.strategy.data.task_force", "TaskForce",
     "prebattle-editor", "edits the detached fleet hierarchy's TaskForce groupings before any session"),
    ("game/ui/screens/battle_setup_state.py", "game.strategy.data.fleet", "Fleet",
     "prebattle-editor", "battle-setup model holds real detached Fleet objects (the package's editor state, not a session read)"),
    ("game/ui/screens/battle_setup_state.py", "game.strategy.data.ship_instance", "ShipInstance",
     "prebattle-editor", "battle-setup model constructs real detached ShipInstance objects pre-session"),

    # --- sandbox-harness: galaxy_test standalone galaxy/system inspector;
    #     constructs its OWN Galaxy/StarSystem via generation, not a scene
    #     pass-through. Explicitly out of PROJ-477's render boundary. ---
    ("game/ui/screens/galaxy_test/galaxy_mode.py", "game.strategy.data.galaxy", "Galaxy",
     "sandbox-harness", "sandbox builds its OWN Galaxy for inspection, not a session pass-through"),
    ("game/ui/screens/galaxy_test/galaxy_mode.py", "game.strategy.generation.density.density_map", "DensityMap",
     "sandbox-harness", "sandbox generation: density map for self-built galaxy (runtime-local at :260)"),
    ("game/ui/screens/galaxy_test/galaxy_mode.py", "game.strategy.generation.loaders.galaxy_layouts_loader", "GalaxyLayoutsLoader",
     "sandbox-harness", "sandbox generation: galaxy layout loader (runtime-local at :259)"),
    ("game/ui/screens/galaxy_test/galaxy_mode.py", "game.strategy.generation.placement_strategies", "DensityBasedPlacementStrategy",
     "sandbox-harness", "sandbox generation: placement strategy for self-built galaxy (runtime-local at :255)"),
    ("game/ui/screens/galaxy_test/galaxy_mode.py", "game.strategy.generation.placement_strategies", "RandomPlacementStrategy",
     "sandbox-harness", "sandbox generation: placement strategy for self-built galaxy (runtime-local at :255)"),
    ("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.planet", "Planet",
     "sandbox-harness", "sandbox builds its OWN Planet objects for inspection (runtime-local at :373)"),
    ("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.planet_gen", "PlanetGenerator",
     "sandbox-harness", "sandbox generation: planet generator (runtime-local at :210)"),
    ("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.planet_physics", "MASS_EARTH",
     "sandbox-harness", "sandbox physics derivation constant for the info panel (runtime-local at :408)"),
    ("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.planet_physics", "calculate_escape_velocity",
     "sandbox-harness", "sandbox physics derivation for the info panel (runtime-local at :408)"),
    ("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.planet_physics", "calculate_surface_gravity",
     "sandbox-harness", "sandbox physics derivation for the info panel (runtime-local at :408)"),
    ("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.star_system", "StarSystem",
     "sandbox-harness", "sandbox builds its OWN StarSystem for inspection (runtime-local at :208)"),
    ("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.stars", "Star",
     "sandbox-harness", "sandbox builds its OWN Star objects (runtime-local at :372)"),
    ("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.data.stars", "StarGenerator",
     "sandbox-harness", "sandbox generation: star generator (runtime-local at :209)"),
    ("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.generation.loaders.system_blueprints_loader", "SystemBlueprintsLoader",
     "sandbox-harness", "sandbox generation: system blueprints loader (runtime-local at :196/:212)"),
    ("game/ui/screens/galaxy_test/system_mode.py", "game.strategy.generation.planet_image_registry", "PlanetImageRegistry",
     "sandbox-harness", "sandbox generation: planet image registry (runtime-local at :211)"),

    # --- race-authoring: race_setup pre-session authoring tool; orchestrates
    #     filesystem race files / randomizes detached RaceConfig / caption
    #     sidecars / UI-polled LLM controller. None traverse a live session. ---
    ("game/ui/screens/race_setup/controller.py", "game.strategy.systems.race_library", "RaceLibrary",
     "race-authoring", "filesystem race-file orchestration before any session exists"),
    ("game/ui/screens/race_setup/controller.py", "game.strategy.systems.race_randomizer", "RaceRandomizer",
     "race-authoring", "randomizes a detached RaceConfig at authoring time"),
    ("game/ui/screens/race_setup/panel_factory.py", "game.strategy.data.race_caption_loader", "RaceCaptionLoader",
     "race-authoring", "loads caption sidecar files at authoring time (runtime-local at :162)"),
    ("game/ui/screens/race_setup/panel_factory.py", "game.strategy.services.race_description_llm_controller", "RaceDescriptionLLMController",
     "race-authoring", "UI-polled LLM state machine for race description authoring (runtime-local at :163; FieldStatus enum is UISAFE)"),
    ("game/ui/screens/race_setup/screen.py", "game.strategy.systems.race_library", "RaceLibrary",
     "race-authoring", "filesystem race-file orchestration before any session exists"),
    ("game/ui/screens/race_setup/screen.py", "game.strategy.systems.race_randomizer", "RaceRandomizer",
     "race-authoring", "test-patch re-export seam (noqa F401 at :28); prune if the seam is removed"),

    # --- design-editor: ship-design editor metadata/catalog loaders;
    #     mutable lazy-loaded base/mod/user role overlay + browse-time catalog,
    #     both editor-time, neither a UI-safe immutable symbol nor a session read. ---
    ("game/ui/screens/builder/right_panel.py", "game.strategy.data.design_role_registry", "get_default_design_role_registry",
     "design-editor", "mutable lazy-loaded base/mod/user role overlay for the design editor (runtime-local at :387)"),
    ("game/ui/screens/design_selector_window.py", "game.strategy.data.design_role_registry", "get_default_design_role_registry",
     "design-editor", "mutable lazy-loaded base/mod/user role overlay for the design selector (runtime-local at :348/:390)"),
    # PROJ-476 Phase 4 (Codex exec-audit F1): the design_selector_window
    # ``DesignCatalog`` import was annotation-only under PEP 563 (no runtime use);
    # it was moved under TYPE_CHECKING in the production file, so it no longer
    # needs a tooling exemption. The live catalog is injected as self.design_catalog.
    ("game/ui/screens/workshop_event_router.py", "game.strategy.data.design_role_registry", "get_default_design_role_registry",
     "design-editor", "mutable lazy-loaded base/mod/user role overlay for the workshop editor (runtime-local at :568)"),
})

# Convenience projection: the exact (file, module, member) triples covered by
# _TOOLING_EXEMPTIONS (tag/reason stripped) for the matcher's membership check.
_TOOLING_EXEMPTION_TRIPLES: frozenset[tuple[str, str, str]] = frozenset(
    (rel, module, member) for (rel, module, member, _tag, _reason) in _TOOLING_EXEMPTIONS
)

# Exact (relative_posix_path, module, member) allowlist. ``member`` is the
# imported name; for bare ``import game.strategy.x`` it is the sentinel
# ``"__MODULE__"``. See module docstring for category meanings.
#
# NOTE (PROJ-474): the former ``UISAFE`` block of triples has been replaced by
# the symbol-level ``_UISAFE_SYMBOLS`` set above. The transitional categories
# below stay FILE-SCOPED because the same symbol can be UI-safe in one file and
# live in another (e.g. ``RaceLibrary``, ``DesignCatalog``).
_IMPORT_ALLOWLIST: frozenset[tuple[str, str, str]] = frozenset({
    # --- CLUSTER: build-queue live-domain imports; PROJ-472 1B migrates (TEMPORARY) ---
    # PROJ-472 1B (2026-05-21): build_queue_input_router, build_queue_screen, and
    # empire_build_queue_window migrated onto facade.empires.(hex_)build_queues +
    # the enriched BuildQueueSourceDTO; their CLUSTER entries are removed so the
    # guard now enforces the boundary for those files.
    # PROJ-475 Phase 2 Task 2.7 MIGRATED + REMOVED the CLUSTER
    # colony_has_planetary_yard import for strategy_detail_formatter.py — the
    # Build-Yard button gate now reads facade.planets.get(planet_id).has_build_yard
    # (the slice resolves the planetary-yard bit with registries at projection time).

    # --- FLEETCAP: PROJ-475 Phase 2 Task 2.6 MIGRATED + REMOVED both
    #     FleetCapabilityCalculator late-imports (fleet_data_source +
    #     fleet_report_filters). The fleet report now consults the
    #     facade-projected ``ShipInfo.has_spaceyard`` via an
    #     ``instance_id -> has_spaceyard`` bridge held on the view-model. ---

    # --- TAIL: deferred ~75-file tail (PROJ-474/475/476); allowlisted-with-reason ---
    ('game/ui/panels/build_queue_controller.py', 'game.strategy.services.design_validator', 'DesignValidator'),
    ('game/ui/panels/system_tree_panel.py', 'game.strategy.services.system_effects_collector', 'collect_sector_effects'),
    ('game/ui/panels/system_tree_panel.py', 'game.strategy.services.system_effects_collector', 'collect_system_effects'),
    ('game/ui/panels/system_tree_panel.py', 'game.strategy.services.system_effects_collector', 'format_intrinsic_ability_magnitude'),
    # PROJ-476: battle_setup prebattle-editor triples moved to _TOOLING_EXEMPTIONS.
    # PROJ-475 Phase 5 (audit Finding 1): the build-queue `compute_planet_production`
    # tail (plan.md:140 "Owned by PROJ-475") is consciously KEPT allowlisted-with-reason.
    # Both call sites (build_queue_panel_factory.py:247, build_queue_screen.py:321) render
    # a LIVE `Planet`/`yard` the build-queue screen already holds and call a pure read-only
    # production calculator with `facade.session_meta.registries()` — there is no `.session`
    # leak. A clean facade `production_rates` projection requires the live-`Planet`→DTO
    # bridge that is PROJ-477's render/read-model boundary work (PROJ-477 scopes
    # build_queue_screen / build_queue_controller / strategy_build_queue_manager). Pinned by
    # `test_build_queue_compute_planet_production_deferral_is_intentional`.
    ('game/ui/screens/build_queue_panel_factory.py', 'game.strategy.services.planet_economy_projector', 'compute_planet_production'),
    ('game/ui/screens/build_queue_screen.py', 'game.strategy.services.planet_economy_projector', 'compute_planet_production'),
    # PROJ-476: builder/right_panel design-editor triple moved to _TOOLING_EXEMPTIONS.
    ('game/ui/screens/cargo_quick_dialog_controller.py', 'game.strategy.services.cargo_transfer_service', 'CargoTransferService'),
    # PROJ-476: design_selector_window design-editor triples moved to _TOOLING_EXEMPTIONS.
    ('game/ui/screens/empire_panel_window.py', 'game.strategy.services.empire_economy_service', 'EmpireEconomyService'),
    ('game/ui/screens/fleet_data_source.py', 'game.strategy.services.component_abilities', 'has_warp_capability'),
    ('game/ui/screens/fleet_data_source.py', 'game.strategy.services.component_abilities', 'ship_has_ability'),
    ('game/ui/screens/fleet_data_source.py', 'game.strategy.services.fleet_speed_calculator', 'FleetSpeedCalculator'),
    ('game/ui/screens/fleet_menu_items.py', 'game.strategy.data.deployed_group', 'FighterWing'),
    ('game/ui/screens/fleet_menu_items.py', 'game.strategy.data.deployed_group', 'SatelliteConstellation'),
    ('game/ui/screens/fleet_report_filters.py', 'game.strategy.services.component_abilities', 'has_warp_capability'),
    ('game/ui/screens/fleet_report_filters.py', 'game.strategy.services.component_abilities', 'ship_has_ability'),
    ('game/ui/screens/fleet_report_filters.py', 'game.strategy.services.fleet_speed_calculator', 'FleetSpeedCalculator'),
    # PROJ-476: galaxy_test sandbox-harness triples moved to _TOOLING_EXEMPTIONS.
    ('game/ui/screens/planet_abilities_controller.py', 'game.strategy.services.component_abilities', 'extract_abilities_from_component'),
    ('game/ui/screens/planet_list_event_router.py', 'game.strategy.services.planet_economy_projector', 'compute_planet_production'),
    ('game/ui/screens/planet_list_filters.py', 'game.strategy.services.system_effects_collector', 'make_group_key'),
    ('game/ui/screens/planet_list_helpers.py', 'game.strategy.services.system_effects_collector', 'format_intrinsic_ability_magnitude'),
    ('game/ui/screens/planet_list_helpers.py', 'game.strategy.services.system_effects_collector', 'make_display_name'),
    ('game/ui/screens/planet_list_helpers.py', 'game.strategy.services.system_effects_collector', 'make_group_key'),
    ('game/ui/screens/planet_list_sidebar.py', 'game.strategy.services.system_effects_collector', 'make_display_name'),
    ('game/ui/screens/planet_menu_items.py', 'game.strategy.data.deployed_group', 'FighterWing'),
    ('game/ui/screens/planet_menu_items.py', 'game.strategy.data.deployed_group', 'SatelliteConstellation'),
    ('game/ui/screens/planet_menu_items.py', 'game.strategy.services.ability_sources.facility', 'FacilityAbilitySource'),
    # PROJ-476: race_setup race-authoring triples moved to _TOOLING_EXEMPTIONS.
    ('game/ui/screens/save_selection_window.py', 'game.strategy.systems.save_game_service', 'SaveGameService'),
    ('game/ui/screens/species_selector_mixin.py', 'game.strategy.systems.race_library', 'RaceLibrary'),
    ('game/ui/screens/new_game_setup_screen.py', 'game.strategy.systems.race_library', 'RaceLibrary'),
    ('game/ui/screens/strategy_build_queue_manager.py', 'game.strategy.systems.design_catalog', 'DesignCatalog'),
    ('game/ui/screens/strategy_click_dispatcher.py', 'game.strategy.data.physics', 'SectorEnvironment'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.data.bay_inventory', 'DropPod'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.data.carried_vehicle', 'CarriedVehicle'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.formulas.habitability', 'calculate_habitability'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.services.component_abilities', 'extract_abilities_from_component'),
    ('game/ui/screens/strategy_detail_formatter.py', 'game.strategy.services.component_abilities', 'extract_abilities_from_component'),
    ('game/ui/screens/strategy_detail_formatter.py', 'game.strategy.services.planet_economy_projector', 'compute_planet_production'),
    ('game/ui/screens/strategy_event_router.py', 'game.strategy.systems.race_library', 'RaceLibrary'),
    ('game/ui/screens/strategy_fleet_command_router.py', 'game.strategy.services.component_abilities', 'extract_abilities_from_component'),
    # PROJ-475 Phase 2 Task 2.4 REMOVED the SaveGameService import entry for
    # strategy_game_state_manager.py — auto-save now routes through
    # facade.session_meta.save_current_game(); the UI no longer imports the service.
    ('game/ui/screens/strategy_render/cursor.py', 'game.strategy.services.cargo_transfer_service', 'project_fleet_position'),
    # Composition root: StrategyScreen rebuilds the facade from a concrete
    # GameSession in its test-swap setter (the `session` SETTER). Transitional;
    # the `session` GETTER + this import are deferred to PROJ-477 (the getter
    # still has live consumers — system_tree_panel dynamic-getattr + Category B
    # mutator write seams — per PROJ-475 post-flesh review B2).
    ('game/ui/screens/strategy_screen.py', 'game.strategy.engine.game_session', 'GameSession'),
    # PROJ-475 Phase 2 Task 2.4 REMOVED the SaveGameService import entry for
    # strategy_screen_lifecycle.py — manual save (on_save_game_click) now routes
    # through facade.session_meta.save_current_game(); the late import is dropped.
    ('game/ui/screens/strategy_superweapons.py', 'game.strategy.services.galaxy_pathfinding_service', 'GalaxyPathfindingService'),
    ('game/ui/screens/strategy_windows/event_log_window_ctrl.py', 'game.strategy.services.replay_resolver', 'ReplayResolver'),
    ('game/ui/screens/strategy_windows/event_log_window_ctrl.py', 'game.strategy.systems.save_game_service', 'SaveGameService'),
    ('game/ui/screens/transfer_controller.py', 'game.strategy.services.cargo_transfer_service', 'project_fleet_position'),
    # PROJ-476: workshop_event_router design-editor triple moved to _TOOLING_EXEMPTIONS.
})

# Sentinel member name for bare ``import game.strategy.x`` (no ``from ... import``).
_MODULE_MEMBER_SENTINEL = "__MODULE__"


def _ui_python_files() -> list[Path]:
    """Every .py under game/ui/ except __pycache__."""
    files: list[Path] = []
    for path in UI_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        files.append(path)
    return sorted(files)


def _type_checking_linenos(tree: ast.AST) -> set[int]:
    """Line numbers of statements inside any ``if TYPE_CHECKING:`` block.

    Imports under ``TYPE_CHECKING`` are type-only and never execute at runtime,
    so they are NOT bypasses (e.g. build_queue_controller's strategy imports).
    """
    out: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        name = test.id if isinstance(test, ast.Name) else (
            test.attr if isinstance(test, ast.Attribute) else None
        )
        if name != "TYPE_CHECKING":
            continue
        for child in node.body:
            for sub in ast.walk(child):
                lineno = getattr(sub, "lineno", None)
                if lineno is not None:
                    out.add(lineno)
    return out


def _is_always_allowed_module(module: str) -> bool:
    """True for the intended write path: facade.* / engine.commands."""
    if module in _ALWAYS_ALLOWED_EXACT:
        return True
    return module == _ALWAYS_ALLOWED_PREFIX or module.startswith(
        _ALWAYS_ALLOWED_PREFIX + "."
    )


def _violations_in_file(rel: str, tree: ast.AST, tc_lines: set[int]) -> list[str]:
    """Return human-readable violation strings for non-allowlisted runtime
    ``game.strategy.*`` imports in one file."""
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if node.lineno in tc_lines:
                continue
            for alias in node.names:
                mod = alias.name
                if not mod.startswith("game.strategy"):
                    continue
                if _is_always_allowed_module(mod):
                    continue
                # PROJ-474: bare ``import game.strategy.x`` binds the module, not
                # a member; the symbol-level UISAFE surface does not apply here.
                if (rel, mod, _MODULE_MEMBER_SENTINEL) in _IMPORT_ALLOWLIST:
                    continue
                # PROJ-476: exact-triple tooling exemption (e.g. a bare module
                # import in a tooling/editor/sandbox screen).
                if (rel, mod, _MODULE_MEMBER_SENTINEL) in _TOOLING_EXEMPTION_TRIPLES:
                    continue
                violations.append(f"{rel}:{node.lineno} import {mod}")
        elif isinstance(node, ast.ImportFrom):
            if node.lineno in tc_lines:
                continue
            mod = node.module
            # PROJ-472 1D (Codex finding 1): ``from game import strategy``
            # (module == 'game', member == 'strategy') re-exposes the whole
            # strategy package as a bare runtime name. Treat the imported
            # ``strategy`` member as a non-allowlisted bypass; other
            # ``from game import <x>`` members are out of scope.
            if mod == "game":
                for alias in node.names:
                    if alias.name == "strategy":
                        violations.append(
                            f"{rel}:{node.lineno} from game import strategy"
                        )
                continue
            if not (mod and mod.startswith("game.strategy")):
                continue
            if _is_always_allowed_module(mod):
                continue
            for alias in node.names:
                # PROJ-474: the documented UI-safe surface is symbol-level and
                # file-independent — check it before the exact transitional
                # file-scoped triple.
                if (mod, alias.name) in _UISAFE_SYMBOLS:
                    continue
                if (rel, mod, alias.name) in _IMPORT_ALLOWLIST:
                    continue
                # PROJ-476: exact (file, module, member) tooling exemption —
                # detached pre-session editor / sandbox harness / authoring
                # service / design-editor metadata; exact-triple, not folder-wide.
                if (rel, mod, alias.name) in _TOOLING_EXEMPTION_TRIPLES:
                    continue
                violations.append(
                    f"{rel}:{node.lineno} from {mod} import {alias.name}"
                )
    return violations


@pytest.mark.parametrize(
    "path",
    _ui_python_files(),
    ids=lambda p: str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
)
def test_no_unallowlisted_strategy_imports_in_ui(path: Path) -> None:
    """No non-allowlisted runtime ``game.strategy.*`` import anywhere in
    ``game/ui/``.

    The write path (``game.strategy.facade.*``, ``game.strategy.engine.commands``)
    is always allowed. Every other current runtime import is either a
    symbol-level UI-safe ``(module, member)`` in ``_UISAFE_SYMBOLS`` (PROJ-474)
    or a transitional file-scoped triple on ``_IMPORT_ALLOWLIST``
    (CLUSTER/FLEETCAP/TAIL entries removed as PROJ-472 1B / PROJ-475/476 migrate
    them). A net-new import fails here until classified UI-safe, allowlisted, or
    routed through the facade. ``if TYPE_CHECKING:`` imports are ignored.
    """
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    tc_lines = _type_checking_linenos(tree)
    violations = _violations_in_file(rel, tree, tc_lines)
    if violations:
        joined = "\n  ".join(violations)
        pytest.fail(
            "PROJ-472 Pattern #5 read-path violation(s): non-allowlisted "
            "runtime `game.strategy.*` import(s):\n  "
            f"{joined}\n"
            "UI code reads session-owned state through the facade. To resolve:\n"
            "  - If the symbol is a documented UI-safe value/config/enum/static "
            "table (Pattern #5), add it to `_UISAFE_SYMBOLS` AND the canonical "
            "token block in docs/02_PATTERNS.md (the parity test enforces both). "
            "Do NOT add a file-scoped triple for a UI-safe symbol — the "
            "no-misfile invariant forbids it.\n"
            "  - If it is an intentional transitional (live/tooling) read, add "
            "the (file, module, member) triple to `_IMPORT_ALLOWLIST` with a "
            "category/reason comment.\n"
            "  - Otherwise, route the read through the facade."
        )


def test_ui_directory_has_python_files() -> None:
    """Sanity: parametrize would silently produce zero tests if not."""
    files = _ui_python_files()
    assert files, f"No .py files found in {UI_DIR}"
    names = {f.name for f in files}
    assert "build_queue_screen.py" in names
    assert "strategy_screen.py" in names


def test_import_classifier_positive_controls() -> None:
    """Positive-control: pin the always-allowed / not-allowed classifications.

    Without this, a future refactor could widen ``_is_always_allowed_module``
    (e.g. to ``game.strategy.data``) and the directory scan would still pass,
    silently re-opening the read path. We also assert the canonical live-domain
    helpers are NOT in the always-allowed set (they must earn an explicit,
    reasoned allowlist entry, never a blanket pass).
    """
    # Write path — always allowed.
    assert _is_always_allowed_module("game.strategy.facade.strategy_session_facade")
    assert _is_always_allowed_module("game.strategy.facade.dto.fleet_dto")
    assert _is_always_allowed_module("game.strategy.engine.commands")
    # Live domain/session/query helpers — must NOT be blanket-allowed.
    assert not _is_always_allowed_module("game.strategy.data.build_queue_source")
    assert not _is_always_allowed_module("game.strategy.data.fleet_capability_calculator")
    assert not _is_always_allowed_module("game.strategy.engine.game_session")
    assert not _is_always_allowed_module("game.strategy.data")
    # A near-miss prefix must not be swallowed by startswith.
    assert not _is_always_allowed_module("game.strategy.facadexyz")


def test_matcher_flags_live_domain_imports_when_not_allowlisted() -> None:
    """Positive-control: the scan flags ``BuildQueueSource`` /
    ``collect_build_queues_at_hex`` / ``FleetCapabilityCalculator`` /
    ``GameSession`` runtime imports for a file with no allowlist entry, and does
    NOT flag a ``TYPE_CHECKING`` import or the facade write path.

    Uses a synthetic relative path that is not in ``_IMPORT_ALLOWLIST`` so the
    allowlist cannot mask the result.
    """
    src = (
        "from __future__ import annotations\n"
        "from typing import TYPE_CHECKING\n"
        "from game.strategy.data.build_queue_source import BuildQueueSource, collect_build_queues_at_hex\n"
        "from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator\n"
        "from game.strategy.engine.game_session import GameSession\n"
        "from game.strategy.facade.strategy_session_facade import StrategySessionFacade\n"
        "from game.strategy.engine.commands import IssueMoveCommand\n"
        "if TYPE_CHECKING:\n"
        "    from game.strategy.data.build_queue_source import BuildQueueSource as _BQS\n"
    )
    tree = ast.parse(src, filename="synthetic.py")
    tc_lines = _type_checking_linenos(tree)
    violations = _violations_in_file("synthetic_not_allowlisted.py", tree, tc_lines)
    blob = "\n".join(violations)

    assert "build_queue_source import BuildQueueSource" in blob
    assert "collect_build_queues_at_hex" in blob
    assert "FleetCapabilityCalculator" in blob
    assert "game_session import GameSession" in blob
    # Write path NOT flagged.
    assert "StrategySessionFacade" not in blob
    assert "IssueMoveCommand" not in blob
    # The single TYPE_CHECKING import must not double-count: BuildQueueSource
    # appears once (the runtime import on line 3), not from the line-9 TC import.
    assert blob.count("build_queue_source import BuildQueueSource") == 1


def test_matcher_flags_from_game_import_strategy_form() -> None:
    """PROJ-472 1D (Codex finding 1): the runtime-import guard must also flag
    the ``from game import strategy`` spelling, which re-exposes the whole
    ``game.strategy`` package under a bare local name and lets UI code reach
    ``strategy.data.build_queue_source.BuildQueueSource`` at runtime.

    Before 1D the matcher only inspected ``ast.ImportFrom.module`` values
    starting with ``game.strategy`` and ``ast.Import`` alias names starting
    with ``game.strategy``, so ``from game import strategy`` (module=='game',
    member=='strategy') slipped through unflagged.
    """
    src = (
        "from game import strategy\n"
        "v = strategy.data.build_queue_source.BuildQueueSource\n"
    )
    tree = ast.parse(src, filename="synthetic.py")
    tc_lines = _type_checking_linenos(tree)
    violations = _violations_in_file("synthetic_not_allowlisted.py", tree, tc_lines)
    blob = "\n".join(violations)
    assert "from game import strategy" in blob, (
        "Guard must flag `from game import strategy` (re-exposes the whole "
        "strategy package as a runtime read surface)."
    )


def test_matcher_does_not_flag_unrelated_from_game_imports() -> None:
    """Negative control for the 1D ``from game import strategy`` rule: other
    ``from game import <x>`` members (e.g. ``core``, ``ui``) must NOT be
    flagged — only the ``strategy`` package re-export is a read-path bypass.
    """
    src = (
        "from game import core\n"
        "from game import ui as _ui\n"
        "from game import strategy, core as _c\n"
    )
    tree = ast.parse(src, filename="synthetic.py")
    tc_lines = _type_checking_linenos(tree)
    violations = _violations_in_file("synthetic_not_allowlisted.py", tree, tc_lines)
    blob = "\n".join(violations)
    assert "import core" not in blob
    assert "import ui" not in blob
    # The mixed import line still flags `strategy` but not `core`.
    assert "from game import strategy" in blob


# --- PROJ-474: symbol-level UISAFE surface invariants ----------------------

_PATTERN5_DOC = REPO_ROOT / "docs" / "02_PATTERNS.md"
_UISAFE_TOKEN_FENCE_MARKER = "PROJ-474 UISAFE canonical token list"


def _parse_pattern5_uisafe_tokens() -> frozenset[tuple[str, str]]:
    """Parse the canonical ``module.member`` token block under Pattern #5.

    The block is a fenced (```` ``` ````) section in ``docs/02_PATTERNS.md``
    immediately preceded by a marker line containing
    ``_UISAFE_TOKEN_FENCE_MARKER``. Each non-blank, non-comment line inside the
    fence is one ``dotted.module.path.member`` token; the last dotted segment is
    the member, the rest is the module. This is parsed (not prose-scraped) so
    the doc and the guard cannot drift.
    """
    text = _PATTERN5_DOC.read_text(encoding="utf-8")
    lines = text.splitlines()
    tokens: set[tuple[str, str]] = set()
    marker_seen = False  # marker line encountered, awaiting opening fence
    in_block = False
    found_block = False
    closed = False
    for line in lines:
        stripped = line.strip()
        if not in_block and _UISAFE_TOKEN_FENCE_MARKER in line and not stripped.startswith("```"):
            marker_seen = True
            continue
        if stripped.startswith("```"):
            if not in_block and marker_seen:
                in_block = True
                found_block = True
                marker_seen = False
                continue
            if in_block:
                in_block = False
                closed = True
                break  # closing fence
            continue
        if not in_block:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        module, _, member = stripped.rpartition(".")
        assert module and member, f"Malformed UISAFE token: {stripped!r}"
        tokens.add((module, member))
    assert found_block, (
        "Pattern #5 UISAFE canonical token block not found in "
        f"{_PATTERN5_DOC} (expected a fenced block immediately preceded by a "
        f"marker line containing {_UISAFE_TOKEN_FENCE_MARKER!r})."
    )
    assert closed, (
        "Pattern #5 UISAFE canonical token block was opened but never closed "
        f"with a fence in {_PATTERN5_DOC} (unterminated ``` block)."
    )
    return frozenset(tokens)


def _misfiled_symbols(
    uisafe: frozenset[tuple[str, str]],
    transitional: frozenset[tuple[str, str, str]],
) -> list[tuple[str, str]]:
    """Return ``(module, member)`` pairs that are in BOTH the symbol-level
    UI-safe set AND the ``(module, member)`` projection of the file-scoped
    transitional allowlist. The no-misfile invariant requires this to be empty.
    """
    transitional_pairs = {(module, member) for (_rel, module, member) in transitional}
    return sorted(uisafe & transitional_pairs)


def test_uisafe_symbols_not_also_in_transitional_allowlist() -> None:
    """No-misfile invariant: a symbol cannot be simultaneously UI-safe AND
    transitional. No ``(module, member)`` in ``_UISAFE_SYMBOLS`` may appear as
    the ``(module, member)`` projection of ANY triple in the file-scoped
    ``_IMPORT_ALLOWLIST`` (CLUSTER/FLEETCAP/TAIL).
    """
    misfiled = _misfiled_symbols(_UISAFE_SYMBOLS, _IMPORT_ALLOWLIST)
    assert not misfiled, (
        "PROJ-474 no-misfile invariant: these symbols are in BOTH "
        "_UISAFE_SYMBOLS and the transitional _IMPORT_ALLOWLIST. A symbol is "
        "either UI-safe (symbol-level, file-independent) or transitional "
        f"(file-scoped), not both — remove the transitional triple(s):\n  {misfiled}"
    )


def test_no_misfile_invariant_is_non_vacuous() -> None:
    """Durable proof that the no-misfile invariant actually fires on a
    duplicate (PROJ-474 exec-audit Finding 2). The Task 1.4 RED step verified
    this manually against the live globals; this pins the detection logic so a
    future refactor of ``_misfiled_symbols`` cannot silently make the invariant
    vacuous.
    """
    uisafe = frozenset({("game.strategy.data.race_config", "RaceConfig")})
    # A transitional triple whose (module, member) projection collides with the
    # UI-safe symbol above — exactly the pre-PROJ-474 misfile shape.
    transitional = frozenset({
        ("game/ui/screens/race_setup/controller.py",
         "game.strategy.data.race_config", "RaceConfig"),
        # A non-colliding triple must NOT be reported.
        ("game/ui/screens/race_setup/controller.py",
         "game.strategy.systems.race_library", "RaceLibrary"),
    })
    misfiled = _misfiled_symbols(uisafe, transitional)
    assert misfiled == [("game.strategy.data.race_config", "RaceConfig")]

    # And the clean case is genuinely empty (not always-truthy).
    assert _misfiled_symbols(
        frozenset({("game.strategy.data.race_config", "RaceConfig")}),
        frozenset({("game/ui/x.py", "game.strategy.systems.race_library", "RaceLibrary")}),
    ) == []


def test_uisafe_symbols_match_pattern5_token_list() -> None:
    """Doc<->guard parity: ``_UISAFE_SYMBOLS`` must equal the canonical token
    block embedded under Pattern #5 in ``docs/02_PATTERNS.md``. Neither the doc
    nor the guard may drift from the other.
    """
    doc_tokens = _parse_pattern5_uisafe_tokens()
    only_in_guard = sorted(_UISAFE_SYMBOLS - doc_tokens)
    only_in_doc = sorted(doc_tokens - _UISAFE_SYMBOLS)
    assert _UISAFE_SYMBOLS == doc_tokens, (
        "PROJ-474 doc<->guard parity drift between _UISAFE_SYMBOLS and the "
        f"Pattern #5 canonical token block ({_PATTERN5_DOC}).\n"
        f"In guard but not doc: {only_in_guard}\n"
        f"In doc but not guard: {only_in_doc}"
    )


def test_uisafe_symbol_matcher_is_symbol_level_not_module_level() -> None:
    """Positive control: a UISAFE ``(module, member)`` is allowed even from a
    SYNTHETIC (not-allowlisted) file, while a DIFFERENT live member of the SAME
    module is still flagged. This pins the structure as symbol-level: it would
    FAIL if ``_UISAFE_SYMBOLS`` were widened to a module prefix.

    Uses ``race_description_llm_controller``: ``FieldStatus`` (enum, UI-safe)
    allowed; ``RaceDescriptionLLMController`` (live state machine) flagged.
    """
    # Precondition: the safe member is UISAFE, the live one is not.
    assert (
        "game.strategy.services.race_description_llm_controller",
        "FieldStatus",
    ) in _UISAFE_SYMBOLS
    assert (
        "game.strategy.services.race_description_llm_controller",
        "RaceDescriptionLLMController",
    ) not in _UISAFE_SYMBOLS

    src = (
        "from __future__ import annotations\n"
        "from game.strategy.services.race_description_llm_controller import FieldStatus\n"
        "from game.strategy.services.race_description_llm_controller import RaceDescriptionLLMController\n"
    )
    tree = ast.parse(src, filename="synthetic.py")
    tc_lines = _type_checking_linenos(tree)
    violations = _violations_in_file("synthetic_not_allowlisted.py", tree, tc_lines)
    blob = "\n".join(violations)

    # Symbol-level allow: the UISAFE enum is NOT flagged even though the file is
    # not on the allowlist.
    assert "import FieldStatus" not in blob
    # Same module, different (live) member: STILL flagged.
    assert "import RaceDescriptionLLMController" in blob


def test_build_queue_compute_planet_production_deferral_is_intentional() -> None:
    """PROJ-475 Phase 5 (audit Finding 1): the build-queue
    ``compute_planet_production`` import tail is a CONSCIOUS allowlist-with-reason,
    deferred to PROJ-477, not an accidental leftover.

    The plan (``plan.md:140``) assigned this tail to PROJ-475 with the explicit
    option "allowlist-with-reason if no clean query exists". Both call sites render
    a LIVE ``Planet``/``yard`` the build-queue screen already holds and call a pure
    read-only production calculator with ``facade.session_meta.registries()`` — no
    ``.session`` leak. A clean facade ``production_rates`` projection needs the
    live-``Planet``→DTO bridge that is PROJ-477's render/read-model boundary work.

    This pin fails if a future change silently drops or re-scopes these entries
    without updating the rationale above them in ``_IMPORT_ALLOWLIST``.
    """
    expected = {
        (
            "game/ui/screens/build_queue_panel_factory.py",
            "game.strategy.services.planet_economy_projector",
            "compute_planet_production",
        ),
        (
            "game/ui/screens/build_queue_screen.py",
            "game.strategy.services.planet_economy_projector",
            "compute_planet_production",
        ),
    }
    missing = expected - _IMPORT_ALLOWLIST
    assert not missing, (
        "PROJ-475 Phase 5: the build-queue compute_planet_production deferral "
        f"entries must stay allowlisted-with-reason (deferred to PROJ-477). Missing: {missing}"
    )


# --- PROJ-476: tooling-exemption category invariants -----------------------

_TOOLING_EXEMPTION_TAGS: frozenset[str] = frozenset({
    "prebattle-editor",
    "sandbox-harness",
    "race-authoring",
    "design-editor",
})


def test_tooling_exemptions_are_disjoint_from_uisafe_and_tail() -> None:
    """PROJ-476 no-misfile invariant: each tooling-screen import is classified
    EXACTLY once.

    (a) The ``(module, member)`` projection of ``_TOOLING_EXEMPTIONS`` must be
        disjoint from ``_UISAFE_SYMBOLS`` — a symbol is either a pure UI-safe
        symbol (PROJ-474) or a file-scoped tooling exemption, never both.
    (b) The ``(file, module, member)`` set of ``_TOOLING_EXEMPTIONS`` must be
        disjoint from the residual transitional ``_IMPORT_ALLOWLIST``
        (TAIL/CLUSTER/FLEETCAP) — a tooling triple lives in exactly one place.
    """
    tooling_pairs = {(module, member) for (_rel, module, member, _tag, _reason) in _TOOLING_EXEMPTIONS}
    misfiled_uisafe = sorted(_UISAFE_SYMBOLS & tooling_pairs)
    assert not misfiled_uisafe, (
        "PROJ-476 no-misfile invariant: these (module, member) pairs are in BOTH "
        "_UISAFE_SYMBOLS and _TOOLING_EXEMPTIONS. A symbol is either UI-safe "
        f"(symbol-level) or a tooling exemption (file-scoped), not both:\n  {misfiled_uisafe}"
    )

    tooling_triples = {(rel, module, member) for (rel, module, member, _tag, _reason) in _TOOLING_EXEMPTIONS}
    overlap = sorted(tooling_triples & _IMPORT_ALLOWLIST)
    assert not overlap, (
        "PROJ-476 no-misfile invariant: these (file, module, member) triples are "
        "in BOTH _TOOLING_EXEMPTIONS and the residual transitional "
        f"_IMPORT_ALLOWLIST. Each tooling import is classified exactly once:\n  {overlap}"
    )

    # Every tooling exemption carries a known category tag.
    bad_tags = sorted({tag for (_r, _m, _mem, tag, _reason) in _TOOLING_EXEMPTIONS if tag not in _TOOLING_EXEMPTION_TAGS})
    assert not bad_tags, (
        f"PROJ-476: unknown tooling-exemption category tag(s): {bad_tags}. "
        f"Allowed: {sorted(_TOOLING_EXEMPTION_TAGS)}"
    )


_TOOLING_TAG_FENCE_MARKER = "PROJ-476 tooling-exemption canonical tag list"


def _parse_pattern5_tooling_tags() -> frozenset[str]:
    """Parse the canonical tooling-exemption category-tag token block under
    Pattern #5 in ``docs/02_PATTERNS.md``.

    The block is a fenced (```` ``` ````) section immediately preceded by a
    marker line containing ``_TOOLING_TAG_FENCE_MARKER``. Each non-blank,
    non-comment line inside the fence is one category tag. Parsed (not
    prose-scraped) so the doc and the guard cannot drift.
    """
    text = _PATTERN5_DOC.read_text(encoding="utf-8")
    lines = text.splitlines()
    tags: set[str] = set()
    marker_seen = False
    in_block = False
    found_block = False
    closed = False
    for line in lines:
        stripped = line.strip()
        if not in_block and _TOOLING_TAG_FENCE_MARKER in line and not stripped.startswith("```"):
            marker_seen = True
            continue
        if stripped.startswith("```"):
            if not in_block and marker_seen:
                in_block = True
                found_block = True
                marker_seen = False
                continue
            if in_block:
                in_block = False
                closed = True
                break
            continue
        if not in_block:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        tags.add(stripped)
    assert found_block, (
        "Pattern #5 tooling-exemption canonical tag block not found in "
        f"{_PATTERN5_DOC} (expected a fenced block immediately preceded by a "
        f"marker line containing {_TOOLING_TAG_FENCE_MARKER!r})."
    )
    assert closed, (
        "Pattern #5 tooling-exemption tag block was opened but never closed "
        f"with a fence in {_PATTERN5_DOC}."
    )
    return frozenset(tags)


def test_tooling_exemption_tags_match_pattern5() -> None:
    """PROJ-476 doc<->guard parity: the set of category tags actually used by
    ``_TOOLING_EXEMPTIONS`` must equal the canonical tag token block embedded
    under Pattern #5 in ``docs/02_PATTERNS.md``. Neither may drift.

    Mirrors PROJ-474's ``_UISAFE_SYMBOLS`` <-> Pattern #5 token-list parity so a
    review-only doc check can't let the prose drift from the implemented tag
    shape while the guard stays green.
    """
    used_tags = frozenset(tag for (_r, _m, _mem, tag, _reason) in _TOOLING_EXEMPTIONS)
    doc_tags = _parse_pattern5_tooling_tags()
    only_in_guard = sorted(used_tags - doc_tags)
    only_in_doc = sorted(doc_tags - used_tags)
    assert used_tags == doc_tags, (
        "PROJ-476 doc<->guard tag-parity drift between the tags used in "
        f"_TOOLING_EXEMPTIONS and the Pattern #5 canonical tag block ({_PATTERN5_DOC}).\n"
        f"In guard but not doc: {only_in_guard}\n"
        f"In doc but not guard: {only_in_doc}"
    )


def _runtime_member_imports(tree: ast.AST, tc_lines: set[int]) -> set[tuple[str, str]]:
    """Collect ``(module, member)`` pairs imported at RUNTIME (outside any
    ``if TYPE_CHECKING:`` block) from a parsed module. Bare
    ``import game.strategy.x`` contributes ``(module, _MODULE_MEMBER_SENTINEL)``.
    """
    out: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if node.lineno in tc_lines:
                continue
            for alias in node.names:
                out.add((alias.name, _MODULE_MEMBER_SENTINEL))
        elif isinstance(node, ast.ImportFrom):
            if node.lineno in tc_lines:
                continue
            if not node.module:
                continue
            for alias in node.names:
                out.add((node.module, alias.name))
    return out


def test_tooling_exemptions_are_live_runtime_imports() -> None:
    """PROJ-476 Phase 4 (Codex exec-audit F2): every ``_TOOLING_EXEMPTIONS``
    triple must correspond to a RUNTIME import that actually exists in source.

    Without this, a stale exemption (e.g. an import later moved under
    ``TYPE_CHECKING`` or deleted) sits in the table forever — exactly the
    ``DesignCatalog`` case the audit found. A ``TYPE_CHECKING``-only or removed
    import is NOT a read-path bypass, so it must NOT keep a tooling exemption.
    """
    stale: list[tuple[str, str, str]] = []
    # Cache parsed trees per file.
    cache: dict[str, set[tuple[str, str]]] = {}
    for (rel, module, member, _tag, _reason) in _TOOLING_EXEMPTIONS:
        if rel not in cache:
            path = REPO_ROOT / rel
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            cache[rel] = _runtime_member_imports(tree, _type_checking_linenos(tree))
        if (module, member) not in cache[rel]:
            stale.append((rel, module, member))
    assert not stale, (
        "PROJ-476 liveness invariant: these _TOOLING_EXEMPTIONS triples are NOT "
        "runtime imports in their files (moved under TYPE_CHECKING or removed). "
        "A non-runtime import is not a read-path bypass — drop the exemption "
        f"instead of keeping a dead entry:\n  {stale}"
    )


def test_tooling_exemption_liveness_check_is_non_vacuous() -> None:
    """Durable proof the liveness scan actually fires on a non-runtime triple,
    so a future refactor of ``_runtime_member_imports`` cannot silently make the
    invariant vacuous (mirrors ``test_no_misfile_invariant_is_non_vacuous``)."""
    # A TYPE_CHECKING-only import must NOT be reported as a runtime import.
    tc_src = (
        "from __future__ import annotations\n"
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from game.strategy.systems.design_catalog import DesignCatalog\n"
    )
    tree = ast.parse(tc_src, filename="synthetic.py")
    runtime = _runtime_member_imports(tree, _type_checking_linenos(tree))
    assert ("game.strategy.systems.design_catalog", "DesignCatalog") not in runtime
    # A real runtime import IS reported.
    rt_src = "from game.strategy.systems.design_catalog import DesignCatalog\n"
    rt_tree = ast.parse(rt_src, filename="synthetic.py")
    rt = _runtime_member_imports(rt_tree, _type_checking_linenos(rt_tree))
    assert ("game.strategy.systems.design_catalog", "DesignCatalog") in rt


def test_tooling_exemption_allows_exact_triple_not_folder() -> None:
    """PROJ-476 positive-control: ``_TOOLING_EXEMPTIONS`` is exact-triple scoped,
    NOT a folder waiver.

    (a) A known tooling triple (``battle_setup_state.py`` ·
        ``game.strategy.data.fleet`` · ``Fleet``) is ALLOWED via the exemption.
    (b) A synthetic NON-exempt live ``GameSession`` import, placed at a path that
        is NOT in ``_TOOLING_EXEMPTIONS`` even though it is under a tooling dir,
        is STILL FLAGGED — so the category cannot be widened into a folder waiver.
    """
    # (a) The real tooling triple is present in the exemption set.
    assert (
        "game/ui/screens/battle_setup_state.py",
        "game.strategy.data.fleet",
        "Fleet",
    ) in {(rel, module, member) for (rel, module, member, _tag, _reason) in _TOOLING_EXEMPTIONS}

    # And the matcher does NOT flag that real import for that real file.
    real_src = "from game.strategy.data.fleet import Fleet\n"
    real_tree = ast.parse(real_src, filename="battle_setup_state.py")
    real_violations = _violations_in_file(
        "game/ui/screens/battle_setup_state.py",
        real_tree,
        _type_checking_linenos(real_tree),
    )
    assert not real_violations, (
        "The exact tooling triple (battle_setup_state.py / fleet / Fleet) must be "
        f"allowed via _TOOLING_EXEMPTIONS, but the matcher flagged: {real_violations}"
    )

    # (b) A live GameSession import in a tooling-dir file that has NO exemption
    # triple is still flagged — the exemption is exact-triple, not folder-wide.
    fake_src = "from game.strategy.engine.game_session import GameSession\n"
    fake_tree = ast.parse(fake_src, filename="galaxy_mode.py")
    fake_violations = _violations_in_file(
        "game/ui/screens/galaxy_test/galaxy_mode.py",  # tooling dir, but no GameSession exemption
        fake_tree,
        _type_checking_linenos(fake_tree),
    )
    blob = "\n".join(fake_violations)
    assert "game_session import GameSession" in blob, (
        "A non-exempt live GameSession import inside a tooling dir must STILL be "
        "flagged — _TOOLING_EXEMPTIONS is exact-triple scoped, not a folder waiver. "
        f"Got: {fake_violations}"
    )
