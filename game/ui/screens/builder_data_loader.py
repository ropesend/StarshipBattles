"""
DEPRECATED: Use workshop_data_loader.py instead.
This file provides backward compatibility aliases.
"""
from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader, LoadResult

# Explicit re-exports for clarity
__all__ = ['BuilderDataLoader', 'LoadResult']
