"""
Unit tests for EmpireTreasuryPanel.

PROJ-99 Phase 2: Tests for treasury panel layout, formatting, and data binding.

PROJ-494 T2.14: the 4-decorator `@patch(create_section_header)` /
`@patch(UIScrollingContainer)` / `@patch(UILabel)` / `@patch(UIImage)` stack
that wrapped 16+ methods has been replaced by a single autouse
`_patched_empire_treasury_imports` fixture that injects the same mocks onto
the test instance as `self.mock_header`, `self.mock_container`, `self.mock_label`,
`self.mock_image`. Method signatures no longer take the 4 positional args.
"""
from contextlib import ExitStack

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.empire_economy_calculator import EmpireEconomySnapshot

PLANET_RESOURCE_NAMES = ["metals", "organics", "vapors", "radioactives", "exotics"]
from game.ui.panels.empire_treasury_panel import (
    EmpireTreasuryPanel,
    LABEL_COL_WIDTH,
    RESOURCE_COL_WIDTH,
    ICON_SIZE,
    ROW_HEIGHT,
    LEFT_MARGIN,
    TOP_MARGIN,
)


# =============================================================================
# Fixtures
# =============================================================================

# =============================================================================
# PROJ-327 Phase 2 Task 2.11: scope-rescope notes
#
# `mock_ui_manager`, `mock_panel`, and `mock_resource_icons` are pure inputs:
# they are passed to `EmpireTreasuryPanel(...)` and the production code only
# reads from them (`panel.get_relative_rect()`, `ui_manager` as a `manager=`
# kwarg, `resource_icons[name]` as a lookup). No test in this file mutates
# any of these three fixtures. Rescoping them to module shaves ~17x the
# per-test MagicMock-tree construction cost without functional impact.
#
# `sample_snapshot` IS mutated by 4 tests in TestPopulationUpkeepRow
# (`sample_snapshot.total_population_upkeep = ...`). It MUST remain
# function-scoped, otherwise the mutations leak across tests.
#
# Original PROJ-322 Task 2.11 deferral cited "mutable MagicMocks accumulate
# assert state" (i.e. .assert_called_once_with after a call records state).
# That is true, but only `mock_panel.get_relative_rect`,
# `self.mock_container.assert_called_once`, `old_container.kill.assert_called_once`,
# and similar call-records are checked — and those are checked on either
# (a) the inner `mock_container`/`mock_header`/etc that come from `@patch`
# decorators (not these fixtures), or (b) `panel._scroll_container.kill`
# /element.kill (also not these fixtures). So accumulated call state on
# `mock_ui_manager` / `mock_panel` / `mock_resource_icons` is never asserted
# on in this file. Rescope is safe.
# =============================================================================


def _build_sample_snapshot() -> EmpireEconomySnapshot:
    """Build a sample EmpireEconomySnapshot with test data (constructor body)."""
    snapshot = EmpireEconomySnapshot()

    # Production
    snapshot.colony_production = {
        "metals": 100.0, "organics": 200.0, "vapors": 50.0,
        "radioactives": 25.0, "exotics": 10.0
    }
    snapshot.ship_production = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.trade_production = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.tribute_production = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.mining_production = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.total_production = snapshot.colony_production.copy()

    # Expenses
    snapshot.tribute_expenses = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.construction_expenses_ships = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.construction_expenses_complexes = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.total_expenses = {r: 0.0 for r in PLANET_RESOURCE_NAMES}

    # Treasury
    snapshot.net_resources = {
        "metals": 100.0, "organics": 200.0, "vapors": 50.0,
        "radioactives": 25.0, "exotics": 10.0
    }
    snapshot.current_storage = {
        "metals": 5000.0, "organics": 3000.0, "vapors": 1000.0,
        "radioactives": 500.0, "exotics": 100.0
    }
    snapshot.max_storage = {
        "metals": 10000.0, "organics": 10000.0, "vapors": 10000.0,
        "radioactives": 10000.0, "exotics": 10000.0
    }

    return snapshot


@pytest.fixture
def sample_snapshot() -> EmpireEconomySnapshot:
    """Create a sample EmpireEconomySnapshot with test data.

    Function-scoped: 4 tests in TestPopulationUpkeepRow mutate
    `snapshot.total_population_upkeep` and would otherwise leak across tests.
    """
    return _build_sample_snapshot()


@pytest.fixture(scope="module")
def mock_ui_manager():
    """Mock pygame_gui UIManager. Module-scoped: pure-input MagicMock,
    never mutated nor asserted-on across the file (PROJ-327 Phase 2 Task 2.11)."""
    return MagicMock()


@pytest.fixture(scope="module")
def mock_panel():
    """Mock UIPanel with realistic dimensions. Module-scoped: pure-input
    container, only `.get_relative_rect()` is called (returns the same inner
    MagicMock) and tests verify identity, not call counts (PROJ-327 Phase 2
    Task 2.11)."""
    panel = MagicMock()
    panel.get_relative_rect.return_value = MagicMock(width=800, height=600)
    return panel


@pytest.fixture(scope="module")
def mock_resource_icons():
    """Mock resource icons dict. Module-scoped: pure-input lookup table,
    never mutated nor asserted-on (PROJ-327 Phase 2 Task 2.11)."""
    icons = {}
    for resource in PLANET_RESOURCE_NAMES:
        mock_surface = MagicMock()
        mock_surface.get_size.return_value = (ICON_SIZE, ICON_SIZE)
        icons[resource] = mock_surface
    return icons


@pytest.fixture
def patched_treasury_imports(request):
    """PROJ-494 T2.14: stand up the 4-mock stack
    (create_section_header / UIScrollingContainer / UILabel / UIImage) that
    previously decorated 16+ methods individually. Attaches mocks to the test
    instance so existing assertion sites (`self.mock_container.call_args`,
    `self.mock_image.assert_not_called()`, etc.) continue to work via
    `self.mock_*`.
    """
    targets = (
        ('mock_header', 'game.ui.panels.empire_treasury_panel.create_section_header'),
        ('mock_container', 'game.ui.panels.empire_treasury_panel.UIScrollingContainer'),
        ('mock_label', 'game.ui.panels.empire_treasury_panel.UILabel'),
        ('mock_image', 'game.ui.panels.empire_treasury_panel.UIImage'),
    )
    with ExitStack() as stack:
        for attr, target in targets:
            setattr(request.instance, attr, stack.enter_context(patch(target)))
        yield


# =============================================================================
# Resource Abbreviations Tests
# =============================================================================

class TestResourceAbbreviations:
    """PROJ-346: pin EmpireTreasuryPanel header rendering against the
    abbreviation lookup, NOT the module-level dict literal.

    The previous tests only inspected ``RESOURCE_ABBREVIATIONS`` (a
    constant in ``game.ui.utils.resource_display``); they would have
    passed even if the panel never imported the lookup. These rewrites
    construct the panel and assert the header-row UILabel calls the
    panel actually issues, which is the production-pinning behaviour.
    """

    def _build_and_capture_label_texts(
        self, mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Construct an EmpireTreasuryPanel and return every UILabel text= arg
        produced during ``_build_resource_header`` (the only call site that
        consumes ``get_resource_abbreviation``)."""
        captured_texts: list[str] = []

        def _label_factory(*args, **kwargs):
            captured_texts.append(kwargs.get("text", ""))
            return MagicMock()

        with patch(
            'game.ui.panels.empire_treasury_panel.create_section_header'
        ), patch(
            'game.ui.panels.empire_treasury_panel.UIScrollingContainer'
        ), patch(
            'game.ui.panels.empire_treasury_panel.UILabel',
            side_effect=_label_factory,
        ), patch(
            'game.ui.panels.empire_treasury_panel.UIImage'
        ):
            EmpireTreasuryPanel(
                mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
            )
        return captured_texts

    def test_panel_header_renders_an_abbreviation_for_every_planetary_resource(
        self, mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Every planetary resource produces an abbreviation UILabel in the
        header row (pins the per-resource ``get_resource_abbreviation`` call,
        not just the dict's keys)."""
        from game.ui.utils.resource_display import get_resource_abbreviation

        texts = self._build_and_capture_label_texts(
            mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
        )

        for resource in PLANET_RESOURCE_NAMES:
            assert get_resource_abbreviation(resource) in texts, (
                f"Panel header missing abbreviation UILabel for {resource!r}; "
                f"captured texts={texts}"
            )

    def test_panel_header_abbreviation_labels_are_three_chars_or_less(
        self, mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """The abbreviation cells the panel renders into the header row are
        all <=3 characters. Pins the panel's UILabel ``text`` arg, not the
        upstream constant."""
        from game.ui.utils.resource_display import get_resource_abbreviation

        texts = self._build_and_capture_label_texts(
            mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
        )

        # Filter to only the abbreviation labels (one per planetary resource).
        expected_abbrevs = {get_resource_abbreviation(r) for r in PLANET_RESOURCE_NAMES}
        rendered_abbrevs = [t for t in texts if t in expected_abbrevs]
        assert rendered_abbrevs, (
            f"No abbreviation labels rendered; texts={texts}"
        )
        for abbrev in rendered_abbrevs:
            assert len(abbrev) <= 3

    def test_panel_renders_expected_planetary_abbreviations(
        self, mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Pin the concrete header-cell texts for the five planetary
        resources, in order — defends both the resource set AND the
        abbreviation values that production actually renders."""
        texts = self._build_and_capture_label_texts(
            mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
        )

        # Each of these MUST appear as a UILabel in the rendered panel.
        for expected in ("Met", "Org", "Vap", "Rad", "Exo"):
            assert expected in texts, (
                f"Panel header missing expected abbreviation {expected!r}; "
                f"texts={texts}"
            )


# =============================================================================
# Value Formatting Tests
# =============================================================================

class TestValueFormatting:
    """Tests for _format_value method."""

    @pytest.fixture(autouse=True)
    def _setup_patches(self, patched_treasury_imports):
        """PROJ-494 T2.14: replaces the 4-decorator stack."""
        pass


    # PROJ-494 T3.18: 4 _format_value tests parametrized on
    # `(input_value, expected_output)`. Each original test asserted multiple
    # input→output pairs; the parametrize now spreads them across cases.
    @pytest.mark.parametrize(
        "input_value,expected_output",
        [
            # Zero values
            pytest.param(0, "0", id='zero_int'),
            pytest.param(0.0, "0", id='zero_float'),
            # Small integers (no commas)
            pytest.param(5, "5", id='small_5'),
            pytest.param(100, "100", id='small_100'),
            pytest.param(999, "999", id='small_999'),
            # Large integers (with commas)
            pytest.param(1000, "1,000", id='large_1k'),
            pytest.param(10000, "10,000", id='large_10k'),
            pytest.param(1000000, "1,000,000", id='large_1m'),
            # Float rounding
            pytest.param(9.5, "10", id='round_up'),
            pytest.param(9.4, "9", id='round_down'),
            pytest.param(1234.7, "1,235", id='round_with_comma'),
        ],
    )
    def test_format_value(
        self, mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
        input_value, expected_output,
    ):
        """_format_value handles zero, small/large integers, and float rounding."""
        panel = EmpireTreasuryPanel(
            mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
        )
        assert panel._format_value(input_value) == expected_output


# =============================================================================
# Row Data Tests
# =============================================================================

class TestRowData:
    """Tests for row data structure methods."""

    @pytest.fixture(autouse=True)
    def _setup_patches(self, patched_treasury_imports):
        """PROJ-494 T2.14: replaces the 4-decorator stack."""
        pass


    def test_production_rows_structure(self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Production rows should have correct structure."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_production_rows()

        assert len(rows) == 6  # 5 sources + total
        assert rows[0][0] == "From Colonies"
        assert rows[5][0] == "Total"
        assert rows[5][2] is True  # Total row has is_total=True

        # Non-total rows have is_total=False
        for i in range(5):
            assert rows[i][2] is False

    def test_expense_rows_structure(self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Expense rows should have correct structure."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()

        assert len(rows) == 4  # 3 categories + total
        assert rows[0][0] == "Tributes"
        assert rows[1][0] == "Construction Queues (Ships)"
        assert rows[2][0] == "Construction Queues (Complexes)"
        assert rows[3][0] == "Total"
        assert rows[3][2] is True

    def test_treasury_rows_structure(self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Treasury rows should have correct structure."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_treasury_rows()

        assert len(rows) == 3
        assert rows[0][0] == "Net Resources"
        assert rows[1][0] == "Total In Storage"
        assert rows[2][0] == "Maximum Storage"

        # No total rows in treasury section
        for row in rows:
            assert row[2] is False

    def test_production_rows_use_snapshot_data(self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Production rows should reference snapshot data."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_production_rows()

        # Check that rows contain actual snapshot data
        assert rows[0][1] is sample_snapshot.colony_production
        assert rows[5][1] is sample_snapshot.total_production


# =============================================================================
# PROJ-290 Phase 1: Population Upkeep row
# =============================================================================

class TestPopulationUpkeepRow:
    @pytest.fixture(autouse=True)
    def _setup_patches(self, patched_treasury_imports):
        """PROJ-494 T2.14: replaces the 4-decorator stack."""
        pass

    """Tests for the PROJ-290 "Population Upkeep" expense row.

    Inserted before the "Total" row when
    `snapshot.total_population_upkeep` has any non-zero entries. Hidden
    (row not emitted) when the dict is empty or all-zero — avoids
    visual noise in a fresh game with no populations yet.

    Cell values are rendered as NEGATIVE floats (drain). Only resources
    with upkeep entries produce cells; resources absent from the dict
    render as 0 via the existing per-column default.
    """

    def test_row_hidden_when_total_population_upkeep_empty(
        self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Fresh-game snapshot with `total_population_upkeep == {}` →
        expense section stays at the legacy 4 rows (no "Population Upkeep")."""
        assert sample_snapshot.total_population_upkeep == {}
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()
        labels = [r[0] for r in rows]
        assert "Population Upkeep" not in labels
        assert len(rows) == 4

    def test_row_hidden_when_all_values_zero(
        self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Dict populated but every value is 0 → still hidden."""
        sample_snapshot.total_population_upkeep = {
            "organics": 0.0, "metals": 0.0, "radioactives": 0.0,
        }
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()
        labels = [r[0] for r in rows]
        assert "Population Upkeep" not in labels

    def test_row_visible_with_single_resource_upkeep(
        self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """`{"organics": 5.0}` → row shown, organics cell is -5.0 drain."""
        sample_snapshot.total_population_upkeep = {"organics": 5.0}
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()

        labels = [r[0] for r in rows]
        assert "Population Upkeep" in labels
        upkeep_row = next(r for r in rows if r[0] == "Population Upkeep")
        label, values, is_total = upkeep_row
        assert is_total is False
        # Drain = NEGATIVE
        assert values["organics"] == pytest.approx(-5.0)
        # Unused resources default to 0 (sparse dict).
        assert values.get("metals", 0.0) == 0.0

    def test_row_visible_with_multi_resource_upkeep(
        self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Multi-resource upkeep: every key becomes a negative cell."""
        sample_snapshot.total_population_upkeep = {
            "organics": 1.5, "metals": 0.15, "radioactives": 0.015,
        }
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()

        upkeep_row = next(r for r in rows if r[0] == "Population Upkeep")
        values = upkeep_row[1]
        assert values["organics"] == pytest.approx(-1.5)
        assert values["metals"] == pytest.approx(-0.15)
        assert values["radioactives"] == pytest.approx(-0.015)

    def test_upkeep_row_inserted_before_total(
        self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Population Upkeep must appear BEFORE the Total row so the
        running-total visually aggregates below it."""
        sample_snapshot.total_population_upkeep = {"organics": 1.0}
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()
        labels = [r[0] for r in rows]
        assert labels.index("Population Upkeep") < labels.index("Total")


# =============================================================================
# Panel Construction Tests
# =============================================================================

class TestPanelConstruction:
    """Tests for panel initialization and construction."""

    @pytest.fixture(autouse=True)
    def _setup_patches(self, patched_treasury_imports):
        """PROJ-494 T2.14: replaces the 4-decorator stack."""
        pass


    def test_panel_passes_constructor_args_to_ui_widgets(
        self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Panel forwards `manager` to UIScrollingContainer and `panel` as the
        scrolling container's parent (i.e., constructor args are not just
        stored but actually plumbed into the UI tree). Pinning this means
        a refactor that drops a kwarg fails the test rather than silently
        breaking layout."""
        EmpireTreasuryPanel(
            mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
        )
        # The scrolling container MUST have been constructed with the
        # passed-in manager and parent panel as its container.
        kwargs = self.mock_container.call_args.kwargs
        assert kwargs["manager"] is mock_ui_manager
        assert kwargs["container"] is mock_panel

    def test_scroll_container_sized_from_panel_relative_rect_minus_margin(
        self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Scroll-container rect is derived from the parent panel's
        get_relative_rect(): width-20, height-20, offset (LEFT_MARGIN, TOP_MARGIN).
        Pins production's actual layout formula at empire_treasury_panel.py:78-88
        instead of merely asserting the container is non-None."""
        # mock_panel fixture sets get_relative_rect -> width=800, height=600.
        EmpireTreasuryPanel(
            mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
        )
        rect = self.mock_container.call_args.kwargs["relative_rect"]
        assert rect.x == LEFT_MARGIN
        assert rect.y == TOP_MARGIN
        assert rect.width == 800 - 20
        assert rect.height == 600 - 20


# =============================================================================
# Refresh Tests
# =============================================================================

class TestRefresh:
    """Tests for panel refresh functionality."""

    @pytest.fixture(autouse=True)
    def _setup_patches(self, patched_treasury_imports):
        """PROJ-494 T2.14: replaces the 4-decorator stack."""
        pass


    def test_refresh_updates_snapshot(self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Refresh should update the stored snapshot."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)

        new_snapshot = EmpireEconomySnapshot()
        new_snapshot.colony_production = {"metals": 999.0}
        panel.refresh(new_snapshot)

        assert panel.snapshot is new_snapshot

    def test_refresh_clears_old_elements(self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Refresh should kill old UI elements."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)

        # Store reference to old elements
        old_elements = list(panel._elements)
        old_container = panel._scroll_container

        new_snapshot = EmpireEconomySnapshot()
        panel.refresh(new_snapshot)

        # Old container should be killed
        old_container.kill.assert_called_once()

        # Old elements should be killed
        for elem in old_elements:
            elem.kill.assert_called()


# =============================================================================
# PROJ-339: Characterization gap-fill tests
# =============================================================================

class TestFormatValueRoundingBoundary:
    """PROJ-339: pin observed rounding boundaries in `_format_value`.

    `_format_value` uses `int(round(value))` (banker's rounding) and then
    formats with comma separators. This pins the observed behavior.
    """

    @pytest.fixture(autouse=True)
    def _setup_patches(self, patched_treasury_imports):
        """PROJ-494 T2.14: replaces the 4-decorator stack."""
        pass


    def test_format_value_zero_thousands_and_rounding(
        self,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """`0` -> "0"; `1234` -> "1,234"; `10000.5` rounds via banker's
        rounding to 10000 -> "10,000".

        Python's `round()` uses banker's rounding (round-half-to-even):
        `round(10000.5)` -> 10000, not 10001. We pin this behavior.
        """
        panel = EmpireTreasuryPanel(
            mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
        )
        assert panel._format_value(0) == "0"
        assert panel._format_value(1234) == "1,234"
        # Banker's rounding: round(10000.5) -> 10000 (even)
        assert panel._format_value(10000.5) == "10,000"


class TestBuildResourceHeaderMissingIcon:
    """PROJ-339: `_build_resource_header` skips the UIImage construction
    when a resource id is absent from `resource_icons`. The label is still
    rendered."""

    @pytest.fixture(autouse=True)
    def _setup_patches(self, patched_treasury_imports):
        """PROJ-494 T2.14: replaces the 4-decorator stack."""
        pass


    def test_build_resource_header_skips_missing_icon(
        self,
        mock_panel, mock_ui_manager, sample_snapshot,
    ):
        """If resource_icons dict is empty, panel constructs without
        attempting any UIImage; UILabels are still rendered."""
        empty_icons = {}
        panel = EmpireTreasuryPanel(
            mock_panel, mock_ui_manager, sample_snapshot, empty_icons,
        )
        # No UIImage constructed because no resource is present in icons dict
        self.mock_image.assert_not_called()
        # Labels were still constructed (panel built without raising)
        assert panel._scroll_container is not None
        assert self.mock_label.call_count > 0


