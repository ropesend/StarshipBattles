from game.ui.screens.planet_list_window import PlanetListWindow

def test_method_exists():
    """Verify that _get_visible_columns exists on the class."""
    assert hasattr(PlanetListWindow, '_get_visible_columns')
    assert callable(PlanetListWindow._get_visible_columns)
