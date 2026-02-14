"""Research UI components.

PROJ-147: Moved from game/research/ui/ to game/ui/research/ to fix architecture
layer violation. The research UI now correctly lives under the UI layer.
"""
from .research_scene import ResearchTreeScene

__all__ = ['ResearchTreeScene']
