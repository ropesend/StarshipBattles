"""Direct unit tests for ``DefaultRaceSetupDelegateFactory`` (PROJ-321..328 audit S4.7).

Pins the production delegate types so a future refactor that swaps a
delegate class without updating the factory gets caught by a focused unit
test, not by a downstream integration failure.

The screen-level tests (test_race_setup_screen.py) exercise the factory
indirectly via screen construction, but they typically use a Mock screen
with bypass_init so swapping a delegate type silently still passes there.
This file exercises the factory against a minimal real-shape screen stub
and asserts the bundle composition.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from game.ui.screens.race_setup.controller import RaceSetupController
from game.ui.screens.race_setup.delegate_factory import (
    DefaultRaceSetupDelegateFactory,
    RaceSetupDelegates,
)
from game.ui.screens.race_setup.input_handler import RaceSetupInputHandler
from game.ui.screens.race_setup.llm_dialog_service import LLMDialogService
from game.ui.screens.race_setup.renderer import RaceSetupRenderer
from game.ui.screens.race_setup.view_model import RaceSetupViewModel


def _stub_screen() -> MagicMock:
    """Build the minimal screen shape ``DefaultRaceSetupDelegateFactory``
    reads. The factory only touches: is_editing, race_config, race_library,
    race_registry, on_complete_callback, on_cancel_callback."""
    screen = MagicMock(name="screen")
    screen.is_editing = False
    screen.race_config = MagicMock(name="race_config")
    screen.race_library = MagicMock(name="race_library")
    screen.race_registry = MagicMock(name="race_registry")
    screen.on_complete_callback = MagicMock(name="on_complete_callback")
    screen.on_cancel_callback = MagicMock(name="on_cancel_callback")
    return screen


def test_factory_returns_race_setup_delegates_bundle():
    bundle = DefaultRaceSetupDelegateFactory().build(_stub_screen())
    assert isinstance(bundle, RaceSetupDelegates)


def test_factory_produces_production_delegate_types():
    """Each delegate slot is the real production class, not a Mock or a
    subclass. Pre-PROJ-325, this wiring lived inline in
    ``RaceSetupScreen.__init__``; the parity test guards against the
    factory drifting from that inline shape."""
    bundle = DefaultRaceSetupDelegateFactory().build(_stub_screen())

    assert isinstance(bundle.view_model, RaceSetupViewModel)
    assert isinstance(bundle.renderer, RaceSetupRenderer)
    assert isinstance(bundle.controller, RaceSetupController)
    assert isinstance(bundle.input_handler, RaceSetupInputHandler)
    assert isinstance(bundle.llm_service, LLMDialogService)


def test_factory_view_model_honours_screen_is_editing():
    """The view model is constructed with the screen's is_editing flag —
    pinned because changing the constructor signature would silently
    drop this wiring."""
    screen_new = _stub_screen()
    screen_new.is_editing = False
    screen_edit = _stub_screen()
    screen_edit.is_editing = True

    bundle_new = DefaultRaceSetupDelegateFactory().build(screen_new)
    bundle_edit = DefaultRaceSetupDelegateFactory().build(screen_edit)

    assert bundle_new.view_model.is_editing is False
    assert bundle_edit.view_model.is_editing is True


def test_factory_controller_wires_screen_callbacks():
    """The controller receives the screen's on_complete_callback +
    on_cancel_callback. Pinned so a refactor that drops a callback wiring
    is caught here rather than discovered when a button stops working."""
    screen = _stub_screen()
    bundle = DefaultRaceSetupDelegateFactory().build(screen)

    assert bundle.controller.on_complete_callback is screen.on_complete_callback
    assert bundle.controller.on_cancel_callback is screen.on_cancel_callback


def test_factory_llm_service_shares_view_model_and_renderer_instances():
    """LLMDialogService must reference the *same* view_model + renderer
    instances the controller does, otherwise updates from the LLM dialog
    don't propagate to the screen state. Pinned identity equality."""
    bundle = DefaultRaceSetupDelegateFactory().build(_stub_screen())

    assert bundle.llm_service._vm is bundle.view_model
    assert bundle.llm_service._renderer is bundle.renderer
