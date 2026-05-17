"""Regression for QA Observation 3 (2026-05-16) — workshop save must
invalidate the per-turn ``scan_designs`` cache.

Pre-fix, ``WorkshopShipIO.save_ship`` constructed ``DesignLibrary`` without
the ``facade_state`` kwarg, so ``DesignLibrary.save_design`` silently no-op'd
its cache-invalidation step. The Build Queue (which DOES pass
``facade_state``) then served stale data and the newly-saved design never
appeared in Available Designs.

PROJ-434 Phase 2: the workshop now routes through the per-empire
``DesignCatalog`` from ``session.services.design_catalogs_by_empire``.
The catalog's ``save_design`` orchestrates the disk write + invalidates
the in-memory list view so the next read sees the new design without a
turn advance. These tests lock the new contract.
"""
from __future__ import annotations

import os
import tempfile
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.core.registry import GameRegistries
from game.strategy.facade.slices._facade_state import FacadeSessionState
from game.strategy.systems.design_catalog import DesignCatalog
from game.strategy.systems.design_repository import DesignRepository
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode


@pytest.fixture
def mock_registries() -> GameRegistries:
    return GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})


def _wired_facade_state(tmpdir: str, empire_id: int) -> tuple[FacadeSessionState, DesignCatalog]:
    """Build a FacadeSessionState whose session exposes a per-empire
    DesignCatalog under ``services.design_catalogs_by_empire``."""
    repo = DesignRepository(tmpdir, empire_id=empire_id)
    catalog = DesignCatalog(empire_id=empire_id)
    catalog.attach_repository(repo)
    session = MagicMock()
    session.services = SimpleNamespace(
        design_catalogs_by_empire={empire_id: catalog},
    )
    state = FacadeSessionState(session=session)
    return state, catalog


# --------------------------------------------------------------------------
# WorkshopContext exposes facade_state.
# --------------------------------------------------------------------------

def test_integrated_context_accepts_facade_state(
    mock_registries: GameRegistries,
) -> None:
    """``WorkshopContext.integrated`` must accept and store facade_state."""
    state = FacadeSessionState(session=MagicMock())
    ctx = WorkshopContext.integrated(
        empire_id=1,
        savegame_path="saves/test",
        facade_state=state,
        registries=mock_registries,
    )
    assert ctx.facade_state is state


def test_integrated_context_facade_state_defaults_to_none(
    mock_registries: GameRegistries,
) -> None:
    """``facade_state`` is optional — standalone / no-facade paths still work."""
    ctx = WorkshopContext.integrated(
        empire_id=1,
        savegame_path="saves/test",
        registries=mock_registries,
    )
    assert ctx.facade_state is None


def test_standalone_context_has_no_facade_state(
    mock_registries: GameRegistries,
) -> None:
    """Standalone mode never has a facade — ``facade_state`` is None."""
    ctx = WorkshopContext.standalone(registries=mock_registries)
    assert ctx.facade_state is None


# --------------------------------------------------------------------------
# WorkshopShipIO routes through the per-empire DesignCatalog.
# --------------------------------------------------------------------------

def _build_ship_io(ctx: WorkshopContext, viewmodel) -> "object":
    """Construct WorkshopShipIO with minimal stubs for the dependencies it
    doesn't exercise in these tests."""
    from game.ui.screens.workshop_ship_io import WorkshopShipIO

    return WorkshopShipIO(
        context=ctx,
        ui_manager=MagicMock(),
        screen_width=1920,
        screen_height=1080,
        ship_io_adapter=MagicMock(),
        design_loader_adapter=MagicMock(),
        viewmodel=viewmodel,
        weapons_report_panel_ref=lambda: MagicMock(),
        show_error_callback=MagicMock(),
        apply_loaded_ship_callback=MagicMock(),
    )


def test_workshop_save_ship_routes_through_design_catalog(
    mock_registries: GameRegistries,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PROJ-434 Phase 2: ``WorkshopShipIO.save_ship`` (integrated mode) routes
    through ``DesignCatalog.save_design`` so the QA-Obs-3 cache contract is
    served by the same catalog the Build Queue reads from."""
    with tempfile.TemporaryDirectory() as tmpdir:
        state, catalog = _wired_facade_state(tmpdir, empire_id=1)
        ctx = WorkshopContext.integrated(
            empire_id=1,
            savegame_path=tmpdir,
            facade_state=state,
            registries=mock_registries,
        )

        ship = MagicMock()
        ship.name = "Probe Ship"
        ship.ship_class = "Escort"
        ship.vehicle_type = "Ship"
        ship.mass = 1000.0
        ship.theme_id = "Federation"
        ship.layers = {}
        ship.to_dict.return_value = {
            "name": "Probe Ship",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "mass": 1000.0,
            "layers": {},
        }

        viewmodel = MagicMock()
        viewmodel.ship = ship

        # Bypass the tkinter prompt — return a fixed name.
        monkeypatch.setattr(
            "game.ui.screens.workshop_ship_io.prompt_string",
            lambda *a, **kw: "Probe Ship",
        )

        ship_io = _build_ship_io(ctx, viewmodel)
        ship_io.save_ship()

        # The new design must be present on the next catalog read on the
        # SAME turn (QA-Obs-3 contract enforced through DesignCatalog).
        names = {d.name for d in catalog.list_designs()}
        assert "Probe Ship" in names


def test_workshop_load_ship_reads_from_design_catalog(
    mock_registries: GameRegistries,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The load path scans through the same DesignCatalog instance the
    Build Queue uses."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "designs", "empire_1"), exist_ok=True)
        state, catalog = _wired_facade_state(tmpdir, empire_id=1)
        ctx = WorkshopContext.integrated(
            empire_id=1,
            savegame_path=tmpdir,
            facade_state=state,
            registries=mock_registries,
        )

        viewmodel = MagicMock()
        viewmodel.ship = MagicMock()

        import game.ui.screens.workshop_ship_io as ship_io_mod

        # Track the catalog kwarg threaded into DesignSelectorWindow.
        captured: list = []

        def fake_selector(**kw):
            captured.append(kw)
            return MagicMock()

        monkeypatch.setattr(ship_io_mod, "DesignSelectorWindow", fake_selector)

        ship_io = _build_ship_io(ctx, viewmodel)
        ship_io.load_ship()

        assert captured, "load_ship must open DesignSelectorWindow"
        assert captured[0]["design_catalog"] is catalog


def test_workshop_select_target_reads_from_design_catalog(
    mock_registries: GameRegistries,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The target-selector path also reads through DesignCatalog."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "designs", "empire_1"), exist_ok=True)
        state, catalog = _wired_facade_state(tmpdir, empire_id=1)
        ctx = WorkshopContext.integrated(
            empire_id=1,
            savegame_path=tmpdir,
            facade_state=state,
            registries=mock_registries,
        )

        viewmodel = MagicMock()
        viewmodel.ship = MagicMock()

        import game.ui.screens.workshop_ship_io as ship_io_mod

        captured: list = []

        def fake_selector(**kw):
            captured.append(kw)
            return MagicMock()

        monkeypatch.setattr(ship_io_mod, "DesignSelectorWindow", fake_selector)

        ship_io = _build_ship_io(ctx, viewmodel)
        ship_io.select_target()

        assert captured, "select_target must open DesignSelectorWindow"
        assert captured[0]["design_catalog"] is catalog


# --------------------------------------------------------------------------
# Game._create_workshop_context threads the live facade_state in.
# --------------------------------------------------------------------------

def test_create_workshop_context_threads_facade_state_from_scene(
    mock_registries: GameRegistries,
) -> None:
    """``Game._create_workshop_context`` reads ``game_session.facade.facade_state``
    (or equivalent) and stores it on the WorkshopContext.

    This locks the production wiring: pre-fix the live facade was reachable
    via ``StrategyScreen.facade`` but never propagated into the workshop.
    """
    from game.app import Game

    fake_state = FacadeSessionState(session=MagicMock())
    game = Game.__new__(Game)
    game.registries = mock_registries

    empire = SimpleNamespace(
        id=1,
        empire_theme_id="default",
        built_ship_designs=set(),
    )
    # Production wiring: ``strategy_screen_lifecycle.on_design_click`` puts
    # the live facade in ``context_data["facade"]`` alongside empire +
    # game_session.
    facade = SimpleNamespace(facade_state=fake_state)
    game_session = SimpleNamespace(save_path="saves/test")

    result = game._create_workshop_context({
        "empire": empire,
        "game_session": game_session,
        "facade": facade,
    })

    assert result is not None
    assert result.facade_state is fake_state, (
        "Game._create_workshop_context must thread the live facade_state into "
        "WorkshopContext so the catalog routing in WorkshopShipIO resolves "
        "the same catalog instance the Build Queue reads from."
    )
