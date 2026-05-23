"""
Unit tests for RaceSummaryPanel.

PROJ-44 Phase 7 Task 7.1: TDD tests for the summary panel extraction.
Tests the race summary display panel functionality.

PROJ-322 Task 5.14 (APC-001-F14): the legacy `RaceSummaryPanel.__new__` +
`patch.object(__init__, ...)` blocks have been replaced with the shared
`make_ui_widget` factory from `tests.fixtures.ui_widget_factory`. The
`TestFeat14RegistryDrivenSummary` helper keeps its bespoke mocking because
it needs to capture every UILabel constructor call by `side_effect`.
"""

import pygame
import pytest
from unittest.mock import MagicMock, patch

from tests.fixtures.ui_widget_factory import make_ui_widget


def _make_panel_with_mocked_pygame_gui(race_config):
    """PROJ-494 T2.11: extracted from
    `TestFeat14RegistryDrivenSummary._refresh_with_mocked_uilabel`.

    Stubs out pygame_gui inside `race_summary_panel`, instantiates a panel
    via `__new__`, wires the dynamic-label bookkeeping the column-3 code
    expects, calls `refresh()`, and returns `(ui_label_mock, panel)` so
    callers can collect label texts via `_collect_label_texts`.
    """
    from game.ui.panels import race_summary_panel as rsp_module

    # Fresh mock class so each call returns a distinct widget.
    ui_label_mock = MagicMock()
    ui_label_mock.side_effect = lambda *a, **kw: MagicMock()
    ui_panel_mock = MagicMock()
    ui_panel_mock.side_effect = lambda *a, **kw: MagicMock()
    ui_scroll_mock = MagicMock()
    ui_scroll_mock.side_effect = lambda *a, **kw: MagicMock()

    with patch.object(rsp_module.pygame_gui.elements, "UILabel", ui_label_mock), \
         patch.object(rsp_module.pygame_gui.elements, "UIPanel", ui_panel_mock), \
         patch.object(
             rsp_module.pygame_gui.elements,
             "UIScrollingContainer",
             ui_scroll_mock,
         ), \
         patch.object(rsp_module, "create_section_header", MagicMock()):
        panel = rsp_module.RaceSummaryPanel.__new__(rsp_module.RaceSummaryPanel)
        panel.race_config = race_config
        panel.summary_labels = {}
        panel.summary_flag_images = []
        panel.summary_portrait_image = None
        panel.summary_ship_images = []
        panel.summary_ship_labels = []
        panel._asset_loader = MagicMock()
        panel.summary_flag_panel = None
        panel.summary_portrait_panel = None
        panel.summary_ship_panel = None
        panel.ui_manager = MagicMock()
        panel.panel = MagicMock()
        panel._env_scroll_container = MagicMock()
        # _rebuild_env_scroll_content reads container.get_relative_rect().width
        # so it can size labels — give it a real int.
        panel._env_scroll_container.get_relative_rect.return_value = pygame.Rect(
            0, 0, 800, 400,
        )
        panel._dynamic_env_labels = []

        panel.refresh()

    return ui_label_mock, panel


# =============================================================================
# Fixtures
# =============================================================================

# PROJ-283 Phase 4: switched from MagicMock to real RaceConfig instances —
# the summary panel formatters now read from `race_config.preferences` (a
# typed dict of `EnvironmentalPreference`), and MagicMock can't impersonate
# the dict subscript + attribute access cleanly. Real RaceConfig is light
# enough to construct in a fixture, and `__post_init__` backfills any
# preferences not explicitly overridden.

def _override_pref(rc, factor_id, *, setpoint=None, tolerance=None):
    from game.strategy.data.environmental_preference import EnvironmentalPreference
    from game.strategy.data.habitability_factors import get_factor
    f = get_factor(factor_id)
    rc.preferences[factor_id] = EnvironmentalPreference(
        setpoint=setpoint if setpoint is not None else f.default_setpoint,
        tolerance=tolerance if tolerance is not None else f.default_tolerance,
        min_value=f.min_value, max_value=f.max_value, step=f.step,
    )


@pytest.fixture
def mock_race_config():
    """Real RaceConfig populated for summary-display tests.

    Sets two atmospheric setpoints (O2, N2) so atmosphere-summary tests
    have something non-zero to render.
    """
    from game.strategy.data.race_config import RaceConfig
    config = RaceConfig(
        name="Test Race",
        flag_id="flag_01",
        portrait_id="portrait_01",
        theme_id="Atlantians",
        faction_name="Test Empire",
        race_name="Testarians",
        government_type="Empire",
        government_organization="Centralized",
        physical_type="Humanoid",
        society_type="Collectivist",
        homeworld_type="CONTINENTAL",
        bio_description="Test biological description",
        socio_description="Test sociological description",
    )
    _override_pref(config, "gravity", setpoint=9.81, tolerance=0.3 * 9.81)
    _override_pref(config, "temperature", setpoint=293.0, tolerance=50.0)
    _override_pref(config, "radiation", setpoint=0.0, tolerance=10.0)
    _override_pref(config, "water", setpoint=0.5, tolerance=0.3)
    # Atmosphere setpoints — keep the gases that the legacy fixture exercised
    _override_pref(config, "gas.O2", setpoint=20000.0)
    _override_pref(config, "gas.N2", setpoint=10000.0)
    return config


@pytest.fixture
def mock_race_config_empty():
    """Real RaceConfig with no atmosphere setpoints — exercises the
    'all neutral' atmosphere-summary branch."""
    from game.strategy.data.race_config import RaceConfig
    config = RaceConfig(
        name="",
        # Empty identity fields exercise placeholder rendering. `validate()`
        # would reject this config, but the summary-panel formatters never
        # call validate — they just read attributes.
        flag_id="",
        portrait_id="",
        theme_id="",
    )
    # Gas setpoints all zero except registry defaults (O2=21k, N2=79k);
    # explicitly zero them so the atmosphere summary formatter falls
    # through to "All neutral".
    for fid in list(config.preferences.keys()):
        if fid.startswith("gas."):
            _override_pref(config, fid, setpoint=0.0)
    return config


@pytest.fixture
def mock_ui_manager():
    """Create a mock pygame_gui UIManager."""
    manager = MagicMock()
    return manager


@pytest.fixture
def mock_asset_loader():
    """Create a mock RaceAssetLoader."""
    loader = MagicMock()
    return loader


def _make_summary_panel(race_config=None, **overrides):
    """Build a `RaceSummaryPanel` via the shared `make_ui_widget` factory.

    Replaces the legacy ``with patch.object(RaceSummaryPanel, '__init__', ...)``
    + ``__new__`` + manual attribute wiring blocks (PROJ-322 Task 5.14 /
    APC-001-F14). The factory patches every ``pygame_gui.elements.UI*`` class
    with a Mock for the duration of `__init__`, so heavy `_create_content`
    runs but is bounded.

    Post-construction the helper also forces `summary_flag_panel` /
    `summary_portrait_panel` / `summary_ship_panel` / `_env_scroll_container`
    to `None` because `refresh()`'s helpers short-circuit on those when None
    but cannot do arithmetic on the MagicMock geometry the factory leaves.

    `race_config` is required by the production `__init__`. Tests typically
    then override `panel.summary_labels` (or similar attrs) with their own
    `MagicMock`-keyed dict before calling `panel.refresh()` to assert against
    the controlled label.
    """
    from game.ui.panels.race_summary_panel import RaceSummaryPanel

    asset_loader = overrides.pop("asset_loader", MagicMock())
    panel = make_ui_widget(
        RaceSummaryPanel,
        race_config=race_config,
        asset_loader=asset_loader,
        **overrides,
    )
    # Disable the geometry-driven refresh paths (flag/portrait/ship panel
    # rebuilds + column-3 env scroll) — they were wired to MagicMocks during
    # __init__ but the legacy refresh tests expect None-guarded short-
    # circuits. Tests can re-assign these attrs if they need the real path.
    panel.summary_flag_panel = None
    panel.summary_portrait_panel = None
    panel.summary_ship_panel = None
    panel._env_scroll_container = None
    return panel


# =============================================================================
# Test: RaceSummaryPanel Import and Creation
# =============================================================================

class TestRaceSummaryPanelCreation:
    """Tests for RaceSummaryPanel initialization."""

    def test_race_summary_panel_init_seeds_label_dict_with_value_keys(self, mock_race_config):
        """RaceSummaryPanel.__init__ → _create_content populates
        summary_labels with the data-row entries used by refresh()
        (faction_value, race_value, gov_value, physical_value,
        society_value). Pinning these specific keys means deletion of
        a row in _create_content fails the test, rather than a
        toothless hasattr() check that can't notice the regression.
        See race_summary_panel.py:386-... refresh() for the read sites."""
        panel = _make_summary_panel(race_config=mock_race_config)

        # The refresh()-consumed value keys must all be present.
        for key in (
            'faction_value', 'race_value', 'gov_value',
            'physical_value', 'society_value',
        ):
            assert key in panel.summary_labels, (
                f"summary_labels missing '{key}' — refresh() reads this key"
            )
        # Image collections are populated to lists/None at construction.
        assert isinstance(panel.summary_flag_images, list)
        assert isinstance(panel.summary_ship_images, list)

# =============================================================================
# Test: Summary Data Formatting
# =============================================================================

class TestSummaryDataFormatting:
    """Tests for summary data formatting methods."""

    # FEAT-14: gravity / temperature / radiation / water / atmosphere are no
    # longer rendered via per-factor formatters. The Summary tab now iterates
    # FACTOR_REGISTRY end-to-end and uses `PreferenceRow.format_value` —
    # see TestFeat14RegistryDrivenSummary below.

    def test_format_description_status_with_content(self, mock_race_config):
        """Description status shows character count when content exists."""
        panel = _make_summary_panel(race_config=mock_race_config)

        bio_status = panel._format_bio_status()
        socio_status = panel._format_socio_status()

        assert "chars" in bio_status or "Set" in bio_status
        assert "chars" in socio_status or "Set" in socio_status

    def test_format_description_status_empty(self, mock_race_config_empty):
        """Description status shows empty when no content."""
        panel = _make_summary_panel(race_config=mock_race_config_empty)

        bio_status = panel._format_bio_status()

        assert "Empty" in bio_status or "0" in bio_status


# =============================================================================
# Test: Refresh Summary
# =============================================================================

class TestRefreshSummary:
    """Tests for refreshing summary display."""

    def test_refresh_updates_faction_label(self, mock_race_config):
        """refresh() forwards the faction summary string to faction_value.set_text.

        PROJ-66 Phase 6: Changed from name_value to faction_value.

        PROJ-346 strengthening: previously asserted only that set_text
        was called (proves invocation, not the value). Now pin the
        single concrete arg returned by ``_format_faction_summary``,
        which (per production race_summary_panel.py:317-324) returns
        ``race_config.faction_name`` when set. mock_race_config seeds
        ``faction_name='Test Empire'``.
        """
        panel = _make_summary_panel(race_config=mock_race_config)
        # Override the labels dict with a controlled mock so the assertion
        # has a deterministic target — the factory's `_create_content` had
        # populated this with mocked-element instances we don't care about.
        panel.summary_labels = {'faction_value': MagicMock()}
        # _env_scroll_container is None for legacy refresh paths.
        panel._env_scroll_container = None

        panel.refresh()

        panel.summary_labels['faction_value'].set_text.assert_called_once_with(
            "Test Empire"
        )

    def test_refresh_updates_theme_label(self, mock_race_config):
        """refresh() forwards race_config.theme_id to theme_value.set_text.

        PROJ-346 strengthening: previously asserted only that set_text
        was called. Now pin the concrete arg — production passes
        ``race_config.theme_id or "[Click Ships tab to set]"``
        (race_summary_panel.py:402-404). mock_race_config seeds
        ``theme_id='Atlantians'``.
        """
        panel = _make_summary_panel(race_config=mock_race_config)
        panel.summary_labels = {'theme_value': MagicMock()}
        panel._env_scroll_container = None

        panel.refresh()

        panel.summary_labels['theme_value'].set_text.assert_called_once_with(
            "Atlantians"
        )

    def test_refresh_clears_previous_flag_images(self, mock_race_config):
        """refresh() clears previous flag images before creating new ones."""
        panel = _make_summary_panel(race_config=mock_race_config)

        # Mock previous flag image — replace whatever _create_content put
        # in summary_flag_images with this one we control.
        old_image = MagicMock()
        panel.summary_flag_images = [old_image]
        panel._env_scroll_container = None

        panel.refresh()

        # Old image should be killed
        old_image.kill.assert_called()


# =============================================================================
# Test: Display Name Placeholders
# =============================================================================

class TestPlaceholders:
    """Tests for placeholder text when values not set."""

    def test_faction_placeholder_when_not_set(self, mock_race_config_empty):
        """Shows placeholder when faction name not set.

        PROJ-66 Phase 6: Changed from name_value to faction_value.
        """
        panel = _make_summary_panel(race_config=mock_race_config_empty)
        faction_label = MagicMock()
        panel.summary_labels = {'faction_value': faction_label}
        panel._env_scroll_container = None

        panel.refresh()

        # Should show placeholder text
        call_arg = faction_label.set_text.call_args[0][0]
        assert "Identity" in call_arg or "set" in call_arg.lower()

    def test_theme_placeholder_when_not_set(self, mock_race_config_empty):
        """Shows placeholder when theme not set."""
        panel = _make_summary_panel(race_config=mock_race_config_empty)
        theme_label = MagicMock()
        panel.summary_labels = {'theme_value': theme_label}
        panel._env_scroll_container = None

        panel.refresh()

        # Should show placeholder text
        call_arg = theme_label.set_text.call_args[0][0]
        assert "Ships" in call_arg or "set" in call_arg.lower()


# =============================================================================
# FEAT-14: Registry-driven Summary tab
# =============================================================================


def _collect_label_texts(label_constructor_mock) -> list:
    """Pull every `text=` (or 2nd positional) value passed to a mocked
    UILabel constructor."""
    texts: list = []
    for call in label_constructor_mock.call_args_list:
        args, kwargs = call
        if "text" in kwargs:
            texts.append(kwargs["text"])
    return texts


@pytest.fixture
def mock_race_config_full():
    """RaceConfig with non-default setpoints on every FACTOR_REGISTRY entry
    (so the gas filter doesn't skip any) — exercises the full registry render."""
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.data.environmental_preference import EnvironmentalPreference
    from game.strategy.data.habitability_factors import FACTOR_REGISTRY

    config = RaceConfig(name="Full Race", flag_id="f", portrait_id="p", theme_id="t")
    for fid, factor in FACTOR_REGISTRY.items():
        # Non-zero setpoint everywhere so gas filter renders all 10 gases.
        setpoint = factor.default_setpoint if factor.default_setpoint > 0 else 1.0
        config.preferences[fid] = EnvironmentalPreference(
            setpoint=setpoint,
            tolerance=factor.default_tolerance,
            min_value=factor.min_value,
            max_value=factor.max_value,
            step=factor.step,
        )
    return config


class TestFeat14RegistryDrivenSummary:
    """FEAT-14: Summary tab iterates FACTOR_REGISTRY end-to-end and renders
    every aptitude explicitly. Reuses `PreferenceRow.format_value` — no
    per-factor formatters in the panel."""

    def _refresh_with_mocked_uilabel(self, race_config, monkeypatch=None):
        """Stub out pygame_gui inside the summary panel module, instantiate
        a panel via __new__ (skipping pygame init), wire the dynamic-label
        bookkeeping the new column-3 code expects, call refresh(), and
        return the captured UILabel-text list.

        PROJ-494 T2.11: nested patches + summary-panel field wiring extracted
        into the module-level `_make_panel_with_mocked_pygame_gui` factory.
        """
        ui_label_mock, panel = _make_panel_with_mocked_pygame_gui(race_config)
        return _collect_label_texts(ui_label_mock), panel

    def test_refresh_renders_every_scalar_factor_display_name(
        self, mock_race_config_full,
    ):
        """Every FACTOR_REGISTRY scalar entry's `display_name` appears in the
        rendered Summary text. This is the registry-driven contract."""
        from game.strategy.data.habitability_factors import iter_scalar_factors

        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config_full)
        joined = "\n".join(texts)
        for factor in iter_scalar_factors():
            assert factor.display_name in joined, (
                f"Scalar factor {factor.id} ({factor.display_name}) missing "
                f"from Summary tab. Rendered text: {joined!r}"
            )

    def test_refresh_renders_every_set_gas_factor_display_name(
        self, mock_race_config_full,
    ):
        """Every gas factor with setpoint > 0 appears by display name. The
        full-config fixture sets every gas to non-zero, so all 10 gases
        must render."""
        from game.strategy.data.habitability_factors import iter_gas_factors

        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config_full)
        joined = "\n".join(texts)
        for factor in iter_gas_factors():
            assert factor.display_name in joined, (
                f"Gas factor {factor.id} ({factor.display_name}) missing "
                f"from Summary tab."
            )

    def test_refresh_uses_preference_row_format_for_setpoint(
        self, mock_race_config_full,
    ):
        """Setpoint values are formatted via PreferenceRow.format_value —
        gravity at 9.81 m/s^2 should render as "1.0 g" (display_scale 1/9.81,
        precision 1, unit "g")."""
        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config_full)
        joined = "\n".join(texts)
        # Gravity setpoint 9.81 m/s^2 → "1.0 g"
        assert "1.0 g" in joined, (
            f"Gravity setpoint not rendered with PROJ-293 display contract "
            f"in {joined!r}"
        )
        # Temperature 293 K (precision 0)
        assert "293 K" in joined or "293K" in joined, (
            f"Temperature setpoint not rendered with display unit in {joined!r}"
        )

    def test_refresh_renders_all_seven_aptitudes_by_name(
        self, mock_race_config,
    ):
        """All 7 RaceConfig aptitudes show with explicit human-readable labels
        and their assigned scores. PROJ-283 collapsed happiness +
        population_growth into base_happiness + base_reproduction_rate;
        those are NOT counted as 'aptitudes' but should still appear."""
        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config)
        joined = "\n".join(texts)
        # Each aptitude's human-readable name + value present.
        expected_aptitude_labels = [
            "Strength",
            "Intelligence",
            "Constitution",
            "Dexterity",
            "Tolerance",        # tolerance_other_species
            "Cooperation",
            "Conflict Tolerance",
        ]
        for label in expected_aptitude_labels:
            assert label in joined, (
                f"Aptitude label {label!r} missing from Summary tab. "
                f"Rendered: {joined!r}"
            )

    def test_refresh_renders_base_happiness_and_reproduction(
        self, mock_race_config,
    ):
        """The PROJ-283 derived seeds — base_happiness and
        base_reproduction_rate — are still rendered explicitly (they are not
        aptitudes per se, but the user wants a complete review)."""
        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config)
        joined = "\n".join(texts)
        # base_happiness default = 0.5 → "0.50"
        # base_reproduction_rate default = 0.03 → "3.0%"
        assert "Happiness" in joined or "happiness" in joined.lower()
        assert "Reproduction" in joined or "reproduction" in joined.lower()

    def test_adding_factor_to_registry_surfaces_automatically(
        self, mock_race_config_full, monkeypatch,
    ):
        """Acceptance: adding a factor to FACTOR_REGISTRY surfaces a row with
        ZERO panel-side change (matches PROJ-283/293 contract).

        We monkeypatch `iter_scalar_factors` to yield an extra synthetic
        factor and assert its display_name appears in the rendered text."""
        from game.strategy.data.habitability_factors import (
            HabitabilityFactor,
            iter_scalar_factors,
            _default_gaussian_scorer,
        )
        from game.strategy.data.environmental_preference import EnvironmentalPreference

        fake_factor = HabitabilityFactor(
            id="fake_axis",
            display_name="Fake Test Axis",
            unit="widgets",
            display_scale=1.0,
            weight=0.1,
            default_setpoint=42.0,
            default_tolerance=5.0,
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            extractor=lambda planet: 0.0,
            scorer=_default_gaussian_scorer,
            display_unit="W",
            display_precision=0,
        )

        original = list(iter_scalar_factors())

        def patched_iter():
            yield from original
            yield fake_factor

        # Inject a preference for the fake factor so the panel doesn't
        # KeyError on lookup.
        mock_race_config_full.preferences["fake_axis"] = EnvironmentalPreference(
            setpoint=fake_factor.default_setpoint,
            tolerance=fake_factor.default_tolerance,
            min_value=fake_factor.min_value,
            max_value=fake_factor.max_value,
            step=fake_factor.step,
        )

        from game.ui.panels import race_summary_panel as rsp_module
        from game.strategy.data import habitability_factors as hab_module
        monkeypatch.setattr(rsp_module, "iter_scalar_factors", patched_iter)
        # The budget calculator (called by _format_budget_summary) iterates
        # race_config.preferences and looks up each factor in FACTOR_REGISTRY
        # via get_factor(). Register the fake there too so the lookup
        # succeeds — this is the same single-edit contract the ticket
        # promises ("adding to FACTOR_REGISTRY surfaces automatically").
        monkeypatch.setitem(hab_module.FACTOR_REGISTRY, "fake_axis", fake_factor)

        texts, _ = self._refresh_with_mocked_uilabel(mock_race_config_full)
        joined = "\n".join(texts)
        assert "Fake Test Axis" in joined, (
            f"Adding a factor to FACTOR_REGISTRY did not surface it on the "
            f"Summary tab. Rendered text: {joined!r}"
        )


# =============================================================================
# PROJ-339: characterization tests
# =============================================================================


class TestPROJ339GovernmentFormatting:
    """PROJ-339: pin `_format_government_summary` 3-state behavior."""

    def test_refresh_updates_government_when_org_set(self, mock_race_config):
        """`_format_government_summary` renders type alone when org is unset,
        type + org when both set, and the placeholder when neither set."""
        panel = _make_summary_panel(race_config=mock_race_config)

        # Both type and org set
        mock_race_config.government_type = "Empire"
        mock_race_config.government_organization = "Centralized"
        assert panel._format_government_summary() == "Government: Empire (Centralized)"

        # Type only
        mock_race_config.government_organization = ""
        assert panel._format_government_summary() == "Government: Empire"

        # Neither
        mock_race_config.government_type = ""
        assert panel._format_government_summary() == "Government: --"


class TestPROJ339ShipPreviewSkips:
    """PROJ-339: pin the early-return paths in `_refresh_ship_preview`."""

    def test_refresh_ship_preview_skips_when_theme_unset(
        self, mock_race_config_empty,
    ):
        """A falsy `theme_id` short-circuits before any
        `ShipThemeManager` lookup — no images attached."""
        from game.ui.panels import race_summary_panel as rsp_module

        panel = _make_summary_panel(race_config=mock_race_config_empty)
        # theme_id is "" in the empty fixture
        assert mock_race_config_empty.theme_id == ""
        # Force ship_panel non-None so the OTHER short-circuit (no panel)
        # is not the reason we exit.
        panel.summary_ship_panel = MagicMock()
        panel.summary_ship_images = []
        panel.summary_ship_labels = []

        with patch.object(
            rsp_module, "get_default_ship_theme_manager",
        ) as mock_get_mgr:
            panel._refresh_ship_preview()

        # Theme manager NEVER consulted — early return triggered first.
        mock_get_mgr.assert_not_called()
        assert panel.summary_ship_images == []
        assert panel.summary_ship_labels == []

    def test_refresh_ship_preview_skips_category_when_surface_missing(
        self, mock_race_config,
    ):
        """When `ShipThemeManager.load_image`/`get_portrait_image` returns
        `None` for a category, that slot's images are skipped (not
        appended) but other categories with surfaces still render."""
        from game.ui.panels import race_summary_panel as rsp_module

        panel = _make_summary_panel(race_config=mock_race_config)
        panel.summary_ship_panel = MagicMock()
        panel.summary_ship_images = []
        panel.summary_ship_labels = []

        # Theme manager: returns None for every skin/portrait, so no
        # UIImage should be appended. Labels still get appended (one per
        # category, regardless of surface presence).
        mock_mgr = MagicMock()
        mock_mgr.load_image.return_value = None
        mock_mgr.get_portrait_image.return_value = None

        with patch.object(
            rsp_module, "get_default_ship_theme_manager", return_value=mock_mgr,
        ), patch.object(
            rsp_module.pygame_gui.elements, "UIImage",
        ) as mock_ui_image, patch.object(
            rsp_module.pygame_gui.elements, "UILabel",
            side_effect=lambda *a, **kw: MagicMock(),
        ):
            panel._refresh_ship_preview()

        # No UIImage was instantiated for any category (all surfaces None).
        mock_ui_image.assert_not_called()
        # Three category labels were still appended.
        assert len(panel.summary_ship_labels) == 3


class TestPROJ339EnvScrollMissingPreference:
    """PROJ-339: pin the defensive '--' rendering in
    `_render_factor_rows` for a missing preference id."""

    def test_rebuild_env_scroll_content_renders_dash_for_missing_preference(
        self, mock_race_config,
    ):
        """If a scalar factor's id is absent from `race_config.preferences`,
        the row text falls back to '<display_name>: --' rather than
        raising a KeyError."""
        from game.ui.panels import race_summary_panel as rsp_module
        from game.strategy.data.habitability_factors import iter_scalar_factors

        # Drop one scalar factor's preference so the panel hits the
        # missing-preference branch.
        scalar_ids = [f.id for f in iter_scalar_factors()]
        dropped_id = scalar_ids[0]
        dropped_display_name = next(
            f.display_name for f in iter_scalar_factors() if f.id == dropped_id
        )
        del mock_race_config.preferences[dropped_id]

        # Re-use the same UILabel-capture pattern as
        # TestFeat14RegistryDrivenSummary.
        ui_label_mock = MagicMock()
        ui_label_mock.side_effect = lambda *a, **kw: MagicMock()
        ui_panel_mock = MagicMock()
        ui_panel_mock.side_effect = lambda *a, **kw: MagicMock()
        ui_scroll_mock = MagicMock()
        ui_scroll_mock.side_effect = lambda *a, **kw: MagicMock()

        with patch.object(rsp_module.pygame_gui.elements, "UILabel", ui_label_mock), \
             patch.object(rsp_module.pygame_gui.elements, "UIPanel", ui_panel_mock), \
             patch.object(
                 rsp_module.pygame_gui.elements,
                 "UIScrollingContainer",
                 ui_scroll_mock,
             ), \
             patch.object(rsp_module, "create_section_header", MagicMock()):
            panel = rsp_module.RaceSummaryPanel.__new__(rsp_module.RaceSummaryPanel)
            panel.race_config = mock_race_config
            panel.summary_labels = {}
            panel.summary_flag_images = []
            panel.summary_portrait_image = None
            panel.summary_ship_images = []
            panel.summary_ship_labels = []
            panel._asset_loader = MagicMock()
            panel.summary_flag_panel = None
            panel.summary_portrait_panel = None
            panel.summary_ship_panel = None
            panel.ui_manager = MagicMock()
            panel.panel = MagicMock()
            panel._env_scroll_container = MagicMock()
            panel._env_scroll_container.get_relative_rect.return_value = pygame.Rect(
                0, 0, 800, 400,
            )
            panel._dynamic_env_labels = []

            panel.refresh()

        # The dropped factor must render with the '--' fallback.
        texts = [
            call.kwargs["text"]
            for call in ui_label_mock.call_args_list
            if "text" in call.kwargs
        ]
        joined = "\n".join(texts)
        assert f"{dropped_display_name}: --" in joined, (
            f"Missing-preference fallback not rendered. "
            f"Expected '{dropped_display_name}: --' in: {joined!r}"
        )


class TestPROJ339HandleButtonClick:
    """PROJ-339: pin `handle_button_click` callback gating."""

    def test_handle_button_click_invokes_load_callback_only_when_btn_load(
        self, mock_race_config,
    ):
        """The Load Race callback fires ONLY when the clicked element is
        `btn_load` AND `on_load_race_callback` is bound. Other elements
        (or no callback) → no-op returning False."""
        load_cb = MagicMock()
        panel = _make_summary_panel(
            race_config=mock_race_config,
            on_load_race_callback=load_cb,
        )
        # btn_load was created during _create_content as a Mock; we
        # control it explicitly so identity comparisons work.
        btn_load_marker = MagicMock()
        panel.btn_load = btn_load_marker

        # Clicked element IS btn_load AND callback bound → fires once.
        result = panel.handle_button_click(btn_load_marker)
        assert result is True
        load_cb.assert_called_once()

        # Some other element → no fire, return False.
        load_cb.reset_mock()
        other_btn = MagicMock()
        result = panel.handle_button_click(other_btn)
        assert result is False
        load_cb.assert_not_called()

        # btn_load clicked but callback unbound → no fire, return False.
        panel.on_load_race_callback = None
        result = panel.handle_button_click(btn_load_marker)
        assert result is False
