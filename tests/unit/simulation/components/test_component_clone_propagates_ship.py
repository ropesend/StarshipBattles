"""Component.clone() must propagate the source's ship reference.

Background: ``data/components.json`` contains formulas like
``"=50 * sqrt(ship_class_mass / 1000)"`` (bridge mass, armor mass, warp_drive,
etc.). ``recalculate_stats()`` resolves ``ship_class_mass`` from either an
explicit ``context`` argument or ``component.ship.max_mass_budget``.

Before this change, ``Component.clone()`` returned a detached clone
(``clone.ship is None``) regardless of whether the source was attached to
a ship. Any caller that cloned an attached component and then triggered
formula evaluation on the clone (``recalculate_stats``, ``add_modifier``,
``copy_modifiers``) crashed with ``FormulaException: Undefined variable:
'ship_class_mass'``.

The same trap was being mitigated manually in three call sites
(``workshop_event_router._handle_select_component_type``,
``builder/interaction_controller.py`` shift-drop, and
``workshop_event_router._handle_add_component`` -- the one that crashed
because the manual fix was missed). Propagating ``self.ship`` in
``clone()`` removes the bug class.

Detached clones (cloning a template/palette component with
``ship is None``) remain detached -- the change is only that an attached
source produces an attached clone.
"""
from __future__ import annotations

import pytest

from game.simulation.components.component import create_component
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import load_components
from game.core.registry import get_default_registry_provider
from tests.fixtures.paths import get_data_dir


@pytest.fixture(autouse=True)
def _setup_component_data():
    initialize_ship_data()
    provider = get_default_registry_provider()
    load_components(str(get_data_dir() / "components.json"), registry_provider=provider)
    yield


class TestCloneShipPropagation:
    def test_clone_of_detached_component_remains_detached(self, fresh_registries):
        """Cloning a palette/template component (ship=None) must yield a
        detached clone. Registry loading and palette display rely on this."""
        bridge = create_component("bridge", registries=fresh_registries)
        assert bridge.ship is None

        clone = bridge.clone()

        assert clone.ship is None

    def test_clone_of_attached_component_inherits_ship(self, fresh_registries):
        """An attached source must produce an attached clone so downstream
        ``recalculate_stats()`` calls resolve ``ship_class_mass`` without
        the caller having to remember to set ``.ship`` manually."""
        ship = Ship(
            "TestShip", 0, 0, (255, 255, 255), registries=fresh_registries
        )
        bridge = create_component("bridge", registries=fresh_registries)
        bridge.ship = ship

        clone = bridge.clone()

        assert clone.ship is ship

    def test_clone_of_attached_recalculates_without_explicit_context(
        self, fresh_registries
    ):
        """Recalculating a clone of an attached ``ship_class_mass``-formula
        component must succeed without passing an explicit context.

        This is the exact bug class behind the workshop add-component crash.
        """
        ship = Ship(
            "TestShip", 0, 0, (255, 255, 255), registries=fresh_registries
        )
        ship.max_mass_budget = 2000.0
        bridge = create_component("bridge", registries=fresh_registries)
        bridge.ship = ship

        clone = bridge.clone()

        # Must not raise FormulaException.
        clone.recalculate_stats()

        # Bridge mass formula: 50 * sqrt(ship_class_mass / 1000).
        expected = 50.0 * (2000.0 / 1000.0) ** 0.5
        assert clone.mass == pytest.approx(expected, abs=0.1)

    @pytest.mark.parametrize(
        "comp_id",
        [
            "bridge",
            "emissive_armor",
            "shield_regenerating_armor",
            "scattering_armor",
            "warp_drive",
        ],
    )
    def test_clone_recalculate_for_all_ship_class_mass_components(
        self, fresh_registries, comp_id
    ):
        """Every ship-side component whose mass formula references
        ``ship_class_mass`` must clone+recalc cleanly when the source is
        attached. Covers the full crash surface the user reported (bridge +
        armor variants) plus warp_drive."""
        ship = Ship(
            "TestShip", 0, 0, (255, 255, 255), registries=fresh_registries
        )
        ship.max_mass_budget = 2000.0
        source = create_component(comp_id, registries=fresh_registries)
        source.ship = ship

        clone = source.clone()
        clone.recalculate_stats()

        assert clone.mass > 0
