"""Shared factory for constructing pygame_gui-derived UI widgets in tests.

PROJ-322 Task 5.0 (APC-001 cluster remediation).

Replacement for the inline ``__new__`` bypass-init pattern that the APC-001
finding flagged across ~16 UI test files. Those tests call
``Cls.__new__(Cls)`` and then manually wire ~50 attributes per test, because
the real ``__init__`` calls ``_create_content`` (or similar) which builds
real ``pygame_gui.elements.UI*`` widgets.

The bypass-init pattern is brittle:

* Every test re-implements per-attribute wiring; missing one yields
  ``AttributeError`` deep in the production code instead of a clear
  signal that the test is incomplete.
* Adding a new UI element to the production class silently breaks tests
  in unrelated files because they never re-ran ``__init__``.
* It tests an instance the production code can never produce.

This module exposes ``make_ui_widget(Cls, **kwargs)`` which:

* Patches every ``pygame_gui.elements.UI*`` class with a ``MagicMock`` for
  the duration of the constructor call. Heavy ``_create_content`` runs but
  every ``pygame_gui`` widget it builds is a Mock, so the cost is bounded.
* Supplies sensible default ``panel``/``manager``/``container`` mocks for
  the most common signatures, while letting callers override any of them.
* Calls the real ``__init__`` so ``self.panel``/``self.ui_manager``/etc.
  end up assigned the way production code expects.

Required vs optional kwargs
---------------------------

The factory introspects the target class's ``__init__`` signature, supplies
defaults for any positional-or-keyword parameter it knows about, and then
applies the caller's overrides on top. Any parameter the caller passes
takes priority — so existing tests with bespoke construction needs can
still drive the factory.

The default mocks the factory ships with:

* ``panel`` — a ``MagicMock()`` whose ``get_relative_rect()`` returns an
  object with ``width=600`` and ``height=400``. (Most race/identity panels
  read width during ``_create_content``.)
* ``manager`` / ``ui_manager`` — a bare ``MagicMock()``.
* ``container`` — a ``MagicMock()`` (used by some screens / windows).
* ``rect`` — a ``pygame.Rect(0, 0, 600, 400)`` if pygame is importable,
  otherwise a ``MagicMock``.

Example
-------

::

    from tests.fixtures.ui_widget_factory import make_ui_widget
    from game.ui.panels.race_identity_panel import RaceIdentityPanel

    def test_update_config_reads_race_name(mock_race_config):
        panel = make_ui_widget(RaceIdentityPanel, race_config=mock_race_config)
        panel.race_name_input = MagicMock()
        panel.race_name_input.get_text.return_value = "Rossarian"
        panel.update_config()
        assert mock_race_config.race_name == "Rossarian"

The same call works for screens and windows; pass any extra constructor
arguments as kwargs.
"""

from __future__ import annotations

import contextlib
import inspect
from typing import Any, Type, TypeVar
from unittest.mock import MagicMock, patch


T = TypeVar("T")


# Names of pygame_gui element classes the factory patches during widget
# construction. The list covers everything we have observed in production
# UI panel/screen ``_create_content`` calls; anything outside it is simply
# left alone (the production code will then attempt the real construction
# and fail loudly, which is the correct signal).
_PYGAME_GUI_ELEMENT_NAMES: tuple[str, ...] = (
    "UIPanel",
    "UILabel",
    "UIButton",
    "UIImage",
    "UITextEntryLine",
    "UITextEntryBox",
    "UITextBox",
    "UIDropDownMenu",
    "UIScrollingContainer",
    "UISelectionList",
    "UIVerticalScrollBar",
    "UIHorizontalSlider",
    "UIWindow",
    "UIStatusBar",
    "UIScreenSpaceHealthBar",
    "UIProgressBar",
    "UITooltip",
)


def _default_panel_mock() -> MagicMock:
    """Build the default ``panel`` mock for ``__init__``."""

    panel = MagicMock(name="DefaultParentPanel")
    rect = MagicMock(name="PanelRect")
    rect.width = 600
    rect.height = 400
    panel.get_relative_rect.return_value = rect
    panel.get_abs_rect.return_value = rect
    panel.get_container.return_value = MagicMock(name="PanelContainer")
    return panel


def _default_rect() -> Any:
    """Return a reasonable ``rect`` default — real pygame.Rect when available."""

    try:
        import pygame  # local import — pygame may be initialized lazily

        return pygame.Rect(0, 0, 600, 400)
    except Exception:  # pragma: no cover - pygame should always be importable
        return MagicMock(name="DefaultRect")


def _build_default_kwargs(cls: Type[T]) -> dict[str, Any]:
    """Inspect ``cls.__init__`` and supply defaults for known parameter names.

    Only fills in parameters whose names match the well-known set
    (``panel`` / ``manager`` / ``ui_manager`` / ``container`` / ``rect``);
    everything else is left to the caller. This keeps the factory
    permissive for screens and windows that take bespoke arguments
    (``RaceConfig``, ``Empire``, etc.) — those callers must still pass the
    real value.
    """

    try:
        sig = inspect.signature(cls.__init__)
    except (TypeError, ValueError):
        # ``__init__`` is built-in or unintrospectable; nothing we can do.
        return {}

    defaults: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        # Only the well-known names get a sensible default; everything else
        # falls through to the caller (or to Python's normal "missing
        # argument" error if no default is declared).
        if name == "panel":
            defaults[name] = _default_panel_mock()
        elif name in ("manager", "ui_manager"):
            defaults[name] = MagicMock(name="UIManager")
        elif name == "container":
            defaults[name] = MagicMock(name="Container")
        elif name == "rect":
            defaults[name] = _default_rect()
    return defaults


@contextlib.contextmanager
def _patch_pygame_gui_elements(target_modules: tuple = ()):
    """Context manager that replaces every ``pygame_gui.elements.UI*`` class
    with a ``MagicMock`` for the duration of the block.

    Patches BOTH:

    * ``pygame_gui.elements.UI*`` — covers code that does
      ``pygame_gui.elements.UILabel(...)`` (qualified lookup).
    * Every ``UI*`` name imported into the ``target_modules`` tuple — covers
      code that does ``from pygame_gui.elements import UILabel`` and then
      uses ``UILabel(...)`` directly. ``patch.object(elements_module, ...)``
      does not affect already-imported bindings, so we have to walk each
      production module and patch its local copy.

    Using ``patch`` (vs assigning to module attributes manually) means each
    test gets a fresh Mock and the originals are guaranteed restored even
    if the constructor raises.
    """

    try:
        import pygame_gui.elements as elements_module
    except ImportError:  # pragma: no cover - pygame_gui is a hard dep
        yield
        return

    patches = []
    try:
        # 1. Patch the canonical pygame_gui.elements namespace.
        for element_name in _PYGAME_GUI_ELEMENT_NAMES:
            if hasattr(elements_module, element_name):
                p = patch.object(elements_module, element_name, MagicMock())
                p.start()
                patches.append(p)
        # 2. Patch any module that re-bound the same names via
        #    `from pygame_gui.elements import UI...`.
        for mod in target_modules:
            for element_name in _PYGAME_GUI_ELEMENT_NAMES:
                if hasattr(mod, element_name):
                    p = patch.object(mod, element_name, MagicMock())
                    p.start()
                    patches.append(p)
        yield
    finally:
        for p in reversed(patches):
            p.stop()


def _resolve_target_modules(cls: Type) -> tuple:
    """Return a tuple of modules whose `pygame_gui.elements.UI*` bindings
    need patching when constructing ``cls``.

    Always includes ``cls``'s defining module. Walks the MRO so subclasses
    that inherit a heavy ``__init__`` from a base also patch the base
    module (the base's qualified vs. local imports both get covered).
    """

    import sys

    modules = []
    seen = set()
    for klass in cls.__mro__:
        mod_name = getattr(klass, "__module__", None)
        if mod_name and mod_name not in seen and mod_name in sys.modules:
            seen.add(mod_name)
            modules.append(sys.modules[mod_name])
    return tuple(modules)


def make_ui_widget(
    cls: Type[T],
    extra_modules: tuple = (),
    **kwargs: Any,
) -> T:
    """Build an instance of ``cls`` via real ``__init__`` with mock pygame_gui.

    Arguments
    ---------
    cls
        The widget class to construct. May be any class whose ``__init__``
        builds ``pygame_gui.elements.UI*`` instances internally — panels,
        screens, windows, and gallery widgets are all in scope.
    extra_modules
        Optional tuple of additional modules to patch ``UI*`` bindings in.
        Use this when ``cls.__init__`` instantiates a sibling widget class
        from another module (the factory automatically patches ``cls``'s
        MRO modules, but not transitively-imported helpers like
        ``ModifierImpactGrid`` which live in their own module).
    **kwargs
        Any constructor arguments. Defaults are supplied for the
        well-known names (``panel``, ``manager`` / ``ui_manager``,
        ``container``, ``rect``); everything else must be passed
        explicitly. Caller-supplied values always take priority over
        defaults.

    Returns
    -------
    An instance of ``cls`` with its real attributes initialized — every
    ``self.panel``, ``self.ui_manager``, ``self.<element>`` reference
    that ``__init__`` assigns will be present (the elements are Mocks).
    """

    defaults = _build_default_kwargs(cls)
    defaults.update(kwargs)

    target_modules = _resolve_target_modules(cls) + tuple(extra_modules)
    with _patch_pygame_gui_elements(target_modules=target_modules):
        return cls(**defaults)


__all__ = ["make_ui_widget"]
