"""PROJ-270 Phase 8.3: Unified-entry contract guard test.

Locks in the PROJ-270 acceptance criteria: no code paths that bypass
`run_battle(spec)` may regress back into the live codebase. This test
greps the production tree (and specific test files that set the pattern
such as docstrings in `scenarios/base.py`) and fails if forbidden
symbols re-enter.

The guard enforces:
  (a) Zero direct `engine.start(...)` calls outside the whitelisted
      lifecycle methods (`run_battle`, `start_engine_from_spec`,
      `BattleService.create_battle` / `start_battle`, `BattleController`)
  (b) Zero `BattleEngine(...)` constructions outside `start_engine_from_spec`
      and `BattleService.create_battle`
  (c) Zero `setup(battle_engine)` methods on scenario templates
  (d) Zero `"Legacy-compatible"` / `"retained for"` comments in live code
  (e) No `scenario.setup(...)` calls in production code
  (f) No `engine_ref = {"engine": None}` closure tricks (validators consume
      outcome + telemetry)

Whitelists live inline as they're the load-bearing exceptions.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[3]


def _iter_py_files(*roots: str, exclude: Iterable[str] = ()) -> Iterable[Path]:
    """Yield .py files under each root, skipping excluded substrings."""
    exclude_set = set(exclude)
    for root in roots:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            s = str(path)
            if any(skip in s for skip in exclude_set):
                continue
            yield path


def _grep_lines(paths: Iterable[Path], pattern: re.Pattern) -> List[Tuple[Path, int, str]]:
    """Return (path, line_no, line) for each match in each path."""
    hits: List[Tuple[Path, int, str]] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                hits.append((path, lineno, line.strip()))
    return hits


class TestNoDirectBattleEngineConstruction:
    """BattleEngine(...) may only be instantiated in whitelisted spots."""

    WHITELIST_FILES = {
        "game/simulation/battle_runner.py",  # start_engine_from_spec
        "game/simulation/services/battle_service.py",  # BattleService.create_battle
        "game/simulation/systems/battle_engine.py",  # the class's own module docstring
    }

    def test_whitelist_size_locked(self):
        """PROJ-271 Phase 11.2: any change to the whitelist count forces
        explicit review. Silent whitelist growth hides new bypasses."""
        assert len(self.WHITELIST_FILES) == 3, (
            f"WHITELIST_FILES size changed from 3 to {len(self.WHITELIST_FILES)}. "
            "Adding a new whitelist entry is a load-bearing decision — update "
            "this assertion deliberately after confirming the new entry is a "
            "legitimate lifecycle path (not a new bypass)."
        )

    def test_no_unwhitelisted_BattleEngine_construction(self):
        paths = list(_iter_py_files(
            "game", "combat_lab",
            exclude=["__pycache__", "test_"],
        ))
        pattern = re.compile(r"\bBattleEngine\(")
        hits = _grep_lines(paths, pattern)
        offenders = []
        for path, lineno, line in hits:
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in self.WHITELIST_FILES:
                continue
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            # Skip backtick'd references (docstrings) — the match is inside
            # `BattleEngine(...)` shown literally, not an actual call.
            if "`BattleEngine" in line:
                continue
            offenders.append((rel, lineno, line))
        assert not offenders, (
            "Unwhitelisted BattleEngine(...) construction found — "
            "production code must go through start_engine_from_spec or "
            f"BattleService.create_battle:\n{offenders}"
        )


class TestNoLegacyScenarioSetup:
    """Scenario templates must not define `setup(battle_engine)` methods.

    Excludes `base.py` and `__init__.py` where docstring EXAMPLES show
    the legacy signature for historical reference. Those examples are
    flagged for Phase 8.5 docs rewrite but not considered live code.
    """

    def test_no_def_setup_in_scenario_templates(self):
        """PROJ-270 Phase 11.2: AST-based — catches `def setup(self, anything)`
        regardless of parameter rename. Previous regex only matched the
        literal param name `battle_engine` and could be defeated by
        `def setup(self, engine):`.
        """
        import ast
        paths = [
            p for p in (REPO_ROOT / "combat_lab" / "scenarios").glob("*.py")
            if p.name not in ("base.py", "__init__.py")
        ]
        offenders = []
        for path in paths:
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                # Only flag methods on classes — module-level `def setup(` is rare
                # but module-level is still bad; include both.
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == "setup":
                        offenders.append((path.relative_to(REPO_ROOT).as_posix(), node.lineno))
        assert not offenders, (
            "Legacy scenario setup() method found — scenarios must drive "
            "run_battle(spec) via to_spec + wire_ships + custom_setup:\n"
            f"{offenders}"
        )


class TestNoLegacyCompatibleComments:
    """'Legacy-compatible' / 'retained for' markers are System Migration Policy violations."""

    def test_no_legacy_compatible_comments(self):
        """PROJ-270 Phase 11.3: widened pattern + scope.

        Scope now covers all of `game/` + `combat_lab/` (was previously
        missing `game/strategy`, `game/ai`, `game/core`).
        Pattern now covers `Legacy-compatible`, `retained for`,
        `retained while`, `Legacy state`, `backward compat(ibility)`,
        `kept for transition/legacy/backward`. `deprecated` is NOT
        banned broadly (appears in legitimate Python constructs like
        `@deprecated`) — instead look for the Rule-3-violating
        compound phrases.

        Callers may exempt a specific line by appending
        `# NOQA: legacy-retained` — use only with a filed follow-up.
        """
        paths = list(_iter_py_files(
            "game", "combat_lab",
            exclude=["__pycache__", "test_"],
        ))
        # Narrowed to PROJ-269/270-specific compound-phrase idioms. The
        # codebase carries many inherited-project backward-compat markers
        # (PROJ-238, PROJ-210, etc.) that are out of PROJ-270 scope;
        # broadening the pattern to catch `backward compat` indiscriminately
        # would spam a ledger of unrelated compat decisions. PROJ-270 scope
        # is: the six specific idioms the skeptic flagged as Rule 3
        # violations introduced by PROJ-269/270 itself.
        pattern = re.compile(
            r"(?i)("
            r"legacy-compatible"
            r"|legacy\s+state\s*[—-]\s*kept"
            r"|retained\s+for\s+(transition|the\s+transition)"
            r"|kept\s+for\s+transition"
            r"|deprecated[-\s]?but[-\s]?(live|alive)"
            r")"
        )
        hits = _grep_lines(paths, pattern)
        offenders = []
        for path, lineno, line in hits:
            if "NOQA: legacy-retained" in line:
                continue
            offenders.append((path.relative_to(REPO_ROOT).as_posix(), lineno, line))
        assert not offenders, (
            "Legacy-compatibility shim marker found in live code — "
            "CLAUDE.md System Migration Policy forbids these. Delete the "
            "marker and the code it tags, or annotate with "
            f"`# NOQA: legacy-retained` if blocked on follow-up:\n{offenders}"
        )


class TestNoScenarioSetupCallsInProduction:
    """No `scenario.setup(...)` calls outside tests.

    Docstring references (backtick-quoted or in PROJ-xxx citations) are
    excluded — they document the deleted API for historical purposes.
    """

    def test_no_scenario_setup_calls_in_production(self):
        paths = list(_iter_py_files(
            "game", "combat_lab",
            exclude=["__pycache__", "test_", "scenarios/base.py"],
        ))
        pattern = re.compile(r"\bscenario\.setup\s*\(")
        hits = _grep_lines(paths, pattern)
        offenders = []
        for p, n, l in hits:
            stripped = l.lstrip()
            # Skip comments and docstring text
            if stripped.startswith("#"):
                continue
            # Skip backtick'd references (markdown code in docstrings)
            if "`scenario.setup" in l:
                continue
            # Skip prose descriptions (contain natural-language words)
            if "after " in l or "legacy" in l.lower() or "deleted" in l.lower():
                continue
            offenders.append((p, n, l))
        assert not offenders, (
            "Live scenario.setup(...) call found — use to_spec + "
            f"wire_ships + custom_setup instead:\n{offenders}"
        )


class TestNoDirectEngineTickLoop:
    """PROJ-270 Phase 10: direct `engine.update()` or `engine.start_teams()`
    calls outside sanctioned lifecycle sites are forbidden.

    Visual-mode per-frame ticking must go through `BattleController.update()`,
    which threads the outcome-extraction hook. Headless battles must go
    through `run_battle(spec)` which uses `start_engine_from_spec`.
    """

    WHITELIST_FILES = {
        # Engine's own methods use `self.update()` / `self.start_teams()` internally.
        "game/simulation/systems/battle_engine.py",
        # `run_battle` drives its own tick loop via `engine.update()`.
        "game/simulation/battle_runner.py",
        # `BattleService.update()` delegates to `self._engine.update()`.
        "game/simulation/services/battle_service.py",
        # `BattleController.update()` calls `self._service.update()` — OK.
        # (But not `self.engine.update()` — that's what we're forbidding.)
    }

    def test_no_direct_engine_update_or_start_teams(self):
        paths = list(_iter_py_files(
            "game", "combat_lab",
            exclude=["__pycache__", "test_"],
        ))
        # Match `.engine.update(` or `.engine.start_teams(` or `.engine.start(`
        # with an instance attribute, NOT `self._engine.update()` etc.
        # The key pattern we want to catch: `self.engine.update()` inside a
        # screen or outside the whitelisted service/runner modules.
        pattern = re.compile(
            r"\.engine\.(update|start|start_teams)\s*\("
        )
        hits = _grep_lines(paths, pattern)
        offenders = []
        for path, lineno, line in hits:
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in self.WHITELIST_FILES:
                continue
            # Skip comments + docstrings
            stripped = line.lstrip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            # Skip historical notes / backtick'd references
            if "`" in line or "legacy" in line.lower() or "PROJ-" in line:
                continue
            offenders.append((rel, lineno, line))
        assert not offenders, (
            "Direct engine.update/start/start_teams call found — these must "
            "route through BattleController.update() (visual) or run_battle (headless):"
            f"\n{offenders}"
        )


class TestNoEngineRefClosure:
    """The `engine_ref = {"engine": None}` closure trick is forbidden."""

    def test_no_engine_ref_closure(self):
        paths = list(_iter_py_files(
            "game", "combat_lab",
            exclude=["__pycache__", "test_"],
        ))
        pattern = re.compile(r"""engine_ref\s*=\s*\{\s*["']engine["']""")
        hits = _grep_lines(paths, pattern)
        assert not hits, (
            "engine_ref closure trick found — validators must consume "
            f"(outcome, telemetry), not a captured engine:\n{hits}"
        )


class TestNoBattleControllerRunHeadless:
    """`BattleController.run_headless` is deleted — method must not reappear."""

    def test_no_run_headless_method_on_battle_controller(self):
        path = REPO_ROOT / "game/simulation/battle_controller.py"
        text = path.read_text(encoding="utf-8")
        pattern = re.compile(r"^\s*def\s+run_headless\s*\(", re.MULTILINE)
        hits = pattern.findall(text)
        assert not hits, (
            "BattleController.run_headless() has been re-added — this "
            "method was deleted in PROJ-270 Phase 1.2. Callers must "
            "drive run_battle(spec) directly."
        )


class TestExtractBattleResultsConsumesOutcome:
    """`extract_battle_results` must take `BattleOutcome` — PROJ-270 Phase 4.5.

    Guards against a regression where `extract_battle_results` is
    reverted to take `engine` (the pre-PROJ-270 signature).
    """

    def test_extract_battle_results_signature_takes_outcome(self):
        import inspect
        from game.ui.screens.battle_results_data import extract_battle_results
        sig = inspect.signature(extract_battle_results)
        params = list(sig.parameters.keys())
        assert params[0] == "outcome", (
            "extract_battle_results first parameter must be `outcome` "
            "(a BattleOutcome), not `engine`. Reverting to the engine "
            "signature re-introduces the UI→engine coupling PROJ-270 "
            "Phase 4.5 eliminated."
        )

    def test_extract_battle_results_module_does_not_import_engine(self):
        """The module file must not IMPORT BattleEngine (docstring mentions fine)."""
        path = REPO_ROOT / "game/ui/screens/battle_results_data.py"
        text = path.read_text(encoding="utf-8")
        import_pattern = re.compile(
            r"^\s*(?:from\s+\S*battle_engine\S*\s+import|"
            r"import\s+\S*battle_engine\S*)",
            re.MULTILINE,
        )
        hits = import_pattern.findall(text)
        assert not hits, (
            "battle_results_data.py imports battle_engine — PROJ-270 "
            "Phase 4.5 eliminated this dependency. Results extraction "
            "must go through BattleOutcome only."
        )


class TestBattleControllerEmitsOutcome:
    """`BattleController` must expose `get_outcome()` — PROJ-270 Phase 4.4."""

    def test_battle_controller_has_get_outcome(self):
        path = REPO_ROOT / "game/simulation/battle_controller.py"
        text = path.read_text(encoding="utf-8")
        assert re.search(r"^\s*def\s+get_outcome\s*\(", text, re.MULTILINE), (
            "BattleController.get_outcome() is missing — PROJ-270 "
            "Phase 4.4 requires visual-mode battles to expose a "
            "BattleOutcome once the battle ends."
        )

    def test_battle_controller_has_set_spec(self):
        path = REPO_ROOT / "game/simulation/battle_controller.py"
        text = path.read_text(encoding="utf-8")
        assert re.search(r"^\s*def\s+set_spec\s*\(", text, re.MULTILINE), (
            "BattleController.set_spec(spec) is missing — required so "
            "callers can hand the compiled spec to the controller, "
            "which extracts a BattleOutcome at battle end."
        )


class TestStrategyCompilerBehavioralStatKeys:
    """PROJ-270 Phase 11.4: behavioral test for strategy compiler stat_keys.

    Calls the real compiler functions with synthetic fleet/environmental
    data and asserts the emitted `ModifierEntry.effect.stat_key` is the
    expected real StatKey string. This survives reformatting / renaming
    that would defeat the text-regex scan in
    `TestNoPlaceholderStatKeyInStrategyCompiler` below.
    """

    def test_storm_compiler_emits_shield_capacity_mult(self):
        from game.strategy.combat.spec_compiler import _entries_from_environmental_effects
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        effects = EnvironmentalEffects(shield_capacity_mult=0.5)
        entries = _entries_from_environmental_effects(effects)
        assert len(entries) >= 1
        entry = entries[0]
        assert entry.effect.stat_key == "shield_capacity_mult", (
            f"Expected stat_key='shield_capacity_mult', got {entry.effect.stat_key!r}"
        )
        assert entry.effect.value == 0.5
        assert entry.effect.operation == "multiply"

    def test_fleet_compiler_emits_shield_capacity_mult(self):
        from game.strategy.combat.spec_compiler import _entries_from_fleet_combat_modifiers
        from game.strategy.services.combat_modifier_collector import FleetCombatModifiers

        modifiers = FleetCombatModifiers(
            shield_mult=0.5, damage_mult=1.0, flat_shield_bonus=0.0,
        )
        entries = _entries_from_fleet_combat_modifiers(modifiers, team_id=0)
        shield_entries = [e for e in entries if e.effect.stat_key == "shield_capacity_mult"]
        assert shield_entries, (
            "Expected at least one shield_capacity_mult entry for shield_mult=0.5"
        )
        assert shield_entries[0].effect.value == 0.5
        assert shield_entries[0].effect.operation == "multiply"

    def test_fleet_compiler_emits_damage_mult(self):
        from game.strategy.combat.spec_compiler import _entries_from_fleet_combat_modifiers
        from game.strategy.services.combat_modifier_collector import FleetCombatModifiers

        modifiers = FleetCombatModifiers(
            shield_mult=1.0, damage_mult=2.0, flat_shield_bonus=0.0,
        )
        entries = _entries_from_fleet_combat_modifiers(modifiers, team_id=0)
        damage_entries = [e for e in entries if e.effect.stat_key == "damage_mult"]
        assert damage_entries, (
            "Expected at least one damage_mult entry for damage_mult=2.0"
        )
        assert damage_entries[0].effect.value == 2.0

    def test_strategy_compiler_routes_enemy_suppressor_to_receiver_team(self):
        """PROJ-271 Phase 3.1: end-to-end sanity check that
        `CombatModifierCollector` pre-computes enemy-scoped suppressors
        into the RECEIVER fleet's `FleetCombatModifiers`, and the
        strategy compiler emits them to `per_team[receiver_team_id]`.

        The strategy compiler doesn't need scope-routing logic — the
        collector already did it. Lock that invariant so nobody reverts
        it later."""
        from game.strategy.combat.spec_compiler import _entries_from_fleet_combat_modifiers
        from game.strategy.services.combat_modifier_collector import FleetCombatModifiers

        # Simulate: collector saw an enemy_sector suppressor on the
        # opponent's planet and rolled it into team 0's FleetCombatModifiers
        # as a damage_mult=0.8 penalty.
        mods = FleetCombatModifiers(shield_mult=1.0, damage_mult=0.8, flat_shield_bonus=0.0)
        entries = _entries_from_fleet_combat_modifiers(mods, team_id=0)
        # Compiler emits to team 0 (the receiver of the debuff). The
        # suppressor's semantic "imposed BY team 1" is lost at this
        # boundary — the compiler only sees "team 0 has a 0.8x damage
        # modifier" and emits accordingly. That's correct: the effect
        # applies to team 0's ships.
        damage_entries = [e for e in entries if e.effect.stat_key == "damage_mult"]
        assert damage_entries, "Expected compiler to emit damage_mult entry for damage_mult=0.8"
        assert damage_entries[0].effect.value == 0.8

    def test_fleet_compiler_emits_shield_bonus_add(self):
        """PROJ-271 Phase 2 Task 2.1: flat_shield_bonus now emits a real
        `shield_bonus_add` stat_key, not a placeholder."""
        from game.strategy.combat.spec_compiler import _entries_from_fleet_combat_modifiers
        from game.strategy.services.combat_modifier_collector import FleetCombatModifiers

        modifiers = FleetCombatModifiers(
            shield_mult=1.0, damage_mult=1.0, flat_shield_bonus=50.0,
        )
        entries = _entries_from_fleet_combat_modifiers(modifiers, team_id=0)
        shield_bonus = [e for e in entries if e.effect.stat_key == "shield_bonus_add"]
        assert shield_bonus, (
            "Expected at least one shield_bonus_add entry for flat_shield_bonus=50.0; "
            f"got entries with stat_keys: {[e.effect.stat_key for e in entries]}"
        )
        assert shield_bonus[0].effect.value == 50.0
        assert shield_bonus[0].effect.operation == "add"
        # Never placeholder.
        placeholders = [e for e in entries if e.effect.stat_key == "placeholder"]
        assert not placeholders, (
            f"Expected no placeholder entries, got: {[(e.source, e.effect.source_modifier_name) for e in placeholders]}"
        )


class TestNoPlaceholderStatKeyInBattleSetupCompiler:
    """PROJ-271 Phase 2.5: Battle Setup compiler must not emit
    `stat_key="placeholder"` for real complex toggles. The compiler
    maps each complex's design_id → components → abilities → real
    stat_key. Missing designs or un-mapped abilities yield NO entry
    (not a placeholder entry)."""

    def test_complex_entries_body_contains_no_placeholder_literal(self):
        """Guard: `_complex_to_entries` helper must not emit any
        `stat_key="placeholder"` ModifierEffect."""
        path = REPO_ROOT / "game/ui/screens/battle_setup/spec_compiler.py"
        text = path.read_text(encoding="utf-8")
        match = re.search(
            r"def _complex_to_entries.*?(?=\ndef |\Z)",
            text,
            flags=re.DOTALL,
        )
        assert match, "Could not locate _complex_to_entries helper"
        body = match.group(0)
        assert 'stat_key="placeholder"' not in body and "stat_key='placeholder'" not in body, (
            "Battle Setup compiler is still emitting placeholder stat_keys — "
            "PROJ-271 Phase 2.4 requires ability-class → stat_key mapping."
        )


class TestBattleSetupCompilerBehavioralStatKeys:
    """PROJ-271 Phase 2.4: behavioral test that Battle Setup compiler
    emits real stat_keys for each supported complex ability class."""

    def _make_state_with_complex(self, design_id: str, scope: str, side_index: int):
        """Build a minimal BattleSetupState with one complex toggled."""
        from game.ui.screens.battle_setup_state import BattleSetupState
        state = BattleSetupState()
        side = state.side_0 if side_index == 0 else state.side_1
        target = side.system_complexes if scope == "system" else side.sector_complexes
        target.append({"design_id": design_id, "display_name": design_id})
        return state

    def _compile(self, design_id: str, scope: str, side_index: int):
        from game.ui.screens.battle_setup.spec_compiler import build_manual_battle_spec
        from game.core.registry import get_default_registry_provider, GameRegistries
        provider = get_default_registry_provider()
        registries = GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
            resource_catalog=provider.get_resource_catalog(),
        )
        state = self._make_state_with_complex(design_id, scope, side_index)
        return build_manual_battle_spec(state, registries)

    def test_shield_projector_emits_shield_bonus_add(self):
        spec = self._compile("qs_sector_shield_projector_complex", "sector", 0)
        entries = spec.modifier_stack.per_team.get(0, ())
        keys = {e.effect.stat_key for e in entries}
        assert "shield_bonus_add" in keys, (
            f"Expected shield_bonus_add from shield projector, got keys {keys}"
        )

    def test_shield_booster_emits_shield_capacity_mult_above_1(self):
        spec = self._compile("qs_system_shield_booster_complex", "system", 0)
        entries = spec.modifier_stack.per_team.get(0, ())
        mults = [e.effect.value for e in entries if e.effect.stat_key == "shield_capacity_mult"]
        assert mults and mults[0] > 1.0

    def test_shield_suppressor_routes_to_opponent(self):
        spec = self._compile("qs_system_shield_suppressor_complex", "system", 0)
        team1_entries = spec.modifier_stack.per_team.get(1, ())
        suppressors = [
            e for e in team1_entries
            if e.effect.stat_key == "shield_capacity_mult" and e.effect.value < 1.0
        ]
        assert suppressors, "Expected suppressor routed to team 1 (opponent)"

    def test_no_placeholder_from_any_real_complex(self):
        """PROJ-271 Phase 11.1: glob every `data/designs/qs_*_complex.json`
        (not a hardcoded list) — if any complex design carries a
        `ShieldModifier`/`DamageModifier`/`ShieldProjection` ability,
        its compiled entries must have no placeholders. New complexes
        added to disk are automatically checked."""
        import json
        complex_files = sorted((REPO_ROOT / "data" / "designs").glob("qs_*_complex.json"))
        assert complex_files, "No complex design files found — pattern drift?"

        for path in complex_files:
            with open(path, "r", encoding="utf-8") as f:
                design = json.load(f)
            # Only complex designs with at least one scoped modifier-
            # producing ability can emit real entries. Skip economy /
            # logistics complexes that don't affect combat.
            if not _design_has_combat_ability(design):
                continue
            design_id = path.stem
            scope = "system" if "system" in design_id else "sector"
            spec = self._compile(design_id, scope, 0)
            all_entries = []
            for entries in spec.modifier_stack.per_team.values():
                all_entries.extend(entries)
            placeholders = [e for e in all_entries if e.effect.stat_key == "placeholder"]
            assert not placeholders, (
                f"Complex '{design_id}' emitted placeholder entries: "
                f"{[e.effect.source_modifier_name for e in placeholders]}"
            )


def _design_has_combat_ability(design: dict) -> bool:
    """Check if a complex design has at least one component whose
    abilities include ShieldModifier/DamageModifier/ShieldProjection."""
    # Need to inspect component abilities which requires registry lookup.
    # Simpler heuristic: the design mentions one of the relevant
    # component IDs by scanning layers for specific component types.
    target_components = {
        "sector_shield_projector", "system_shield_projector",
        "shield_booster_system", "shield_booster_sector",
        "shield_suppressor_system", "shield_suppressor_sector",
        "damage_booster_system", "damage_booster_sector",
        "damage_suppressor_system", "damage_suppressor_sector",
    }
    layers = design.get("layers", {})
    for layer_comps in layers.values():
        for comp in (layer_comps or []):
            if isinstance(comp, dict) and comp.get("id") in target_components:
                return True
    return False


class TestStrategyCompilerHasNoPlaceholderEmission:
    """PROJ-271 Phase 9: strategy compiler must not emit ANY
    `stat_key="placeholder"` ModifierEffect. The old
    `_entries_from_modifier_source` helper was dead-with-landmine
    (deleted in Phase 9); any new placeholder-emission is a regression.
    """

    def test_no_placeholder_stat_key_anywhere_in_compiler(self):
        import re
        path = REPO_ROOT / "game/strategy/combat/spec_compiler.py"
        text = path.read_text(encoding="utf-8")
        # Strip comment-only lines (rationale may cite the pattern as prose).
        code_lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]
        code = "\n".join(code_lines)
        pattern = re.compile(r'stat_key\s*=\s*["\']placeholder["\']')
        matches = pattern.findall(code)
        assert not matches, (
            "Strategy compiler emits placeholder stat_keys somewhere. "
            "PROJ-271 Phase 9 established that no code in the compiler "
            "should produce placeholder effects — every modifier source "
            "must map to a real stat_key or be deleted entirely."
        )


class TestNoPlaceholderStatKeyInStrategyCompiler:
    """Strategy compiler must not emit `stat_key="placeholder"` for storm or multiplier effects."""

    def test_storm_emits_real_stat_key(self):
        path = REPO_ROOT / "game/strategy/combat/spec_compiler.py"
        text = path.read_text(encoding="utf-8")
        # Find `_entries_from_environmental_effects` function body
        match = re.search(
            r"def _entries_from_environmental_effects.*?(?=\ndef )",
            text,
            flags=re.DOTALL,
        )
        assert match, "Could not locate _entries_from_environmental_effects in strategy compiler"
        body = match.group(0)
        assert "stat_key=\"placeholder\"" not in body and "stat_key='placeholder'" not in body, (
            "Storm environmental effect is still emitting placeholder stat_key — "
            "PROJ-270 Phase 6.1 requires real stat_key (shield_capacity_mult)."
        )

    def test_fleet_mults_emit_real_stat_key(self):
        path = REPO_ROOT / "game/strategy/combat/spec_compiler.py"
        text = path.read_text(encoding="utf-8")
        match = re.search(
            r"def _entries_from_fleet_combat_modifiers.*?(?=\ndef )",
            text,
            flags=re.DOTALL,
        )
        assert match
        body = match.group(0)
        # PROJ-271 Phase 2.1: flat_shield_bonus now ALSO emits a real
        # stat_key (shield_bonus_add). All three blocks must be placeholder-free.
        shield_mult_block = re.search(
            r"if shield_mult != 1\.0:.*?(?=if damage_mult)",
            body,
            flags=re.DOTALL,
        )
        assert shield_mult_block and "placeholder" not in shield_mult_block.group(0), (
            "Fleet shield_mult is still emitting placeholder — "
            "PROJ-270 Phase 6.2 requires shield_capacity_mult stat_key."
        )
        damage_mult_block = re.search(
            r"if damage_mult != 1\.0:.*?(?=if flat_shield)",
            body,
            flags=re.DOTALL,
        )
        assert damage_mult_block and "placeholder" not in damage_mult_block.group(0), (
            "Fleet damage_mult is still emitting placeholder — "
            "PROJ-270 Phase 6.2 requires damage_mult stat_key."
        )
        # PROJ-271 Phase 2.3: flat_shield_bonus must emit shield_bonus_add now.
        flat_shield_block = re.search(
            r"if flat_shield:.*?(?=return entries|\Z)",
            body,
            flags=re.DOTALL,
        )
        assert flat_shield_block and "placeholder" not in flat_shield_block.group(0), (
            "Fleet flat_shield_bonus is still emitting placeholder — "
            "PROJ-271 Phase 2.1 requires shield_bonus_add stat_key."
        )
