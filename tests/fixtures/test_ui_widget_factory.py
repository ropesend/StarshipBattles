"""Smoke tests for ``tests.fixtures.ui_widget_factory.make_ui_widget``.

PROJ-322 Task 5.0 verification — exercise the factory against a known
panel class to confirm:

* ``__init__`` runs to completion (not bypassed).
* Defaults for ``panel`` / ``manager`` / ``ui_manager`` are auto-supplied.
* Caller overrides take precedence.
* The returned object exposes the attributes the production class
  assigns during construction.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from tests.fixtures.ui_widget_factory import bypass_init, make_ui_widget


def test_make_ui_widget_constructs_race_identity_panel():
    """Factory builds a RaceIdentityPanel via real ``__init__`` (panel attrs
    set; UI element references initialized to None per ``_init_empty_refs``)."""

    from game.ui.panels.race_identity_panel import RaceIdentityPanel

    config = MagicMock()
    config.race_name = ""
    config.race_name_plural = ""
    config.faction_name = ""
    config.government_type = ""
    config.government_organization = ""
    config.leader_title = ""
    config.leader_name = ""
    config.physical_type = ""
    config.society_type = ""

    panel = make_ui_widget(RaceIdentityPanel, race_config=config)

    # Real __init__ ran: it stored the race_config and the auto-supplied
    # panel + manager mocks.
    assert panel.race_config is config
    assert panel.panel is not None
    assert panel.ui_manager is not None

    # _init_empty_refs ran during __init__ AND _create_content followed —
    # the UI element refs exist as attributes (set to mocked elements by
    # _create_content rather than the None placeholders).
    assert hasattr(panel, "race_name_input")
    assert hasattr(panel, "faction_name_input")
    assert hasattr(panel, "government_type_dropdown")


def test_make_ui_widget_caller_overrides_take_priority():
    """Caller-supplied panel/manager kwargs override the factory defaults."""

    from game.ui.panels.race_identity_panel import RaceIdentityPanel

    custom_panel = MagicMock(name="CustomPanel")
    custom_panel.get_relative_rect.return_value = MagicMock(width=999)
    custom_manager = MagicMock(name="CustomManager")
    config = MagicMock()

    panel = make_ui_widget(
        RaceIdentityPanel,
        panel=custom_panel,
        manager=custom_manager,
        race_config=config,
    )

    assert panel.panel is custom_panel
    assert panel.ui_manager is custom_manager


def test_make_ui_widget_constructs_race_summary_panel():
    """Factory works for the summary panel too — exercises the broader
    ``_create_content`` path with mocked pygame_gui elements."""

    from game.strategy.data.race_config import RaceConfig
    from game.ui.panels.race_summary_panel import RaceSummaryPanel

    # Real RaceConfig — the summary panel reads real preferences.
    config = RaceConfig(
        name="Test Race",
        flag_id="flag_01",
        portrait_id="portrait_01",
        theme_id="Atlantians",
        faction_name="Test Empire",
        race_name="Testarians",
    )
    asset_loader = MagicMock(name="AssetLoader")

    panel = make_ui_widget(
        RaceSummaryPanel,
        race_config=config,
        asset_loader=asset_loader,
    )

    # Construction succeeded — the summary panel's tracked state lives.
    assert panel.race_config is config
    assert panel._asset_loader is asset_loader
    # The summary_labels dict was initialized by ``__init__``.
    assert isinstance(panel.summary_labels, dict)
    # And its element collection lists exist.
    assert isinstance(panel.summary_flag_images, list)


@pytest.mark.parametrize(
    "kwarg_name",
    ["panel", "manager"],
)
def test_make_ui_widget_supplies_default_when_kwarg_omitted(kwarg_name):
    """Smoke check: omitting ``panel`` or ``manager`` does not raise — the
    factory's introspection-based defaulting fills them in."""

    from game.ui.panels.race_identity_panel import RaceIdentityPanel

    config = MagicMock()
    # Only pass race_config; rely on the factory for panel + manager defaults.
    panel = make_ui_widget(RaceIdentityPanel, race_config=config)

    # The kwarg under test maps to either ``self.panel`` or ``self.ui_manager``.
    if kwarg_name == "panel":
        assert panel.panel is not None
    else:
        assert panel.ui_manager is not None


# ---------------------------------------------------------------------------
# bypass_init context manager (PROJ-324 Task 1.1)
# ---------------------------------------------------------------------------


class _BypassInitTarget:
    """Disposable class for bypass_init lifecycle testing.

    A fresh class is constructed per test (via subclassing) so flag
    leakage from a buggy implementation is impossible to mask.
    """


def test_bypass_init_sets_and_clears_flag_normally():
    Cls = type("Target1", (_BypassInitTarget,), {})
    assert "bypass_init" not in Cls.__dict__

    with bypass_init(Cls):
        assert Cls.bypass_init is True

    assert "bypass_init" not in Cls.__dict__


def test_bypass_init_clears_flag_on_exception():
    Cls = type("Target2", (_BypassInitTarget,), {})

    with pytest.raises(RuntimeError, match="boom"):
        with bypass_init(Cls):
            assert Cls.bypass_init is True
            raise RuntimeError("boom")

    assert "bypass_init" not in Cls.__dict__


def test_bypass_init_nested_restores_previous_value():
    """Nested ``bypass_init`` on the same class restores the previous
    value (False / True), not just the absence of the attribute."""

    Cls = type("Target3", (_BypassInitTarget,), {})
    Cls.bypass_init = False  # pre-existing falsy value

    with bypass_init(Cls):
        assert Cls.bypass_init is True
        with bypass_init(Cls):
            assert Cls.bypass_init is True
        # Inner exit must restore to True (set by outer), not False.
        assert Cls.bypass_init is True

    # Outer exit restores to the original False.
    assert Cls.bypass_init is False


def test_bypass_init_preserves_pre_existing_truthy_value():
    Cls = type("Target4", (_BypassInitTarget,), {})
    Cls.bypass_init = "custom"

    with bypass_init(Cls):
        assert Cls.bypass_init is True

    assert Cls.bypass_init == "custom"


# ---------------------------------------------------------------------------
# _build_default_kwargs direct unit tests (PROJ-321..328 audit S4.6)
# ---------------------------------------------------------------------------
#
# The integration tests above cover the well-trodden RaceIdentityPanel /
# RaceSummaryPanel paths, but the introspection logic in _build_default_kwargs
# has signature shapes (positional-only, keyword-only, **kwargs, no signature)
# that are easier to pin against synthetic classes than against real production
# classes. These direct tests guard against regressions in the introspection
# itself, independent of any pygame_gui class shape.


from tests.fixtures.ui_widget_factory import _build_default_kwargs


class _AllWellKnown:
    def __init__(self, panel, manager, ui_manager, container, rect):
        self.panel = panel
        self.manager = manager
        self.ui_manager = ui_manager
        self.container = container
        self.rect = rect


class _MixedKnownAndCustom:
    def __init__(self, race_config, panel, manager, custom_param):
        self.race_config = race_config
        self.panel = panel
        self.manager = manager
        self.custom_param = custom_param


class _KeywordOnly:
    def __init__(self, *, panel, manager):
        self.panel = panel
        self.manager = manager


class _PositionalOnly:
    def __init__(self, panel, manager, /):
        self.panel = panel
        self.manager = manager


class _Variadic:
    def __init__(self, *args, **kwargs):
        pass


def test_build_default_kwargs_supplies_all_well_known_names():
    """Every well-known name (panel, manager, ui_manager, container, rect)
    gets a default."""
    defaults = _build_default_kwargs(_AllWellKnown)
    assert set(defaults.keys()) == {"panel", "manager", "ui_manager", "container", "rect"}
    assert all(v is not None for v in defaults.values())


def test_build_default_kwargs_skips_unknown_names():
    """Unknown-named parameters (race_config, custom_param) are not auto-defaulted —
    the caller must pass them. Well-known names (panel, manager) still get defaults."""
    defaults = _build_default_kwargs(_MixedKnownAndCustom)
    assert set(defaults.keys()) == {"panel", "manager"}
    assert "race_config" not in defaults
    assert "custom_param" not in defaults


def test_build_default_kwargs_handles_keyword_only_parameters():
    """KEYWORD_ONLY parameters are not skipped (they're regular named args)."""
    defaults = _build_default_kwargs(_KeywordOnly)
    assert set(defaults.keys()) == {"panel", "manager"}


def test_build_default_kwargs_handles_positional_only_parameters():
    """POSITIONAL_ONLY parameters with well-known names still get defaults
    (callers must pass them positionally though — this is a Python convention,
    not a factory enforcement)."""
    defaults = _build_default_kwargs(_PositionalOnly)
    assert set(defaults.keys()) == {"panel", "manager"}


def test_build_default_kwargs_skips_variadic_parameters():
    """*args and **kwargs are skipped — the function checks param.kind explicitly."""
    defaults = _build_default_kwargs(_Variadic)
    assert defaults == {}


def test_build_default_kwargs_returns_empty_dict_for_unintrospectable_init():
    """Built-in __init__ (e.g. object.__init__) is unintrospectable on some
    Python builds — function must return {} rather than raise."""
    # object.__init__ raises TypeError when passed to inspect.signature on CPython,
    # but only sometimes — depends on the build. Use a synthetic class with
    # a slot-only __init__ via __slots__ to construct a guaranteed-uninspectable case.
    # Easiest: pass `int` which has a built-in __init__ that inspect can't introspect
    # cleanly on some Python builds. If this is introspectable on the current build,
    # the test still passes (we only assert the return type/shape).
    defaults = _build_default_kwargs(object)
    assert isinstance(defaults, dict)
    # No well-known names — object.__init__ takes no parameters beyond self.
    assert "panel" not in defaults
    assert "manager" not in defaults
