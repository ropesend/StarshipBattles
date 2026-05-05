"""Pure helper tests for builder component list items."""
from __future__ import annotations

from types import SimpleNamespace


class FakePanel:
    def __init__(self, *, relative_rect, **_kwargs) -> None:
        self.relative_rect = relative_rect
        self.killed = False

    def get_abs_rect(self):
        return self.relative_rect

    def kill(self) -> None:
        self.killed = True


class FakeButton:
    def __init__(self, **_kwargs) -> None:
        self.selected = False

    def select(self) -> None:
        self.selected = True

    def unselect(self) -> None:
        self.selected = False


class FakeImage:
    def __init__(self, **_kwargs) -> None:
        pass


class CapturingLabel:
    instances: list[CapturingLabel] = []

    def __init__(self, *, text: str, **_kwargs) -> None:
        self.text = text
        self.instances.append(self)


class FakeSpriteManager:
    def get_sprite(self, _sprite_index: int):
        return None


class FakeComponent:
    def __init__(
        self,
        *,
        name: str = "Fusion Core",
        mass: float = 10.0,
        abilities: dict[str, object] | None = None,
        clone_component: object | None = None,
    ) -> None:
        self.name = name
        self.type_str = "utility"
        self.mass = mass
        self.max_hp = 25
        self.sprite_index = 0
        self.data = {"major_classification": "Power"}
        self.abilities = abilities or {}
        self.ability_instances = list(self.abilities.values())
        self.clone_calls = 0
        self._clone_component = clone_component

    def has_ability(self, ability_name: str) -> bool:
        return ability_name in self.abilities

    def get_ability(self, ability_name: str) -> object:
        return self.abilities[ability_name]

    def get_abilities(self, ability_name: str) -> list[object]:
        ability = self.abilities.get(ability_name)
        return [ability] if ability is not None else []

    def clone(self) -> object:
        self.clone_calls += 1
        return self._clone_component


class RecalculatingClone:
    def __init__(self, recalculated_mass: float) -> None:
        self.mass = 0.0
        self.ship = None
        self._recalculated_mass = recalculated_mass
        self.recalculate_calls = 0

    def recalculate_stats(self) -> None:
        self.recalculate_calls += 1
        self.mass = self._recalculated_mass


def _patch_component_item_ui(monkeypatch) -> object:
    from game.ui.screens.builder import components

    CapturingLabel.instances = []
    monkeypatch.setattr(components, "UIPanel", FakePanel)
    monkeypatch.setattr(components, "UIButton", FakeButton)
    monkeypatch.setattr(components, "UILabel", CapturingLabel)
    monkeypatch.setattr(components, "UIImage", FakeImage)
    return components


def test_tooltip_includes_weapon_beam_propulsion_shield_and_unknown_abilities() -> None:
    from game.ui.screens.builder.components import ComponentListItem

    component = FakeComponent(
        name="Mixed Battery",
        abilities={
            "WeaponAbility": SimpleNamespace(damage=12, range=800, reload_time=2.5),
            "BeamWeaponAbility": SimpleNamespace(base_accuracy=0.75),
            "CombatPropulsion": SimpleNamespace(thrust_force=30),
            "ManeuveringThruster": SimpleNamespace(turn_rate=4),
            "ShieldProjection": SimpleNamespace(capacity=90),
            "ColonizePlanet": SimpleNamespace(),
        },
    )

    tooltip = ComponentListItem.__new__(ComponentListItem)._generate_tooltip(component)

    assert "Damage: 12" in tooltip
    assert "Range: 800" in tooltip
    assert "Acc: 75%" in tooltip
    assert "Reload: 2.5s" in tooltip
    assert "Thrust: 30" in tooltip
    assert "Turn: 4/s" in tooltip
    assert "Shield: 90" in tooltip
    assert "- ColonizePlanet" in tooltip


def test_tooltip_uses_resource_generation_for_power_branch() -> None:
    from game.ui.screens.builder.components import ComponentListItem

    component = FakeComponent(
        abilities={"ResourceGeneration": SimpleNamespace(rate=7)}
    )

    tooltip = ComponentListItem.__new__(ComponentListItem)._generate_tooltip(component)

    assert "Power: +7/s" in tooltip


def test_component_item_uses_base_mass_without_ship_context(monkeypatch) -> None:
    components = _patch_component_item_ui(monkeypatch)
    component = FakeComponent(mass=12.5)

    components.ComponentListItem(
        component=component,
        manager=object(),
        container=object(),
        y_pos=0,
        width=200,
        sprite_mgr=FakeSpriteManager(),
        ship_context=None,
    )

    assert component.clone_calls == 0
    assert CapturingLabel.instances[-1].text == "Fusion Core (12.5t)"


def test_component_item_recalculates_clone_mass_with_ship_context(monkeypatch) -> None:
    components = _patch_component_item_ui(monkeypatch)
    ship_context = object()
    clone = RecalculatingClone(recalculated_mass=42.25)
    component = FakeComponent(mass=12.5, clone_component=clone)

    components.ComponentListItem(
        component=component,
        manager=object(),
        container=object(),
        y_pos=0,
        width=200,
        sprite_mgr=FakeSpriteManager(),
        ship_context=ship_context,
    )

    assert component.clone_calls == 1
    assert clone.ship is ship_context
    assert clone.recalculate_calls == 1
    assert CapturingLabel.instances[-1].text == "Fusion Core (42.2t)"
