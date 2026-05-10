"""Controller for PlanetListWindow (PROJ-329C Phase 3).

Owns the facade-side queries the window invokes when a row is selected:
fetching the per-species ``ColonyDemographicView`` for colonized planets
(PROJ-292 H1) and dispatching the navigate callback when the user clicks
"Navigate to Planet".

The controller does NOT touch ``pygame_gui`` widgets. Widget construction
lives in ``PlanetListUiBuilder`` (in the screen module). The controller
is constructed in Stage 1 of the screen ``__init__`` (cheap; no facade
I/O), and its query methods are called from event handlers / the builder
during Stage 3 and beyond.

Pattern reference: PROJ-328 Phase C ``transfer_controller.py``.
"""
from __future__ import annotations

from typing import Any, Optional


class PlanetListController:
    """Facade-coupled queries + navigate dispatch for PlanetListWindow.

    The window calls ``resolve_demographic_view(planet)`` from
    ``_on_planet_selected`` to thread PROJ-292's colonized-context
    ``view=`` kwarg into ``PlanetReportPanel``. ``navigate_to(location)``
    invokes the optional ``on_navigate_callback`` registered by the
    registrar.
    """

    def __init__(self, facade=None, on_navigate_callback=None) -> None:
        self.facade = facade
        self.on_navigate_callback = on_navigate_callback

    def resolve_demographic_view(self, planet) -> Optional[Any]:
        """Return ``ColonyDemographicView`` for a colonized planet, or
        ``None`` for uncolonized / no-facade fallback (PROJ-292 H1)."""
        if planet.owner_id is None or self.facade is None:
            return None
        return self.facade.get_colony_demographic_view(planet.id)

    def navigate_to(self, location) -> None:
        """Fire the navigate callback if registered."""
        if self.on_navigate_callback is not None:
            self.on_navigate_callback(location)


__all__ = ["PlanetListController"]
