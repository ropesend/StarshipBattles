from game.ui.screens.planet_list_columns import ColumnManager

def test_method_exists():
    """Verify that get_visible_columns exists on the ColumnManager class.

    Note: Originally this method was _get_visible_columns on PlanetListWindow,
    but it was extracted to ColumnManager as part of PROJ-62 Phase 2.
    """
    assert hasattr(ColumnManager, 'get_visible_columns')
    assert callable(ColumnManager.get_visible_columns)
