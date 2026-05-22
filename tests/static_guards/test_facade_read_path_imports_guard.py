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

The allowlist below enumerates EVERY runtime ``game.strategy.*`` import
currently present under ``game/ui`` (snapshot 2026-05-21), so the guard is GREEN
on commit. Its value is blocking *net-new* non-allowlisted imports. Entries are
categorised:

  UISAFE   — the documented UI-safe config/value/enum surface (Pattern #5):
             GameConfig/game_config scalars, RaceConfig + label tuples,
             EnvironmentalPreference, habitability factors, ContainableKind,
             ActivationPhase.
  CLUSTER  — build-queue cluster live-domain imports; PROJ-472 1B removes these
             as the cluster migrates onto facade queries. (TEMPORARY)
  FLEETCAP — FleetCapabilityCalculator late-imports; deferred to PROJ-475
             (no facade query exists yet).
  TAIL     — the deferred ~75-file tail (battle_setup / galaxy_test / race_setup /
             builder / save-game / misc service-helper reads); PROJ-474/475/476.
             Allowlisted-with-reason now so the guard is green and net-new
             bypasses are still caught.
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

# Exact (relative_posix_path, module, member) allowlist. ``member`` is the
# imported name; for bare ``import game.strategy.x`` it is the sentinel
# ``"__MODULE__"``. See module docstring for category meanings.
_IMPORT_ALLOWLIST: frozenset[tuple[str, str, str]] = frozenset({
    # --- UISAFE: documented UI-safe config/value/enum surface (Pattern #5) ---
    ('game/ui/panels/race_environment_panel.py', 'game.strategy.data.environmental_preference', 'EnvironmentalPreference'),
    ('game/ui/panels/race_environment_panel.py', 'game.strategy.data.habitability_factors', 'iter_gas_factors'),
    ('game/ui/panels/race_environment_panel.py', 'game.strategy.data.habitability_factors', 'iter_scalar_factors'),
    ('game/ui/panels/race_environment_panel.py', 'game.strategy.data.homeworld_presets', 'apply_preset_to_config'),
    ('game/ui/panels/race_environment_panel.py', 'game.strategy.data.homeworld_presets', 'get_preset_for_planet_type'),
    ('game/ui/panels/race_environment_panel.py', 'game.strategy.data.homeworld_presets', 'get_preset_id_from_name'),
    ('game/ui/panels/race_environment_panel.py', 'game.strategy.data.homeworld_presets', 'load_homeworld_presets'),
    ('game/ui/panels/race_environment_panel.py', 'game.strategy.data.race_point_budget', 'RacePointBudget'),
    ('game/ui/panels/race_aptitudes_panel.py', 'game.strategy.data.race_point_budget', 'RacePointBudget'),
    ('game/ui/panels/race_identity_panel.py', 'game.strategy.data.race_config', 'GOVERNMENT_ORGANIZATIONS'),
    ('game/ui/panels/race_identity_panel.py', 'game.strategy.data.race_config', 'GOVERNMENT_TYPES'),
    ('game/ui/panels/race_identity_panel.py', 'game.strategy.data.race_config', 'LEADER_TITLES'),
    ('game/ui/panels/race_identity_panel.py', 'game.strategy.data.race_config', 'PHYSICAL_TYPES'),
    ('game/ui/panels/race_identity_panel.py', 'game.strategy.data.race_config', 'SOCIETY_TYPES'),
    ('game/ui/panels/race_summary_panel.py', 'game.strategy.data.habitability_factors', 'iter_gas_factors'),
    ('game/ui/panels/race_summary_panel.py', 'game.strategy.data.habitability_factors', 'iter_scalar_factors'),
    ('game/ui/panels/race_summary_panel.py', 'game.strategy.data.race_point_budget', 'RacePointBudget'),
    ('game/ui/widgets/preference_row.py', 'game.strategy.data.environmental_preference', 'EnvironmentalPreference'),
    ('game/ui/screens/new_game_setup_controller.py', 'game.strategy.engine.game_config', 'DEFAULT_SYSTEM_COUNT'),
    ('game/ui/screens/new_game_setup_controller.py', 'game.strategy.engine.game_config', 'GameConfig'),
    ('game/ui/screens/new_game_setup_controller.py', 'game.strategy.engine.game_config', 'PlayerConfig'),
    ('game/ui/screens/new_game_setup_controller.py', 'game.strategy.engine.game_config', 'THEME_DEFAULTS'),
    ('game/ui/screens/new_game_setup_screen.py', 'game.strategy.engine.game_config', 'DEFAULT_SYSTEM_COUNT'),
    ('game/ui/screens/new_game_setup_screen.py', 'game.strategy.engine.game_config', 'GameConfig'),
    ('game/ui/screens/new_game_setup_screen.py', 'game.strategy.engine.game_config', 'MAX_SYSTEM_COUNT'),
    ('game/ui/screens/new_game_setup_screen.py', 'game.strategy.engine.game_config', 'MIN_SYSTEM_COUNT'),
    ('game/ui/screens/new_game_setup_screen.py', 'game.strategy.engine.game_config', 'THEME_DEFAULTS'),
    ('game/ui/screens/new_game_setup_screen.py', 'game.strategy.engine.game_config', 'VALID_GALAXY_TYPES'),
    ('game/ui/screens/new_game_setup_view_model.py', 'game.strategy.engine.game_config', 'DEFAULT_SYSTEM_COUNT'),
    ('game/ui/screens/new_game_setup_view_model.py', 'game.strategy.engine.game_config', 'MAX_SYSTEM_COUNT'),
    ('game/ui/screens/new_game_setup_view_model.py', 'game.strategy.engine.game_config', 'MIN_SYSTEM_COUNT'),
    ('game/ui/screens/planet_abilities_controller.py', 'game.strategy.data.component_activation_state', 'ActivationPhase'),
    ('game/ui/screens/transfer_container_rows.py', 'game.strategy.data.containable', 'ContainableKind'),
    ('game/ui/screens/transfer_mass_preview.py', 'game.strategy.data.containable', 'ContainableKind'),
    ('game/ui/screens/transfer_view_model.py', 'game.strategy.data.containable', 'ContainableKind'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.data.component_activation_state', 'ActivationPhase'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.data.component_activation_state', 'ComponentActivationState'),
    ('game/ui/screens/strategy_fleet_command_router.py', 'game.strategy.data.component_activation_state', 'ActivationPhase'),

    # --- CLUSTER: build-queue live-domain imports; PROJ-472 1B migrates (TEMPORARY) ---
    ('game/ui/screens/build_queue_input_router.py', 'game.strategy.data.build_queue_source', 'BuildQueueSource'),  # PROJ-472 1B will migrate
    ('game/ui/screens/build_queue_input_router.py', 'game.strategy.data.build_queue_source', 'collect_build_queues_at_hex'),  # PROJ-472 1B will migrate
    ('game/ui/screens/build_queue_screen.py', 'game.strategy.data.build_queue_source', 'BuildQueueSource'),  # PROJ-472 1B will migrate
    ('game/ui/screens/build_queue_screen.py', 'game.strategy.data.build_queue_source', 'collect_build_queues_at_hex'),  # PROJ-472 1B will migrate
    ('game/ui/screens/empire_build_queue_window.py', 'game.strategy.data.build_queue_source', 'BuildQueueSource'),  # PROJ-472 1B will migrate
    ('game/ui/screens/empire_build_queue_window.py', 'game.strategy.data.build_queue_source', 'collect_all_build_queues_for_empire'),  # PROJ-472 1B will migrate
    ('game/ui/screens/strategy_detail_formatter.py', 'game.strategy.data.build_queue_source', 'colony_has_planetary_yard'),  # PROJ-472 1B/1C will migrate

    # --- FLEETCAP: FleetCapabilityCalculator late-imports; deferred to PROJ-475 ---
    ('game/ui/screens/fleet_data_source.py', 'game.strategy.data.fleet_capability_calculator', 'FleetCapabilityCalculator'),
    ('game/ui/screens/fleet_report_filters.py', 'game.strategy.data.fleet_capability_calculator', 'FleetCapabilityCalculator'),

    # --- TAIL: deferred ~75-file tail (PROJ-474/475/476); allowlisted-with-reason ---
    ('game/ui/panels/build_queue_controller.py', 'game.strategy.services.design_validator', 'DesignValidator'),
    ('game/ui/panels/empire_treasury_panel.py', 'game.strategy.services.empire_economy_service', 'EmpireEconomySnapshot'),
    ('game/ui/panels/race_description_panel.py', 'game.strategy.services.race_description_llm_controller', 'FieldStatus'),
    ('game/ui/panels/system_tree_panel.py', 'game.strategy.services.system_effects_collector', 'collect_sector_effects'),
    ('game/ui/panels/system_tree_panel.py', 'game.strategy.services.system_effects_collector', 'collect_system_effects'),
    ('game/ui/panels/system_tree_panel.py', 'game.strategy.services.system_effects_collector', 'format_intrinsic_ability_magnitude'),
    ('game/ui/screens/battle_setup/constants.py', 'game.strategy.data.fleet_hierarchy', 'BattleRole'),
    ('game/ui/screens/battle_setup/controller.py', 'game.strategy.data.fleet_hierarchy', 'BattleRole'),
    ('game/ui/screens/battle_setup/fleet_hierarchy_editor.py', 'game.strategy.data.fleet_hierarchy', 'CombatPolicy'),
    ('game/ui/screens/battle_setup/fleet_hierarchy_editor.py', 'game.strategy.data.ship_instance', 'ShipInstance'),
    ('game/ui/screens/battle_setup/fleet_hierarchy_editor.py', 'game.strategy.data.squadron', 'Squadron'),
    ('game/ui/screens/battle_setup/fleet_hierarchy_editor.py', 'game.strategy.data.task_force', 'TaskForce'),
    ('game/ui/screens/battle_setup_state.py', 'game.strategy.data.fleet', 'Fleet'),
    ('game/ui/screens/battle_setup_state.py', 'game.strategy.data.ship_instance', 'ShipInstance'),
    ('game/ui/screens/build_queue_panel_factory.py', 'game.strategy.services.planet_economy_projector', 'compute_planet_production'),
    ('game/ui/screens/build_queue_screen.py', 'game.strategy.services.planet_economy_projector', 'compute_planet_production'),
    ('game/ui/screens/builder/right_panel.py', 'game.strategy.data.design_role_registry', 'get_default_design_role_registry'),
    ('game/ui/screens/builder/stat_getters.py', 'game.strategy.services.superweapon_registry', 'SUPERWEAPONS'),
    ('game/ui/screens/builder/stat_rows_dynamic.py', 'game.strategy.services.ability_metadata', 'StrategicKind'),
    ('game/ui/screens/builder/stat_rows_dynamic.py', 'game.strategy.services.ability_metadata', 'abilities_with_kind_tag'),
    ('game/ui/screens/cargo_quick_dialog_controller.py', 'game.strategy.services.cargo_transfer_service', 'CargoTransferService'),
    ('game/ui/screens/design_selector_window.py', 'game.strategy.data.design_role_registry', 'get_default_design_role_registry'),
    ('game/ui/screens/design_selector_window.py', 'game.strategy.systems.design_catalog', 'DesignCatalog'),
    ('game/ui/screens/empire_panel_window.py', 'game.strategy.config.economy_config', 'get_default_economy_config'),
    ('game/ui/screens/empire_panel_window.py', 'game.strategy.services.empire_economy_service', 'EmpireEconomyService'),
    ('game/ui/screens/fleet_data_source.py', 'game.strategy.services.component_abilities', 'has_warp_capability'),
    ('game/ui/screens/fleet_data_source.py', 'game.strategy.services.component_abilities', 'ship_has_ability'),
    ('game/ui/screens/fleet_data_source.py', 'game.strategy.services.fleet_speed_calculator', 'FleetSpeedCalculator'),
    ('game/ui/screens/fleet_menu_items.py', 'game.strategy.data.deployed_group', 'FighterWing'),
    ('game/ui/screens/fleet_menu_items.py', 'game.strategy.data.deployed_group', 'SatelliteConstellation'),
    ('game/ui/screens/fleet_report_filters.py', 'game.strategy.services.component_abilities', 'has_warp_capability'),
    ('game/ui/screens/fleet_report_filters.py', 'game.strategy.services.component_abilities', 'ship_has_ability'),
    ('game/ui/screens/fleet_report_filters.py', 'game.strategy.services.fleet_speed_calculator', 'FleetSpeedCalculator'),
    ('game/ui/screens/galaxy_test/constants.py', 'game.strategy.data.planet', 'PlanetType'),
    ('game/ui/screens/galaxy_test/galaxy_mode.py', 'game.strategy.data.galaxy', 'Galaxy'),
    ('game/ui/screens/galaxy_test/galaxy_mode.py', 'game.strategy.engine.game_config', 'VALID_GALAXY_TYPES'),
    ('game/ui/screens/galaxy_test/galaxy_mode.py', 'game.strategy.generation.density.density_map', 'DensityMap'),
    ('game/ui/screens/galaxy_test/galaxy_mode.py', 'game.strategy.generation.loaders.galaxy_layouts_loader', 'GalaxyLayoutsLoader'),
    ('game/ui/screens/galaxy_test/galaxy_mode.py', 'game.strategy.generation.placement_strategies', 'DensityBasedPlacementStrategy'),
    ('game/ui/screens/galaxy_test/galaxy_mode.py', 'game.strategy.generation.placement_strategies', 'RandomPlacementStrategy'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.data.planet', 'Planet'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.data.planet', 'PlanetType'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.data.planet_gen', 'PlanetGenerator'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.data.planet_physics', 'MASS_EARTH'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.data.planet_physics', 'calculate_escape_velocity'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.data.planet_physics', 'calculate_surface_gravity'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.data.star_system', 'StarSystem'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.data.stars', 'Star'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.data.stars', 'StarGenerator'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.generation.loaders.system_blueprints_loader', 'SystemBlueprintsLoader'),
    ('game/ui/screens/galaxy_test/system_mode.py', 'game.strategy.generation.planet_image_registry', 'PlanetImageRegistry'),
    ('game/ui/screens/orders_window.py', 'game.strategy.data.order_types', 'OrderType'),
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
    ('game/ui/screens/race_setup/controller.py', 'game.strategy.data.race_config', 'RaceConfig'),
    ('game/ui/screens/race_setup/controller.py', 'game.strategy.data.race_point_budget', 'RacePointBudget'),
    ('game/ui/screens/race_setup/controller.py', 'game.strategy.systems.race_library', 'RaceLibrary'),
    ('game/ui/screens/race_setup/controller.py', 'game.strategy.systems.race_randomizer', 'RaceRandomizer'),
    ('game/ui/screens/race_setup/llm_dialog_service.py', 'game.strategy.services.race_description_llm_controller', 'FieldStatus'),
    ('game/ui/screens/race_setup/panel_factory.py', 'game.strategy.data.race_caption_loader', 'RaceCaptionLoader'),
    ('game/ui/screens/race_setup/panel_factory.py', 'game.strategy.services.race_description_llm_controller', 'RaceDescriptionLLMController'),
    ('game/ui/screens/race_setup/screen.py', 'game.strategy.data.race_config', 'RaceConfig'),
    ('game/ui/screens/race_setup/screen.py', 'game.strategy.systems.race_library', 'RaceLibrary'),
    ('game/ui/screens/race_setup/screen.py', 'game.strategy.systems.race_randomizer', 'RaceRandomizer'),
    ('game/ui/screens/race_validator.py', 'game.strategy.data.race_point_budget', 'RacePointBudget'),
    ('game/ui/screens/save_selection_window.py', 'game.strategy.systems.save_game_service', 'SaveGameService'),
    ('game/ui/screens/species_selector_mixin.py', 'game.strategy.systems.race_library', 'RaceLibrary'),
    ('game/ui/screens/new_game_setup_screen.py', 'game.strategy.systems.race_library', 'RaceLibrary'),
    ('game/ui/screens/strategy_build_queue_manager.py', 'game.strategy.data.order_types', 'OrderType'),
    ('game/ui/screens/strategy_build_queue_manager.py', 'game.strategy.systems.design_catalog', 'DesignCatalog'),
    ('game/ui/screens/strategy_click_dispatcher.py', 'game.strategy.data.physics', 'SectorEnvironment'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.data.bay_inventory', 'DropPod'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.data.carried_vehicle', 'CarriedVehicle'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.data.order_types', 'OrderType'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.formulas.habitability', 'calculate_habitability'),
    ('game/ui/screens/strategy_detail_fmt.py', 'game.strategy.services.component_abilities', 'extract_abilities_from_component'),
    ('game/ui/screens/strategy_detail_formatter.py', 'game.strategy.services.component_abilities', 'extract_abilities_from_component'),
    ('game/ui/screens/strategy_detail_formatter.py', 'game.strategy.services.planet_economy_projector', 'compute_planet_production'),
    ('game/ui/screens/strategy_event_router.py', 'game.strategy.config.economy_config', 'get_default_economy_config'),
    ('game/ui/screens/strategy_event_router.py', 'game.strategy.systems.race_library', 'RaceLibrary'),
    ('game/ui/screens/strategy_fleet_command_router.py', 'game.strategy.services.component_abilities', 'extract_abilities_from_component'),
    ('game/ui/screens/strategy_game_state_manager.py', 'game.strategy.systems.save_game_service', 'SaveGameService'),
    ('game/ui/screens/strategy_render/cursor.py', 'game.strategy.services.cargo_transfer_service', 'project_fleet_position'),
    ('game/ui/screens/strategy_render/dyson_spheres.py', 'game.strategy.data.planet', 'PlanetType'),
    ('game/ui/screens/strategy_render/systems.py', 'game.strategy.data.planet', 'PlanetType'),
    # Composition root: StrategyScreen rebuilds the facade from a concrete
    # GameSession in its test-swap setter. Transitional; deprecation is PROJ-475.
    ('game/ui/screens/strategy_screen.py', 'game.strategy.engine.game_session', 'GameSession'),
    ('game/ui/screens/strategy_screen_lifecycle.py', 'game.strategy.systems.save_game_service', 'SaveGameService'),
    ('game/ui/screens/strategy_screen_order_editing.py', 'game.strategy.data.order_types', 'OrderType'),
    ('game/ui/screens/strategy_superweapons.py', 'game.strategy.services.galaxy_pathfinding_service', 'GalaxyPathfindingService'),
    ('game/ui/screens/strategy_windows/event_log_window_ctrl.py', 'game.strategy.services.replay_resolver', 'ReplayResolver'),
    ('game/ui/screens/strategy_windows/event_log_window_ctrl.py', 'game.strategy.systems.save_game_service', 'SaveGameService'),
    ('game/ui/screens/transfer_controller.py', 'game.strategy.services.cargo_transfer_service', 'project_fleet_position'),
    ('game/ui/screens/workshop_event_router.py', 'game.strategy.data.design_role_registry', 'get_default_design_role_registry'),
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
                if (rel, mod, _MODULE_MEMBER_SENTINEL) in _IMPORT_ALLOWLIST:
                    continue
                violations.append(f"{rel}:{node.lineno} import {mod}")
        elif isinstance(node, ast.ImportFrom):
            if node.lineno in tc_lines:
                continue
            mod = node.module
            if not (mod and mod.startswith("game.strategy")):
                continue
            if _is_always_allowed_module(mod):
                continue
            for alias in node.names:
                if (rel, mod, alias.name) in _IMPORT_ALLOWLIST:
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
    is always allowed. Every other current runtime import is on
    ``_IMPORT_ALLOWLIST`` (UI-safe surface, or transitional CLUSTER/FLEETCAP/TAIL
    entries removed as PROJ-472 1B / PROJ-474/475/476 migrate them). A net-new
    import fails here until allowlisted or routed through the facade.
    ``if TYPE_CHECKING:`` imports are ignored.
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
            "UI code reads session-owned state through the facade. If this is "
            "a documented UI-safe surface or an intentional transitional read, "
            "add the (file, module, member) triple to _IMPORT_ALLOWLIST with a "
            "category/reason comment."
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
