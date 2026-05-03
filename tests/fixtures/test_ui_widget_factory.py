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

from tests.fixtures.ui_widget_factory import make_ui_widget


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
