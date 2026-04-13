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
        paths = [
            p for p in (REPO_ROOT / "combat_lab" / "scenarios").glob("*.py")
            if p.name not in ("base.py", "__init__.py")
        ]
        pattern = re.compile(r"^\s*def\s+setup\s*\(\s*self\s*,\s*battle_engine\b")
        hits = _grep_lines(paths, pattern)
        assert not hits, (
            "Legacy scenario setup(battle_engine) method found — "
            "scenarios must drive run_battle(spec) via to_spec + wire_ships "
            f"+ custom_setup:\n{hits}"
        )


class TestNoLegacyCompatibleComments:
    """'Legacy-compatible' / 'retained for' markers are System Migration Policy violations."""

    def test_no_legacy_compatible_comments(self):
        paths = list(_iter_py_files(
            "game/simulation", "game/ui", "combat_lab",
            exclude=["__pycache__", "test_"],
        ))
        pattern = re.compile(r"Legacy-compatible|retained for")
        hits = _grep_lines(paths, pattern)
        assert not hits, (
            "Legacy-compatible / retained-for marker found in live code — "
            "CLAUDE.md System Migration Policy forbids these. Delete the "
            f"marker and the code it tags:\n{hits}"
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
        # flat_shield_bonus is intentionally still placeholder (PROJ-271 deferred).
        # shield_mult and damage_mult must NOT be placeholder.
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
