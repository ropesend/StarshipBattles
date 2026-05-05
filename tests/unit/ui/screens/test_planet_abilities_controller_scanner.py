"""PROJ-353A audit-R2: characterization tests for ``PlanetAbilitiesController``
scanner + editor-discovery surface.

Codex's PROJ-351A..353 audit
(``AgentCoordination/Scratchpad/Discussion/20260505T034007Z_proj351-353-codex-audit/``)
flagged that PROJ-351A T6.4's data-driven scanner refactor (replacing the
hardcoded ``TOGGLEABLE_ABILITIES`` / ``_ENVIRONMENT_EDITORS`` /
``_ACTIVATABLE_ABILITIES`` lists with registry/data scans) had no direct
tests against ``scan_abilities`` or ``get_available_editors``. Without
direct coverage, a future re-hardcode would not be caught.

This file pins the documented contract:

- ``scan_abilities`` returns one entry per (facility, component, ability)
  triple where the ability data carries an ``activation_time`` field.
- Abilities WITHOUT ``activation_time`` are skipped.
- Non-operational facilities contribute nothing.
- Multiple components with the same ability_name receive ``#1``, ``#2``,
  ... ``instance_label`` suffixes; singletons get an empty label.
- ``get_available_editors`` filters ``ENVIRONMENT_EDITORS`` to the keys
  whose ability appears on the planet's operational facilities.
- Display-name humanization handles CamelCase + override map.

Mode: characterization-only — no production refactors.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

from game.ui.screens.planet_abilities_controller import (
    ABILITY_DISPLAY_NAME_OVERRIDES,
    ENVIRONMENT_EDITORS,
    PlanetAbilitiesController,
    _humanize_ability_name,
)


def _facility(
    instance_id: str,
    name: str,
    components: List[Dict[str, Any]],
    *,
    is_operational: bool = True,
    layer: str = "OUTER",
) -> SimpleNamespace:
    """Build a minimal facility stand-in for scanner tests.

    Components carry inline ``abilities`` dicts so
    ``extract_abilities_from_component`` returns them without a registry.
    """
    return SimpleNamespace(
        instance_id=instance_id,
        name=name,
        is_operational=is_operational,
        design_data={"layers": {layer: components}},
    )


def _planet(facilities: List[Any], populations: List[Any] | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        facilities=facilities,
        populations=populations or [],
    )


# ---------------------------------------------------------------------------
# scan_abilities — data-driven discovery via `activation_time` predicate
# ---------------------------------------------------------------------------


class TestScanAbilitiesDataDrivenDiscovery:

    def test_ability_with_activation_time_is_scanned_as_toggleable(self):
        """The contract: any ability whose data dict carries an
        `activation_time` field counts as toggleable, regardless of name."""
        comp = {"id": "c1", "abilities": {
            "PlanetaryShield": {"activation_time": 5, "value": 100},
        }}
        facility = _facility("fac-1", "Defense Complex", [comp])
        controller = PlanetAbilitiesController(_planet([facility]), facade=None)

        entries = controller.scan_abilities()

        assert len(entries) == 1
        entry = entries[0]
        assert entry["ability_name"] == "PlanetaryShield"
        assert entry["facility_id"] == "fac-1"
        assert entry["facility_name"] == "Defense Complex"
        assert entry["display_name"] == "Planetary Shield"
        assert entry["instance_label"] == ""

    def test_ability_without_activation_time_is_skipped(self):
        """An ability whose data is just ``{"value": ...}`` (no
        ``activation_time``) must NOT appear in the scan output. This
        is the core data-driven contract."""
        comp = {"id": "c1", "abilities": {
            "RadiationShield": {"value": 0.5},  # passive, no activation_time
        }}
        facility = _facility("fac-1", "Atmosphere Plant", [comp])
        controller = PlanetAbilitiesController(_planet([facility]), facade=None)

        entries = controller.scan_abilities()

        assert entries == []

    def test_non_operational_facility_contributes_nothing(self):
        """`is_operational=False` short-circuits the inner scan."""
        comp = {"id": "c1", "abilities": {
            "PlanetaryShield": {"activation_time": 5},
        }}
        facility = _facility(
            "fac-1", "Offline Complex", [comp], is_operational=False
        )
        controller = PlanetAbilitiesController(_planet([facility]), facade=None)

        assert controller.scan_abilities() == []

    def test_multiple_components_with_same_ability_get_instance_labels(self):
        """When two components on the same planet expose the same
        ability_name, entries get `#1` and `#2` instance labels so the
        UI can disambiguate."""
        comp_a = {"id": "shield_a", "abilities": {
            "PlanetaryShield": {"activation_time": 5},
        }}
        comp_b = {"id": "shield_b", "abilities": {
            "PlanetaryShield": {"activation_time": 5},
        }}
        facility = _facility("fac-1", "Twin Shield Complex", [comp_a, comp_b])
        controller = PlanetAbilitiesController(_planet([facility]), facade=None)

        entries = controller.scan_abilities()

        assert len(entries) == 2
        labels = sorted(e["instance_label"] for e in entries)
        assert labels == [" #1", " #2"]
        # Component keys differ even with same ability_name.
        assert entries[0]["component_key"] != entries[1]["component_key"]

    def test_singleton_ability_has_empty_instance_label(self):
        """A unique ability_name on the planet gets an empty instance
        label — instance numbering only kicks in for duplicates."""
        comp = {"id": "c1", "abilities": {
            "PlanetaryShield": {"activation_time": 5},
        }}
        facility = _facility("fac-1", "Defense Complex", [comp])
        controller = PlanetAbilitiesController(_planet([facility]), facade=None)

        entries = controller.scan_abilities()

        assert entries[0]["instance_label"] == ""

    def test_mixed_facilities_yield_one_entry_per_qualifying_component(self):
        """Multiple facilities each contributing one toggleable component
        produce one entry per (facility, component) pair."""
        fac_a = _facility(
            "fac-a", "Shield Tower",
            [{"id": "s1", "abilities": {"PlanetaryShield": {"activation_time": 5}}}],
        )
        fac_b = _facility(
            "fac-b", "Beam Array",
            [{"id": "b1", "abilities": {"PlanetaryBeam": {"activation_time": 3}}}],
        )
        fac_c = _facility(
            "fac-c", "Inert Complex",
            [{"id": "rad", "abilities": {"RadiationShield": {"value": 0.2}}}],
        )
        controller = PlanetAbilitiesController(
            _planet([fac_a, fac_b, fac_c]), facade=None
        )

        entries = controller.scan_abilities()

        ability_names = sorted(e["ability_name"] for e in entries)
        # PlanetaryShield + PlanetaryBeam (toggleable); RadiationShield omitted
        # (no activation_time).
        assert ability_names == ["PlanetaryBeam", "PlanetaryShield"]


# ---------------------------------------------------------------------------
# Display-name humanization
# ---------------------------------------------------------------------------


class TestHumanizeAbilityName:

    def test_camel_case_split_on_uppercase_boundaries(self):
        assert _humanize_ability_name("PlanetaryShield") == "Planetary Shield"
        assert _humanize_ability_name("WarpFieldStabilizer") == "Warp Field Stabilizer"

    def test_override_map_takes_precedence(self):
        """`ShieldProjection` is documented as needing the override
        because `Shield Projection` doesn't match the established UI
        label `Shield Projector`."""
        assert "ShieldProjection" in ABILITY_DISPLAY_NAME_OVERRIDES
        assert _humanize_ability_name("ShieldProjection") == "Shield Projector"


# ---------------------------------------------------------------------------
# get_available_editors — ENVIRONMENT_EDITORS routing
# ---------------------------------------------------------------------------


class TestGetAvailableEditors:

    def test_returns_only_env_editor_keys_present_on_planet(self):
        """`ENVIRONMENT_EDITORS` is a closed UI-routing list: the editor
        button is shown when the planet has a facility component
        carrying the corresponding ability. Other abilities (even
        toggleable ones like `PlanetaryShield`) do NOT produce editor
        rows; that's by design — env editors are a different UI surface."""
        comp_atmosphere = {"id": "atm", "abilities": {
            "AtmosphereModifier": {"value": 0.1},
        }}
        # PlanetaryShield is toggleable but NOT an environment editor.
        comp_shield = {"id": "shield", "abilities": {
            "PlanetaryShield": {"activation_time": 5},
        }}
        facility = _facility("fac-1", "Multi", [comp_atmosphere, comp_shield])
        controller = PlanetAbilitiesController(_planet([facility]), facade=None)

        editors = controller.get_available_editors()

        keys = [k for k, _ in editors]
        assert keys == ["AtmosphereModifier"]
        # Ensure the canonical label is the human-readable env-domain name.
        assert dict(editors)["AtmosphereModifier"] == "Atmosphere"

    def test_returns_all_env_editors_when_all_present(self):
        """All four ENVIRONMENT_EDITORS entries appear in the order they
        are declared in the controller module."""
        comps = [
            {"id": f"c{i}", "abilities": {key: {"value": 0.1}}}
            for i, (key, _label) in enumerate(ENVIRONMENT_EDITORS)
        ]
        facility = _facility("fac-1", "Omni Editor", comps)
        controller = PlanetAbilitiesController(_planet([facility]), facade=None)

        editors = controller.get_available_editors()

        assert editors == ENVIRONMENT_EDITORS

    def test_returns_empty_when_no_env_editor_abilities_present(self):
        """Planet with only non-environment abilities → no editor rows."""
        comp = {"id": "c1", "abilities": {
            "PlanetaryShield": {"activation_time": 5},
        }}
        facility = _facility("fac-1", "Combat-Only", [comp])
        controller = PlanetAbilitiesController(_planet([facility]), facade=None)

        assert controller.get_available_editors() == []

    def test_non_operational_facility_excluded_from_editor_discovery(self):
        """Mirrors the scanner contract — offline facilities don't gate
        editor buttons either."""
        comp = {"id": "atm", "abilities": {
            "AtmosphereModifier": {"value": 0.1},
        }}
        facility = _facility(
            "fac-1", "Offline Atmo", [comp], is_operational=False
        )
        controller = PlanetAbilitiesController(_planet([facility]), facade=None)

        assert controller.get_available_editors() == []


# ---------------------------------------------------------------------------
# should_show_food_editor — orthogonal predicate; pin briefly
# ---------------------------------------------------------------------------


class TestShouldShowFoodEditor:

    def test_returns_true_when_planet_has_populations(self):
        controller = PlanetAbilitiesController(
            _planet([], populations=[SimpleNamespace(species_id="human")]),
            facade=None,
        )
        assert controller.should_show_food_editor() is True

    def test_returns_false_when_no_populations(self):
        controller = PlanetAbilitiesController(_planet([]), facade=None)
        assert controller.should_show_food_editor() is False
