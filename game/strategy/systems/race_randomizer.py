"""
Race Randomizer - Generates random race configuration values.

Provides static methods for randomizing identity fields, visual selections,
and ship themes in the Species Setup dialog. Uses pre-generated race name
data from game/data/race_names.json when a portrait is selected.

FEAT-12: All methods accept an optional `rng: random.Random` parameter
following the per-battle RNG convention documented in
`docs/02_PATTERNS.md` Section 18 (PROJ-252). When `rng is None`, a fresh
`random.Random()` is used so existing callers see identical (unseeded)
behavior.
"""
import random
from typing import Any, Dict, List, Optional

from game.core.json_utils import load_json
from game.core.paths import Paths
from game.strategy.data.environmental_preference import EnvironmentalPreference
from game.strategy.data.habitability_factors import FACTOR_REGISTRY, get_factor
from game.strategy.data.homeworld_presets import (
    apply_preset_to_config,
    load_homeworld_presets,
)
from game.strategy.data.race_config import (
    APTITUDE_NAMES,
    GOVERNMENT_TYPES,
    GOVERNMENT_ORGANIZATIONS,
    LEADER_TITLES,
    PHYSICAL_TYPES,
    RaceConfig,
    SOCIETY_TYPES,
)
from game.strategy.data.race_point_budget import RacePointBudget


def _resolve_rng(rng: Optional[random.Random]) -> random.Random:
    """Return `rng` if given, else a fresh unseeded `random.Random()`."""
    return rng if rng is not None else random.Random()


class RaceRandomizer:
    """Generates random values for race configuration fields."""

    _race_names_cache: Optional[Dict] = None

    @staticmethod
    def _load_race_names() -> Dict:
        """Load and cache the race names data file."""
        if RaceRandomizer._race_names_cache is not None:
            return RaceRandomizer._race_names_cache

        path = Paths.RACE_NAMES_FILE
        data = load_json(path, default={})
        RaceRandomizer._race_names_cache = data
        return data

    @staticmethod
    def randomize_identity(
        portrait_id: Optional[str] = None,
        rng: Optional[random.Random] = None,
    ) -> Dict[str, str]:
        """
        Generate random identity fields for a race.

        Args:
            portrait_id: If provided, use portrait-specific names from data file.
            rng: Optional `random.Random` instance for deterministic output.

        Returns:
            Dict with keys: race_name, race_name_plural, leader_name,
            physical_type, government_type, government_organization,
            leader_title, society_type, faction_name
        """
        rng = _resolve_rng(rng)
        data = RaceRandomizer._load_race_names()

        # Pick name + plural from portrait-specific or fallback pool
        name_entry = RaceRandomizer._pick_name_entry(data, portrait_id, rng)
        race_name = name_entry["name"]
        race_name_plural = name_entry["plural"]

        # Pick leader name from portrait-specific or fallback pool
        leader_name = RaceRandomizer._pick_leader(data, portrait_id, rng)

        # Pick from dropdown lists
        physical_type = rng.choice(PHYSICAL_TYPES)
        government_type = rng.choice(GOVERNMENT_TYPES)
        government_org = rng.choice(GOVERNMENT_ORGANIZATIONS)
        leader_title = rng.choice(LEADER_TITLES)
        society_type = rng.choice(SOCIETY_TYPES)

        # Generate faction name
        faction_name = f"{race_name} {government_type}"

        return {
            "race_name": race_name,
            "race_name_plural": race_name_plural,
            "leader_name": leader_name,
            "physical_type": physical_type,
            "government_type": government_type,
            "government_organization": government_org,
            "leader_title": leader_title,
            "society_type": society_type,
            "faction_name": faction_name,
        }

    @staticmethod
    def _pick_name_entry(
        data: Dict,
        portrait_id: Optional[str],
        rng: random.Random,
    ) -> Dict[str, str]:
        """Pick a name entry (name + plural) from portrait data or fallback."""
        if portrait_id and "portraits" in data:
            portrait_data = data["portraits"].get(portrait_id)
            if portrait_data and portrait_data.get("names"):
                return rng.choice(portrait_data["names"])

        fallback = data.get("fallback_names", [])
        if fallback:
            return rng.choice(fallback)

        return {"name": "Unknown", "plural": "Unknown"}

    @staticmethod
    def _pick_leader(
        data: Dict,
        portrait_id: Optional[str],
        rng: random.Random,
    ) -> str:
        """Pick a leader name from portrait data or fallback."""
        if portrait_id and "portraits" in data:
            portrait_data = data["portraits"].get(portrait_id)
            if portrait_data and portrait_data.get("leaders"):
                return rng.choice(portrait_data["leaders"])

        fallback = data.get("fallback_leaders", [])
        if fallback:
            return rng.choice(fallback)

        return "Leader"

    @staticmethod
    def randomize_flag(
        available_flags: List[str],
        rng: Optional[random.Random] = None,
    ) -> str:
        """Pick a random flag from available flag IDs."""
        if not available_flags:
            return ""
        return _resolve_rng(rng).choice(available_flags)

    @staticmethod
    def randomize_portrait(
        available_portraits: List[str],
        rng: Optional[random.Random] = None,
    ) -> str:
        """Pick a random portrait from available portrait IDs."""
        if not available_portraits:
            return ""
        return _resolve_rng(rng).choice(available_portraits)

    @staticmethod
    def randomize_theme(
        available_themes: List[str],
        rng: Optional[random.Random] = None,
    ) -> str:
        """Pick a random ship theme from available theme IDs."""
        if not available_themes:
            return ""
        return _resolve_rng(rng).choice(available_themes)

    # ------------------------------------------------------------------ #
    # FEAT-12 Sub-task 2: budget-aware aptitude rolling                   #
    # ------------------------------------------------------------------ #

    _APT_HIGH_RANGE = (55, 80)
    _APT_LOW_RANGE = (20, 45)

    @staticmethod
    def randomize_aptitudes(
        budget: int,
        rng: Optional[random.Random] = None,
    ) -> Dict[str, int]:
        """Pick aptitude values that respect the given point budget.

        Shape: 2-3 aptitudes pushed HIGH (55-80), 2-3 pushed LOW (20-45),
        remaining stay at the free baseline (50). If the rolled values
        exceed `budget`, the highest-cost aptitude is reduced one step
        toward 50 until the total cost fits.

        Args:
            budget: Maximum aptitude cost allowed (`RacePointBudget`
                semantics — below 50 refunds linearly, above 50 costs
                exponentially).
            rng: Optional `random.Random` for deterministic output.

        Returns:
            `{aptitude_name: value}` for all 7 paid aptitudes. Caller is
            responsible for writing values into a `RaceConfig`.
        """
        rng = _resolve_rng(rng)
        cost_calc = RacePointBudget()

        names = list(APTITUDE_NAMES)
        rng.shuffle(names)
        n_high = rng.randint(2, 3)
        n_low = rng.randint(2, 3)
        high_names = names[:n_high]
        low_names = names[n_high : n_high + n_low]

        result: Dict[str, int] = {name: 50 for name in APTITUDE_NAMES}
        for name in high_names:
            result[name] = rng.randint(*RaceRandomizer._APT_HIGH_RANGE)
        for name in low_names:
            result[name] = rng.randint(*RaceRandomizer._APT_LOW_RANGE)

        # Rebalance: pull the highest-cost aptitude one step toward 50
        # until total cost fits the budget.
        def total_cost() -> int:
            return sum(cost_calc._single_aptitude_cost(v) for v in result.values())

        while total_cost() > budget:
            # Highest absolute cost above 50 dominates; only those can be reduced.
            candidates = [n for n, v in result.items() if v > 50]
            if not candidates:
                break
            top = max(candidates, key=lambda n: cost_calc._single_aptitude_cost(result[n]))
            result[top] -= 1

        return result

    # ------------------------------------------------------------------ #
    # FEAT-12 Sub-task 3: budget-aware environment randomization          #
    # ------------------------------------------------------------------ #

    _REPRO_MIN = 0.005
    _REPRO_MAX = 0.10
    _SETPOINT_JITTER_STEPS = 3   # ±3 factor.step units around current setpoint
    _TOLERANCE_JITTER_LO = 0.5
    _TOLERANCE_JITTER_HI = 2.0
    _TOLERANCE_CEILING_MULT = 4.0

    @staticmethod
    def randomize_environment(
        budget: int,
        rng: Optional[random.Random] = None,
    ) -> Dict[str, Any]:
        """Randomize environmental preferences within `budget`.

        Algorithm:
            1. Pick a random homeworld preset and apply it to a fresh
               `RaceConfig`. This seeds preferences with biologically
               coherent values for the chosen planet type.
            2. Jitter every factor's setpoint by ±`step * 3`, clamp to
               `[min_value, max_value]`.
            3. Jitter every factor's tolerance by `× uniform(0.5, 2.0)`,
               clamp to `[step, default_tolerance × 4]`.
            4. Roll `base_reproduction_rate` in `[0.005, 0.10]` and
               `base_happiness` in `[0.0, 1.0]`.
            5. If total cost (preferences + reproduction) exceeds budget,
               pull the most-expensive tolerance one step toward
               `default_tolerance` and repeat.

        Args:
            budget: Maximum combined cost for preferences + reproduction
                rate. Setpoints and happiness are free.
            rng: Optional `random.Random` for deterministic output.

        Returns:
            Dict with keys: `preferences` (factor_id -> EnvironmentalPreference),
            `homeworld_type`, `base_reproduction_rate`, `base_happiness`.
        """
        rng = _resolve_rng(rng)
        cost_calc = RacePointBudget()

        # Step 1: seed from a random preset.
        presets = load_homeworld_presets()
        preset_id = rng.choice(list(presets.keys()))
        config = RaceConfig()  # auto-fills FACTOR_REGISTRY defaults
        apply_preset_to_config(presets[preset_id], config)

        # Step 2 + 3: jitter setpoints and tolerances per factor.
        for factor_id, factor in FACTOR_REGISTRY.items():
            current = config.preferences[factor_id]
            jitter_setpoint = current.setpoint + rng.uniform(
                -RaceRandomizer._SETPOINT_JITTER_STEPS * factor.step,
                RaceRandomizer._SETPOINT_JITTER_STEPS * factor.step,
            )
            new_setpoint = max(
                factor.min_value, min(factor.max_value, jitter_setpoint)
            )
            tolerance_mult = rng.uniform(
                RaceRandomizer._TOLERANCE_JITTER_LO,
                RaceRandomizer._TOLERANCE_JITTER_HI,
            )
            tol_ceiling = (
                factor.default_tolerance * RaceRandomizer._TOLERANCE_CEILING_MULT
            )
            tol_floor = factor.step
            new_tolerance = max(
                tol_floor, min(tol_ceiling, current.tolerance * tolerance_mult)
            )
            config.preferences[factor_id] = EnvironmentalPreference(
                setpoint=new_setpoint,
                tolerance=new_tolerance,
                min_value=factor.min_value,
                max_value=factor.max_value,
                step=factor.step,
            )

        # Step 4: roll repro + happiness.
        config.base_reproduction_rate = rng.uniform(
            RaceRandomizer._REPRO_MIN, RaceRandomizer._REPRO_MAX
        )
        config.base_happiness = rng.uniform(0.0, 1.0)

        # Step 5: rebalance preferences toward registry defaults if over budget.
        def env_cost() -> int:
            return cost_calc.calculate_preferences_cost(
                config
            ) + cost_calc.calculate_reproduction_cost(config.base_reproduction_rate)

        # Safety cap on the rebalance loop — every iteration strictly reduces
        # total cost, so this caps a pathological case.
        max_iterations = 17 * 50
        iters = 0
        while env_cost() > budget and iters < max_iterations:
            iters += 1
            # Find factor whose preference deviates most expensively from default.
            most_expensive = max(
                FACTOR_REGISTRY.keys(),
                key=lambda fid: abs(
                    config.preferences[fid].tolerance
                    - get_factor(fid).default_tolerance
                ),
            )
            factor = get_factor(most_expensive)
            current = config.preferences[most_expensive]
            # Pull tolerance one `step` closer to default_tolerance.
            if current.tolerance > factor.default_tolerance:
                new_tol = max(
                    factor.default_tolerance, current.tolerance - factor.step
                )
            elif current.tolerance < factor.default_tolerance:
                new_tol = min(
                    factor.default_tolerance, current.tolerance + factor.step
                )
            else:
                # All tolerances at default — nothing more to rebalance.
                # If still over budget, the reproduction rate is the cause;
                # pull it toward the default 3%.
                if config.base_reproduction_rate > RacePointBudget.REPRO_DEFAULT:
                    config.base_reproduction_rate = max(
                        RacePointBudget.REPRO_DEFAULT,
                        config.base_reproduction_rate - RacePointBudget.REPRO_STEP,
                    )
                else:
                    break
                continue
            config.preferences[most_expensive] = EnvironmentalPreference(
                setpoint=current.setpoint,
                tolerance=max(new_tol, 0.0),
                min_value=factor.min_value,
                max_value=factor.max_value,
                step=factor.step,
            )

        return {
            "preferences": dict(config.preferences),
            "homeworld_type": config.homeworld_type,
            "base_reproduction_rate": config.base_reproduction_rate,
            "base_happiness": config.base_happiness,
        }

    # ------------------------------------------------------------------ #
    # FEAT-12 Sub-task 5: master "Randomize All" orchestrator             #
    # ------------------------------------------------------------------ #

    _MASTER_BUDGET = 100
    _APT_FRACTION_LO = 0.3
    _APT_FRACTION_HI = 0.7

    @staticmethod
    def randomize_all(
        available_flags: List[str],
        available_portraits: List[str],
        available_themes: List[str],
        portrait_id_for_names: Optional[str] = None,
        rng: Optional[random.Random] = None,
    ) -> Dict[str, Any]:
        """Roll a complete race configuration in one call.

        Apportions the 100-point budget between aptitudes and environment
        with a random per-run fraction in `[0.3, 0.7]`, then delegates
        identity/visuals/ships to the existing `randomize_*` methods.

        Args:
            available_flags / available_portraits / available_themes: ID
                pools for visual selection.
            portrait_id_for_names: Optional portrait id passed to
                `randomize_identity` for portrait-aware names. When None,
                the freshly-rolled portrait id is used.
            rng: Optional `random.Random` for deterministic output.

        Returns:
            Dict with all identity/visuals/ships/env/aptitudes fields.
            The screen layer applies these directly to the working
            `RaceConfig`.
        """
        rng = _resolve_rng(rng)

        # Visuals first — chosen portrait may seed identity name picking.
        flag_id = RaceRandomizer.randomize_flag(available_flags, rng=rng)
        portrait_id = RaceRandomizer.randomize_portrait(available_portraits, rng=rng)
        theme_id = RaceRandomizer.randomize_theme(available_themes, rng=rng)

        identity = RaceRandomizer.randomize_identity(
            portrait_id=portrait_id_for_names or portrait_id or None,
            rng=rng,
        )

        # Apportion budget. Roll repro/happiness inside `randomize_environment`,
        # but precompute env_budget = available - apt_budget where available
        # depends on whatever reproduction cost env ends up paying. Since we
        # don't know that yet, give env the larger lump sum and let it
        # rebalance its tolerances if reproduction lands on the expensive side.
        fraction = rng.uniform(
            RaceRandomizer._APT_FRACTION_LO, RaceRandomizer._APT_FRACTION_HI
        )
        apt_budget = round(RaceRandomizer._MASTER_BUDGET * fraction)
        env_budget = RaceRandomizer._MASTER_BUDGET - apt_budget

        aptitudes = RaceRandomizer.randomize_aptitudes(budget=apt_budget, rng=rng)
        env = RaceRandomizer.randomize_environment(budget=env_budget, rng=rng)

        result: Dict[str, Any] = {
            **identity,
            "flag_id": flag_id,
            "portrait_id": portrait_id,
            "theme_id": theme_id,
            "aptitudes": aptitudes,
            **env,
        }
        return result
