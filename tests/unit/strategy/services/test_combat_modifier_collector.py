"""Tests for CombatModifierCollector — strategic-to-combat modifier resolution."""
import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from game.strategy.services.combat_modifier_collector import (
    FleetCombatModifiers,
    collect_combat_modifiers,
    _find_empire,
    _find_reference_planet,
)


@dataclass
class MockFacility:
    design_data: Dict[str, Any] = field(default_factory=dict)
    is_operational: bool = True
    component_states: Dict[str, Any] = field(default_factory=dict)

    def get_activation_state(self, comp_key: str):
        from game.strategy.data.component_activation_state import ComponentActivationState
        data = self.component_states.get(comp_key)
        if data is None:
            return ComponentActivationState()
        if isinstance(data, ComponentActivationState):
            return data
        return ComponentActivationState.from_dict(data)


@dataclass
class MockPlanet:
    name: str = "Test"
    id: int = 1
    owner_id: int = 0
    facilities: List = field(default_factory=list)


@dataclass
class MockFleet:
    id: int = 1
    owner_id: int = 0
    location: Any = None
    ships: List = field(default_factory=list)


@dataclass
class MockEmpire:
    id: int = 0
    colonies: List = field(default_factory=list)


@dataclass
class MockSystem:
    planets: List = field(default_factory=list)


@dataclass
class MockGalaxy:
    _systems: Dict = field(default_factory=dict)
    _planets_by_hex: Dict = field(default_factory=dict)

    def get_system_at_hex(self, hex_coord):
        return self._systems.get(str(hex_coord))

    def get_planets_at_global_hex(self, hex_coord):
        return self._planets_by_hex.get(str(hex_coord), [])

    def get_planet_global_hex(self, planet):
        return "hex_0"

    def get_system_of_planet(self, planet):
        return self._systems.get("default")


def _facility_with_ability(ability_name, data, active=True):
    """Create a facility with a specific ability on a component.

    Args:
        ability_name: Ability registry key.
        data: Ability data dict.
        active: If True, set the component as ACTIVE in component_states.
    """
    from game.strategy.data.component_activation_state import (
        ComponentActivationState, ActivationPhase,
    )
    comp_key = "CORE:0:test_comp"
    component_states = {}
    if active:
        component_states[comp_key] = ComponentActivationState(
            phase=ActivationPhase.ACTIVE,
            ability_name=ability_name,
            energy_drain_rate=data.get('energy_drain_rate', 0.0) if isinstance(data, dict) else 0.0,
        )
    return MockFacility(
        design_data={
            "layers": {"CORE": [
                {"id": "test_comp", "abilities": {ability_name: data}}
            ]}
        },
        component_states=component_states,
    )


class TestFleetCombatModifiers:
    """Tests for the FleetCombatModifiers dataclass."""

    def test_defaults(self):
        mods = FleetCombatModifiers()
        assert mods.shield_mult == 1.0
        assert mods.damage_mult == 1.0
        assert mods.flat_shield_bonus == 0.0

    def test_no_effect_when_defaults(self):
        """Default modifiers should have no combat effect."""
        mods = FleetCombatModifiers()
        assert mods.shield_mult == 1.0
        assert mods.damage_mult == 1.0


class TestCollectCombatModifiers:
    """Tests for collect_combat_modifiers()."""

    def test_no_facilities_returns_defaults(self):
        """No facilities at battle location = default modifiers."""
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        galaxy = MockGalaxy()
        empires = [MockEmpire(id=0), MockEmpire(id=1)]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.shield_mult == pytest.approx(1.0)
        assert result.damage_mult == pytest.approx(1.0)
        assert result.flat_shield_bonus == pytest.approx(0.0)

    def test_allied_shield_booster_applies_to_fleet(self):
        """Allied shield booster on a planet should boost the fleet's shields."""
        booster_facility = _facility_with_ability("ShieldModifier", {
            "multiplier": 1.25,
            "scope": "allied_system",
            "stack_group": "shield_boost_sys"
        })
        planet = MockPlanet(owner_id=0, facilities=[booster_facility])
        system = MockSystem(planets=[planet])
        galaxy = MockGalaxy(
            _systems={"default": system},
            _planets_by_hex={"hex_0": [planet]}
        )
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        emp0 = MockEmpire(id=0, colonies=[planet])
        empires = [emp0, MockEmpire(id=1)]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.shield_mult == pytest.approx(1.25)

    def test_enemy_shield_suppressor_applies_to_fleet(self):
        """Enemy shield suppressor should reduce the fleet's shields."""
        suppressor_facility = _facility_with_ability("ShieldModifier", {
            "multiplier": 0.75,
            "scope": "enemy_system",
            "stack_group": "shield_suppress_sys"
        })
        # Suppressor is owned by empire 1, enemies of fleet owner (empire 0)
        enemy_planet = MockPlanet(owner_id=1, facilities=[suppressor_facility])
        # Need a planet at the hex for reference, and the enemy planet in the system
        ref_planet = MockPlanet(owner_id=0)
        system = MockSystem(planets=[ref_planet, enemy_planet])
        galaxy = MockGalaxy(
            _systems={"default": system},
            _planets_by_hex={"hex_0": [ref_planet]}
        )
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        emp1 = MockEmpire(id=1, colonies=[enemy_planet])
        empires = [MockEmpire(id=0, colonies=[ref_planet]), emp1]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.shield_mult == pytest.approx(0.75)

    def test_flat_shield_projection_sums(self):
        """Scoped ShieldProjection should add flat shield points."""
        projector_facility = _facility_with_ability("ShieldProjection", {
            "value": 50,
            "scope": "allied_system"
        })
        planet = MockPlanet(owner_id=0, facilities=[projector_facility])
        system = MockSystem(planets=[planet])
        galaxy = MockGalaxy(
            _systems={"default": system},
            _planets_by_hex={"hex_0": [planet]}
        )
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        emp0 = MockEmpire(id=0, colonies=[planet])
        empires = [emp0, MockEmpire(id=1)]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.flat_shield_bonus == pytest.approx(50.0)

    def test_damage_modifier_applies(self):
        """Damage booster should modify the fleet's damage output."""
        booster = _facility_with_ability("DamageModifier", {
            "multiplier": 1.25,
            "scope": "allied_system",
            "stack_group": "damage_boost_sys"
        })
        planet = MockPlanet(owner_id=0, facilities=[booster])
        system = MockSystem(planets=[planet])
        galaxy = MockGalaxy(
            _systems={"default": system},
            _planets_by_hex={"hex_0": [planet]}
        )
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        emp0 = MockEmpire(id=0, colonies=[planet])
        empires = [emp0, MockEmpire(id=1)]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.damage_mult == pytest.approx(1.25)

    def test_scope_none_uses_ability_default_scope(self):
        """Ability entries with scope=None should use the class default scope."""
        booster = _facility_with_ability("DamageModifier", {
            "multiplier": 1.25,
            "scope": None,
            "stack_group": "damage_default_scope"
        })
        planet = MockPlanet(owner_id=0, facilities=[booster])
        system = MockSystem(planets=[planet])
        galaxy = MockGalaxy(
            _systems={"default": system},
            _planets_by_hex={"hex_0": [planet]}
        )
        fleet = MockFleet(location="hex_0", owner_id=0)
        opponent = MockFleet(location="hex_0", owner_id=1)
        empires = [MockEmpire(id=0, colonies=[planet]), MockEmpire(id=1)]

        result = collect_combat_modifiers(fleet, opponent, galaxy, empires, None)

        assert result.damage_mult == pytest.approx(1.25)


class TestLookupHelpers:
    """Tests for collector lookup helper edge cases."""

    def test_find_reference_planet_returns_none_without_galaxy(self):
        assert _find_reference_planet("hex_0", None, []) is None

    def test_find_empire_returns_none_when_id_does_not_match(self):
        empires = [MockEmpire(id=0), MockEmpire(id=1)]

        assert _find_empire(99, empires) is None


# ---------------------------------------------------------------------------
# PROJ-429 Phase 5 — registry-driven combat-modifier name sets.
# ---------------------------------------------------------------------------


class TestCombatModifierAbilityNamesFromRegistry:
    """The combat-modifier ability names are read from the unified
    ``AbilityMetadataRegistry`` rather than re-encoded in literal sets at
    each call site.

    Two distinct categorisations are tested:

    * ``StrategicKind.COMBAT_MODIFIER`` — multiplier-aggregated combat
      modifiers consumed by ``StrategyModifierStackBuilder``'s
      ``entries_from_sector_effects`` filter (includes ThrustModifier).
    * ``StrategicKind.COMBAT_FLAT_BONUS`` — flat-additive combat
      modifiers (``ShieldProjection``).

    The collector's per-fleet aggregation path is a STRICT SUBSET of
    COMBAT_MODIFIER (shield + damage only); a separate test checks the
    collector iterates exactly those two names.
    """

    def test_spec_builder_combat_modifier_set_matches_registry(self) -> None:
        from game.strategy.services.ability_metadata import (
            StrategicKind,
            abilities_with_kind_tag,
        )

        # The set the strategy-side sector-effects filter should iterate.
        expected = frozenset({"ShieldModifier", "DamageModifier", "ThrustModifier"})
        assert abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER) == expected

    def test_shield_projection_is_flat_bonus_not_modifier(self) -> None:
        from game.strategy.services.ability_metadata import (
            StrategicKind,
            ability_has_kind_tag,
        )

        assert ability_has_kind_tag("ShieldProjection", StrategicKind.COMBAT_FLAT_BONUS)
        assert not ability_has_kind_tag("ShieldProjection", StrategicKind.COMBAT_MODIFIER)

    def test_collector_uses_registry_for_combat_flat_bonus_resolution(self) -> None:
        """The collector must consult the unified
        ``AbilityMetadataRegistry`` for combat-flat-bonus resolution
        (i.e. import ``abilities_with_kind_tag``).

        Design note: the collector retains its per-accumulator dispatch
        for shield / damage multipliers (which is structural to
        ``FleetCombatModifiers``'s three fields). The structural change
        is that COMBAT_FLAT_BONUS membership is registry-driven, which
        eliminates the cross-file ``"ShieldProjection"`` literal drift
        between collector and stack builder.
        """
        # Existence: registry knows ShieldProjection as a FLAT_BONUS.
        from game.strategy.services.ability_metadata import (
            StrategicKind,
            abilities_with_kind_tag,
        )

        assert "ShieldProjection" in abilities_with_kind_tag(
            StrategicKind.COMBAT_FLAT_BONUS
        )

        # AST: the collector module imports the registry helper.
        import ast
        from pathlib import Path

        from game.strategy.services import combat_modifier_collector as mod

        source = Path(mod.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)

        uses_kind_helper = any(
            isinstance(n, ast.ImportFrom)
            and n.module == "game.strategy.services.ability_metadata"
            and any(a.name == "abilities_with_kind_tag" for a in n.names)
            for n in ast.walk(tree)
        )
        assert uses_kind_helper, (
            "combat_modifier_collector.py must import "
            "abilities_with_kind_tag from "
            "game.strategy.services.ability_metadata so the "
            "ShieldProjection / COMBAT_FLAT_BONUS resolution goes "
            "through the registry."
        )

    def test_stack_builder_module_does_not_hardcode_combat_ability_literals(self) -> None:
        """``strategy_modifier_stack_builder.py`` similarly must not
        hardcode the COMBAT_MODIFIER name set in
        ``entries_from_sector_effects``. The literal-emission lines that
        produce ModifierEntry instances (ShieldModifier / DamageModifier
        / ShieldProjection per fleet team) are PRESERVED — they emit
        named entries by design and there is one branch per name. The
        AST check therefore inspects the function body of
        ``entries_from_sector_effects`` specifically.
        """
        import ast
        from pathlib import Path

        from game.strategy.combat import strategy_modifier_stack_builder as mod

        source = Path(mod.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)

        target_func: ast.FunctionDef | None = None
        for class_node in tree.body:
            if not isinstance(class_node, ast.ClassDef):
                continue
            for item in class_node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "entries_from_sector_effects":
                    target_func = item
                    break
            if target_func is not None:
                break

        assert target_func is not None, (
            "entries_from_sector_effects not found in strategy_modifier_stack_builder.py"
        )

        # The filter set inside this function must NOT be a literal
        # frozenset/set of {"ShieldModifier","DamageModifier","ThrustModifier"}.
        for node in ast.walk(target_func):
            if isinstance(node, (ast.Set, ast.SetComp)):
                # ast.Set has .elts; ast.SetComp doesn't include literal members
                if isinstance(node, ast.Set):
                    string_members = {
                        e.value
                        for e in node.elts
                        if isinstance(e, ast.Constant) and isinstance(e.value, str)
                    }
                    if string_members & {"ShieldModifier", "DamageModifier", "ThrustModifier"}:
                        raise AssertionError(
                            f"entries_from_sector_effects contains a literal "
                            f"set with combat-modifier names {sorted(string_members)} — "
                            f"route through abilities_with_kind_tag(...) instead."
                        )
