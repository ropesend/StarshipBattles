"""Regression for QA Observation 3 (2026-05-16) — workshop save must
invalidate the per-turn ``scan_designs`` cache.

Pre-fix, ``WorkshopShipIO.save_ship`` constructed ``DesignLibrary`` without
the ``facade_state`` kwarg, so ``DesignLibrary.save_design`` silently no-op'd
its cache-invalidation step. The Build Queue (which DOES pass
``facade_state``) then served stale data and the newly-saved design never
appeared in Available Designs.

Fix: ``WorkshopContext`` carries an optional ``facade_state`` reference;
``Game._create_workshop_context`` threads ``screen.facade.facade_state``
into it; ``WorkshopShipIO`` forwards it to every ``DesignLibrary(...)``
construction. These tests lock the contract going forward.
"""
from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock

import pytest

from game.core.registry import GameRegistries
from game.strategy.facade.slices._facade_state import FacadeSessionState
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode


@pytest.fixture
def mock_registries() -> GameRegistries:
    return GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})


@pytest.fixture
def fake_state() -> FacadeSessionState:
    return FacadeSessionState(session=MagicMock())


# --------------------------------------------------------------------------
# WorkshopContext exposes facade_state.
# --------------------------------------------------------------------------

def test_integrated_context_accepts_facade_state(
    mock_registries: GameRegistries, fake_state: FacadeSessionState
) -> None:
    """``WorkshopContext.integrated`` must accept and store facade_state."""
    ctx = WorkshopContext.integrated(
        empire_id=1,
        savegame_path="saves/test",
        facade_state=fake_state,
        registries=mock_registries,
    )
    assert ctx.facade_state is fake_state


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
# WorkshopShipIO threads facade_state into every DesignLibrary construction.
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


def test_workshop_save_ship_constructs_design_library_with_facade_state(
    mock_registries: GameRegistries,
    fake_state: FacadeSessionState,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``WorkshopShipIO.save_ship`` (integrated mode) must construct
    ``DesignLibrary`` with the context's facade_state.

    This is the QA Obs 3 contract test: without facade_state, cache
    invalidation silently no-op's and the build queue serves stale data.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        ctx = WorkshopContext.integrated(
            empire_id=1,
            savegame_path=tmpdir,
            facade_state=fake_state,
            registries=mock_registries,
        )
        assert ctx.mode == WorkshopMode.INTEGRATED

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

        # Capture every DesignLibrary construction.
        constructed: list = []
        import game.ui.screens.workshop_ship_io as ship_io_mod

        real_cls = ship_io_mod.DesignLibrary

        def capturing_ctor(*args, **kwargs):
            inst = real_cls(*args, **kwargs)
            constructed.append(inst)
            return inst

        monkeypatch.setattr(ship_io_mod, "DesignLibrary", capturing_ctor)

        ship_io = _build_ship_io(ctx, viewmodel)
        ship_io.save_ship()

        assert constructed, "save_ship must construct a DesignLibrary"
        for lib in constructed:
            assert lib._facade_state is fake_state, (
                "WorkshopShipIO must pass context.facade_state into "
                "DesignLibrary so save_design invalidates the per-turn cache."
            )

        # Cache invalidation effect: empire 1 entry must NOT survive the save.
        # (No entry was seeded — but the pop is a no-op-safe contract.)
        assert 1 not in fake_state.designs_by_empire


def test_workshop_load_ship_constructs_design_library_with_facade_state(
    mock_registries: GameRegistries,
    fake_state: FacadeSessionState,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The load path also threads facade_state so a load right after a save
    in the same turn reads from the same cache space."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "designs", "empire_1"), exist_ok=True)
        ctx = WorkshopContext.integrated(
            empire_id=1,
            savegame_path=tmpdir,
            facade_state=fake_state,
            registries=mock_registries,
        )

        viewmodel = MagicMock()
        viewmodel.ship = MagicMock()

        constructed: list = []
        import game.ui.screens.workshop_ship_io as ship_io_mod

        real_cls = ship_io_mod.DesignLibrary

        def capturing_ctor(*args, **kwargs):
            inst = real_cls(*args, **kwargs)
            constructed.append(inst)
            return inst

        monkeypatch.setattr(ship_io_mod, "DesignLibrary", capturing_ctor)
        # Stub out DesignSelectorWindow — we only care about construction.
        monkeypatch.setattr(
            ship_io_mod, "DesignSelectorWindow", lambda **kw: MagicMock()
        )

        ship_io = _build_ship_io(ctx, viewmodel)
        ship_io.load_ship()

        assert constructed, "load_ship must construct a DesignLibrary"
        for lib in constructed:
            assert lib._facade_state is fake_state


def test_workshop_select_target_constructs_design_library_with_facade_state(
    mock_registries: GameRegistries,
    fake_state: FacadeSessionState,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The target-selector path also threads facade_state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "designs", "empire_1"), exist_ok=True)
        ctx = WorkshopContext.integrated(
            empire_id=1,
            savegame_path=tmpdir,
            facade_state=fake_state,
            registries=mock_registries,
        )

        viewmodel = MagicMock()
        viewmodel.ship = MagicMock()

        constructed: list = []
        import game.ui.screens.workshop_ship_io as ship_io_mod

        real_cls = ship_io_mod.DesignLibrary

        def capturing_ctor(*args, **kwargs):
            inst = real_cls(*args, **kwargs)
            constructed.append(inst)
            return inst

        monkeypatch.setattr(ship_io_mod, "DesignLibrary", capturing_ctor)
        monkeypatch.setattr(
            ship_io_mod, "DesignSelectorWindow", lambda **kw: MagicMock()
        )

        ship_io = _build_ship_io(ctx, viewmodel)
        ship_io.select_target()

        assert constructed, "select_target must construct a DesignLibrary"
        for lib in constructed:
            assert lib._facade_state is fake_state


# --------------------------------------------------------------------------
# Game._create_workshop_context threads the live facade_state in.
# --------------------------------------------------------------------------

def test_create_workshop_context_threads_facade_state_from_scene(
    mock_registries: GameRegistries, fake_state: FacadeSessionState
) -> None:
    """``Game._create_workshop_context`` reads ``game_session.facade.facade_state``
    (or equivalent) and stores it on the WorkshopContext.

    This locks the production wiring: pre-fix the live facade was reachable
    via ``StrategyScreen.facade`` but never propagated into the workshop.
    """
    from types import SimpleNamespace
    from game.app import Game

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
        "WorkshopContext so the workshop's DesignLibrary save invalidates the "
        "per-turn cache (QA Obs 3 regression)."
    )
