"""Formation editor components.

This package contains extracted components from the FormationEditorScene:
- FormationRenderer: Handles all rendering (grid, arrows, selection, handles)
- FormationInputHandler: Manages event handling state machine
"""

from game.ui.screens.formation.renderer import FormationRenderer
from game.ui.screens.formation.input_handler import FormationInputHandler

__all__ = ['FormationRenderer', 'FormationInputHandler']
