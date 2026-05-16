"""Data regression tests for the Maintenance abstraction (QA Observation 5).

Pins down the data shape changes in `data/components.json`:

- ``crew_quarters`` declares both ``CrewCapacity`` and ``ProvidesMaintenance``.
- ``fighter_cockpit`` declares ``ProvidesMaintenance``.
- ``robotic_drone_crew`` declares ``ProvidesMaintenance`` and lists ``Satellite``
  in allowed_vehicle_types.
- New ``automated_maintenance_unit_{small,medium,large}`` components exist and
  provide maintenance + consume energy.
- No component still uses the legacy ``CrewRequired`` ability key.
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
    for entry in data.get("components", []):
        by_id[entry["id"]] = entry
    return by_id


@pytest.fixture(scope="module")
def components() -> dict[str, Any]:
    return _load_components_by_id()


class TestProviderComponents:
    def test_crew_quarters_provides_maintenance(self, components) -> None:
        cq = components["crew_quarters"]
        ab = cq["abilities"]
        assert "CrewCapacity" in ab
        assert "ProvidesMaintenance" in ab
        # Maintenance provided should match crew capacity (1:1 per design).
        assert ab["ProvidesMaintenance"] == ab["CrewCapacity"]

    def test_fighter_cockpit_provides_maintenance(self, components) -> None:
        fc = components["fighter_cockpit"]
        ab = fc["abilities"]
        assert "ProvidesMaintenance" in ab
        assert ab["ProvidesMaintenance"] == ab["CrewCapacity"]

    def test_robotic_drone_crew_provides_maintenance(self, components) -> None:
        rdc = components["robotic_drone_crew"]
        ab = rdc["abilities"]
        assert "ProvidesMaintenance" in ab
        assert ab["ProvidesMaintenance"] == ab["CrewCapacity"]

    def test_robotic_drone_crew_allowed_on_satellites(self, components) -> None:
        rdc = components["robotic_drone_crew"]
        assert "Satellite" in rdc["allowed_vehicle_types"]


class TestAutomatedMaintenanceUnits:
    @pytest.mark.parametrize("comp_id", [
        "automated_maintenance_unit_small",
        "automated_maintenance_unit_medium",
        "automated_maintenance_unit_large",
    ])
    def test_unit_exists(self, components, comp_id) -> None:
        assert comp_id in components, f"{comp_id} should be defined in data/components.json"

    @pytest.mark.parametrize("comp_id,allowed", [
        ("automated_maintenance_unit_small", {"Ship", "Satellite", "Planetary Complex"}),
        ("automated_maintenance_unit_medium", {"Ship", "Satellite", "Planetary Complex"}),
        ("automated_maintenance_unit_large", {"Ship", "Satellite", "Planetary Complex"}),
    ])
    def test_unit_allowed_vehicle_types(self, components, comp_id, allowed) -> None:
        c = components[comp_id]
        for vehicle_type in allowed:
            assert vehicle_type in c["allowed_vehicle_types"], \
                f"{comp_id} should allow {vehicle_type}"

    def test_units_provide_maintenance_in_ascending_order(self, components) -> None:
        small = components["automated_maintenance_unit_small"]["abilities"]["ProvidesMaintenance"]
        medium = components["automated_maintenance_unit_medium"]["abilities"]["ProvidesMaintenance"]
        large = components["automated_maintenance_unit_large"]["abilities"]["ProvidesMaintenance"]
        assert small < medium < large

    def test_units_have_ascending_mass(self, components) -> None:
        small = components["automated_maintenance_unit_small"]["mass"]
        medium = components["automated_maintenance_unit_medium"]["mass"]
        large = components["automated_maintenance_unit_large"]["mass"]
        assert small < medium < large

    def test_units_consume_energy(self, components) -> None:
        for comp_id in (
            "automated_maintenance_unit_small",
            "automated_maintenance_unit_medium",
            "automated_maintenance_unit_large",
        ):
            ab = components[comp_id]["abilities"]
            assert "ResourceConsumption" in ab, f"{comp_id} should consume energy"
            # ResourceConsumption may be a list or dict; check resource is energy.
            rc = ab["ResourceConsumption"]
            if isinstance(rc, list):
                resources = {entry.get("resource") for entry in rc if isinstance(entry, dict)}
            elif isinstance(rc, dict):
                resources = {rc.get("resource")}
            else:
                resources = set()
            assert "energy" in resources, f"{comp_id} should consume energy"


class TestCrewRequiredRenamedAway:
    """No component in shipped data should reference the legacy CrewRequired ability."""

    def test_no_component_uses_legacy_crew_required_key(self, components) -> None:
        offenders: list[str] = []
        for comp_id, entry in components.items():
            ab = entry.get("abilities") or {}
            if "CrewRequired" in ab:
                offenders.append(comp_id)
        assert not offenders, (
            f"These components still use the legacy 'CrewRequired' ability key; "
            f"rename to 'RequiresMaintenance': {offenders}"
        )

    def test_no_component_uses_unknown_legacy_keys(self, components) -> None:
        # Belt-and-braces: ensure RequiresMaintenance shows up somewhere.
        has_any = False
        for entry in components.values():
            ab = entry.get("abilities") or {}
            if "RequiresMaintenance" in ab:
                has_any = True
                break
        assert has_any, "At least one component should declare RequiresMaintenance"
