"""Regression tests for QA Observation 4: mini-weapon resource consumption.

mini_railgun and mini_capital_missile previously had no ResourceConsumption
ability binding, so WeaponFiringSystem.can_afford_activation() always returned
True regardless of ammo state. These tests pin down the data fix.

Source paths referenced:
- Data: data/components.json
- Firing path: game/simulation/combat/weapon_firing_system.py (_fire_weapon)
- Resource gate: game/simulation/components/component_resource_manager.py
  (can_afford_activation)
- Stat readout: game/ui/screens/builder/stat_getters.py (get_dps_duration)
"""

from __future__ import annotations

import json
import os
from typing import Any

import pytest


def _load_components_by_id() -> dict[str, Any]:
    here = os.path.dirname(__file__)
    path = os.path.join(here, "..", "..", "..", "data", "components.json")
    path = os.path.abspath(path)
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    by_id: dict[str, Any] = {}
    for comp in data.get("components", []):
        by_id[comp["id"]] = comp
    return by_id


COMPONENTS_BY_ID = _load_components_by_id()


def _get_resource_consumption(comp: dict[str, Any]) -> list[dict[str, Any]]:
    abilities = comp.get("abilities", {})
    rc = abilities.get("ResourceConsumption", [])
    if isinstance(rc, dict):
        return [rc]
    return list(rc)


class TestMiniRailgunAmmoConsumption:
    """mini_railgun must consume ammo per shot (matches full railgun resource)."""

    def test_mini_railgun_exists(self) -> None:
        assert "mini_railgun" in COMPONENTS_BY_ID

    def test_mini_railgun_has_resource_consumption_binding(self) -> None:
        comp = COMPONENTS_BY_ID["mini_railgun"]
        rc = _get_resource_consumption(comp)
        assert rc, "mini_railgun must declare ResourceConsumption (was empty)"

    def test_mini_railgun_consumes_ammo_half_unit_per_activation(self) -> None:
        comp = COMPONENTS_BY_ID["mini_railgun"]
        rc = _get_resource_consumption(comp)
        activation_entries = [e for e in rc if e.get("trigger") == "activation"]
        assert len(activation_entries) == 1, (
            "mini_railgun should have exactly one activation-triggered "
            f"ResourceConsumption entry, found: {activation_entries}"
        )
        entry = activation_entries[0]
        assert entry.get("resource") == "ammo"
        assert entry.get("amount") == 0.5


class TestMiniCapitalMissileAmmoConsumption:
    """mini_capital_missile must consume ammo per shot (mirrors capital_missile)."""

    def test_mini_capital_missile_exists(self) -> None:
        assert "mini_capital_missile" in COMPONENTS_BY_ID

    def test_full_capital_missile_consumes_ammo(self) -> None:
        """Sanity: the parent variant defines the canonical binding we mirror."""
        comp = COMPONENTS_BY_ID["capital_missile"]
        rc = _get_resource_consumption(comp)
        ammo_entries = [
            e for e in rc
            if e.get("resource") == "ammo" and e.get("trigger") == "activation"
        ]
        assert ammo_entries, (
            "capital_missile is expected to declare an ammo activation cost; "
            "if this changes, revisit the mini variant's binding too."
        )

    def test_mini_capital_missile_has_resource_consumption_binding(self) -> None:
        comp = COMPONENTS_BY_ID["mini_capital_missile"]
        rc = _get_resource_consumption(comp)
        assert rc, "mini_capital_missile must declare ResourceConsumption"

    def test_mini_capital_missile_consumes_ammo_half_of_parent(self) -> None:
        parent = COMPONENTS_BY_ID["capital_missile"]
        parent_rc = _get_resource_consumption(parent)
        parent_ammo = next(
            e for e in parent_rc
            if e.get("resource") == "ammo" and e.get("trigger") == "activation"
        )
        parent_amount = parent_ammo["amount"]

        mini = COMPONENTS_BY_ID["mini_capital_missile"]
        mini_rc = _get_resource_consumption(mini)
        activation_entries = [e for e in mini_rc if e.get("trigger") == "activation"]
        assert len(activation_entries) == 1
        entry = activation_entries[0]
        assert entry.get("resource") == "ammo"
        # Mini fighters carry rounds at half the parent shot cost.
        assert entry.get("amount") == pytest.approx(parent_amount * 0.5)


class TestFullRailgunUnchanged:
    """Defensive: the full railgun's existing binding must not regress."""

    def test_full_railgun_still_consumes_one_ammo_per_shot(self) -> None:
        comp = COMPONENTS_BY_ID["railgun"]
        rc = _get_resource_consumption(comp)
        activation_entries = [e for e in rc if e.get("trigger") == "activation"]
        assert len(activation_entries) == 1
        entry = activation_entries[0]
        assert entry.get("resource") == "ammo"
        assert entry.get("amount") == 1
