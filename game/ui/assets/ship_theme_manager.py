"""Ship-theme asset loader (PROJ-314).

Reads the canonical ``assets:`` schema from
``assets/ShipThemes/<Theme>/theme.json`` and lazy-loads skin + portrait
:class:`pygame.Surface` instances on demand.

Schema (PROJ-314)::

    {
        "schema_version": 1,
        "name": "Federation",
        "description": "...",
        "image_sizes": {
            "skin":     [2048, 2048],
            "portrait": [2048, 2048]
        },
        "assets": {
            "Battleship": {
                "skin":     "Skins/battleship.png",
                "portrait": "Portraits/battleship.png",
                "scale":    1.0
            }
        }
    }

* Keys must match :data:`game.core.ship_classes.SHIP_CLASSES_WITH_VISUAL_THEMES`
  exactly. Mismatches log a warning at discovery (the loader still
  registers what it finds — UX preference is "render most slots correctly"
  rather than reject the whole theme).
* ``portrait`` is **optional**. When absent or pointing at a missing file,
  :meth:`ShipThemeManager.get_portrait_image` returns the synthetic
  placeholder Surface (consistent with :meth:`load_image`).
* ``scale`` defaults to ``1.0``.
* ``image_sizes`` is checked at load via PIL: a mismatch logs a warning
  but does not reject the asset.
"""
from __future__ import annotations

import logging
import os
import threading
from typing import Optional, Sequence

import pygame

from game.core.json_utils import load_json
from game.core.paths import Paths
from game.core.profiling import profile_block
from game.core.ship_classes import SHIP_CLASSES_WITH_VISUAL_THEMES
from game.ui.colors import OVERLAY_FALLBACK

logger = logging.getLogger(__name__)

_default_ship_theme_manager: Optional['ShipThemeManager'] = None


class ShipThemeManager:
    """Manager for ship visual themes (PROJ-314).

    Usage::

        manager = get_default_ship_theme_manager()
        manager.initialize()
        skin = manager.load_image("Federation", "Escort")
        portrait = manager.get_portrait_image("Federation", "Escort")

    Testing:

    * :func:`set_default_ship_theme_manager` to swap the singleton.
    * :meth:`clear` to reset caches but preserve the instance.
    """

    def __init__(self) -> None:
        # Skin Surface cache: {theme_name: {ship_class: Surface}}.
        self.themes: dict[str, dict[str, pygame.Surface]] = {}
        # Per-class metadata: {theme_name: {ship_class: {skin_path, portrait_path, scale}}}.
        self.theme_data: dict[str, dict[str, dict[str, object]]] = {}
        # Bounding-rect cache: {theme_name: {ship_class: pygame.Rect}}.
        self.image_metrics: dict[str, dict[str, pygame.Rect]] = {}
        # Portrait Surface cache: {theme_name: {ship_class: Surface}}.
        self.portraits: dict[str, dict[str, pygame.Surface]] = {}
        # Per-theme metadata (description, declared image sizes).
        self.theme_metadata: dict[str, dict[str, object]] = {}

        self.default_theme = "Federation"
        self.discovery_complete = False
        self._init_lock = threading.Lock()
        self._io_lock = threading.Lock()

    # -- Lifecycle -----------------------------------------------------------

    def clear(self) -> None:
        """Reset all caches and state. Used for test isolation."""
        with self._init_lock:
            with self._io_lock:
                self.themes = {}
                self.theme_data = {}
                self.image_metrics = {}
                self.portraits = {}
                self.theme_metadata = {}
                self.discovery_complete = False
                logger.info("ShipThemeManager caches cleared.")

    def initialize(self) -> None:
        """Discover all themes from assets/ShipThemes without loading images."""
        with self._init_lock:
            if self.discovery_complete and self.theme_data:
                return  # Already initialized.

            themes_dir = Paths.SHIP_THEMES_DIR
            if not os.path.exists(themes_dir):
                logger.error("ShipThemes directory not found: %s", themes_dir)
                return

            with profile_block("Theme: Discover All"):
                self.theme_data = {}
                self.theme_metadata = {}
                for entry in os.scandir(themes_dir):
                    if entry.is_dir():
                        self._discover_theme(entry.path)

            self.discovery_complete = True
            logger.info(
                "Discovered %d ship themes: %s",
                len(self.theme_data), list(self.theme_data.keys()),
            )

    def _discover_theme(self, theme_dir: str) -> None:
        """Read theme.json and store per-class skin/portrait paths + metadata."""
        json_path = os.path.join(theme_dir, "theme.json")
        data = load_json(json_path)
        if data is None:
            return

        try:
            theme_name = data.get('name', os.path.basename(theme_dir))
            schema_version = data.get('schema_version')
            assets = data.get('assets')
            if not isinstance(assets, dict):
                logger.error(
                    "Theme %s: missing or invalid 'assets:' block (legacy "
                    "'images:' schema is no longer supported, see PROJ-314).",
                    theme_name,
                )
                return

            if schema_version is not None and schema_version != 1:
                logger.warning(
                    "Theme %s: unknown schema_version=%r — attempting to "
                    "read with current loader (forward-compat).",
                    theme_name, schema_version,
                )

            image_sizes = data.get('image_sizes', {}) or {}
            self.theme_metadata[theme_name] = {
                'description': data.get('description', ''),
                'image_sizes': image_sizes,
                'theme_dir': theme_dir,
            }

            self.theme_data[theme_name] = {}
            declared_keys = set(assets.keys())
            self._validate_declared_keys(theme_name, declared_keys)

            for ship_class, entry in assets.items():
                if not isinstance(entry, dict):
                    logger.error(
                        "Theme %s: assets[%r] is not an object (PROJ-314 schema)",
                        theme_name, ship_class,
                    )
                    continue
                skin_rel = entry.get('skin')
                portrait_rel = entry.get('portrait')
                scale = float(entry.get('scale', 1.0))

                skin_path: Optional[str] = None
                if isinstance(skin_rel, str) and skin_rel:
                    candidate = os.path.join(theme_dir, skin_rel)
                    if os.path.exists(candidate):
                        skin_path = candidate
                        self._validate_image_size(
                            candidate, image_sizes.get('skin'),
                            theme_name, ship_class, kind='skin',
                        )
                    else:
                        logger.error(
                            "Skin not found for %s/%s: %s",
                            theme_name, ship_class, skin_rel,
                        )

                portrait_path: Optional[str] = None
                if isinstance(portrait_rel, str) and portrait_rel:
                    candidate = os.path.join(theme_dir, portrait_rel)
                    if os.path.exists(candidate):
                        portrait_path = candidate
                        self._validate_image_size(
                            candidate, image_sizes.get('portrait'),
                            theme_name, ship_class, kind='portrait',
                        )
                    else:
                        logger.warning(
                            "Portrait not found for %s/%s: %s "
                            "(synthetic fallback will be used)",
                            theme_name, ship_class, portrait_rel,
                        )

                if skin_path is None:
                    # No skin = nothing to register. Portrait alone is not useful.
                    continue

                self.theme_data[theme_name][ship_class] = {
                    'skin_path': skin_path,
                    'portrait_path': portrait_path,
                    'scale': scale,
                }

        except (KeyError, TypeError, ValueError) as e:
            logger.error("Failed to discover theme %s: %s", theme_dir, e)

    @staticmethod
    def _validate_declared_keys(theme_name: str, declared: set[str]) -> None:
        """Warn on extras / missing entries against the canonical set."""
        canonical = SHIP_CLASSES_WITH_VISUAL_THEMES
        extras = declared - canonical
        missing = canonical - declared
        if extras:
            logger.warning(
                "Theme %s: theme.json declares unknown ship classes %s "
                "(not in SHIP_CLASSES_WITH_VISUAL_THEMES)",
                theme_name, sorted(extras),
            )
        if missing:
            logger.info(
                "Theme %s: theme.json missing %d canonical ship class(es): %s",
                theme_name, len(missing), sorted(missing),
            )

    @staticmethod
    def _validate_image_size(
        path: str,
        expected: Sequence[int] | None,
        theme_name: str,
        ship_class: str,
        kind: str,
    ) -> None:
        """Compare actual PNG dimensions to the declared size; warn on mismatch.

        Best-effort: PIL import failures or decode errors are swallowed
        because asset validation must never block the loader.
        """
        if expected is None:
            return
        try:
            ew, eh = int(expected[0]), int(expected[1])
        except (TypeError, ValueError, IndexError):
            return
        try:
            from PIL import Image
            with Image.open(path) as img:
                aw, ah = int(img.width), int(img.height)
        except Exception:  # Intentional broad catch: size validation is best-effort, must not block discovery.
            return
        if (aw, ah) != (ew, eh):
            logger.warning(
                "Theme %s/%s %s image_sizes mismatch: declared=%dx%d actual=%dx%d (%s)",
                theme_name, ship_class, kind, ew, eh, aw, ah, path,
            )

    # -- Skin loading --------------------------------------------------------

    def load_image(self, theme_name: str, ship_class: str) -> pygame.Surface:
        """Load (or fetch from cache) the skin Surface for a theme/ship-class.

        Returns the synthetic placeholder Surface when discovery is
        incomplete or the asset is missing. Always returns a Surface;
        never returns None.
        """
        if not self.discovery_complete:
            return self._create_fallback_image(ship_class)

        if theme_name not in self.theme_data:
            logger.debug(
                "load_image: theme %r not in theme_data (available=%s); "
                "falling back to %r",
                theme_name, list(self.theme_data.keys()), self.default_theme,
            )
            theme_name = self.default_theme

        if theme_name in self.themes and ship_class in self.themes[theme_name]:
            return self.themes[theme_name][ship_class]

        if theme_name in self.theme_data and ship_class in self.theme_data[theme_name]:
            return self._load_single_image(theme_name, ship_class)

        return self._create_fallback_image(ship_class)

    def _load_single_image(self, theme_name: str, ship_class: str) -> pygame.Surface:
        with self._io_lock:
            if theme_name in self.themes and ship_class in self.themes[theme_name]:
                return self.themes[theme_name][ship_class]

            entry = self.theme_data[theme_name][ship_class]
            path = str(entry['skin_path'])

            try:
                with profile_block(f"Theme: Lazy Load ({ship_class})"):
                    surf = pygame.image.load(path).convert_alpha()
                    self.themes.setdefault(theme_name, {})[ship_class] = surf
                    rect = surf.get_bounding_rect(min_alpha=20)
                    self.image_metrics.setdefault(theme_name, {})[ship_class] = rect
                    return surf
            except FileNotFoundError as e:
                logger.error("Lazy load failed - file not found %s: %s", path, e)
                return self._create_fallback_image(ship_class)
            except pygame.error as e:
                logger.error("Lazy load failed for %s (pygame error): %s", path, e)
                return self._create_fallback_image(ship_class)

    def get_image_metrics(
        self, theme_name: str, ship_class: str,
    ) -> Optional[pygame.Rect]:
        """Return the visible bounding rect for a ship's skin image."""
        if not self.discovery_complete:
            return None

        if theme_name not in self.theme_data:
            theme_name = self.default_theme

        with self._io_lock:
            if theme_name in self.image_metrics and ship_class in self.image_metrics[theme_name]:
                return self.image_metrics[theme_name][ship_class]

        surf = self.load_image(theme_name, ship_class)

        with self._io_lock:
            if theme_name in self.image_metrics and ship_class in self.image_metrics[theme_name]:
                return self.image_metrics[theme_name][ship_class]
            if surf:
                rect = surf.get_bounding_rect(min_alpha=1)
                self.image_metrics.setdefault(theme_name, {})[ship_class] = rect
                return rect

        return None

    def get_manual_scale(self, theme_name: str, ship_class: str) -> float:
        """Return the per-ship manual scale factor (default 1.0)."""
        if not self.discovery_complete:
            return 1.0
        if theme_name not in self.theme_data:
            theme_name = self.default_theme
        if theme_name in self.theme_data and ship_class in self.theme_data[theme_name]:
            return float(self.theme_data[theme_name][ship_class].get('scale', 1.0))
        return 1.0

    def _create_fallback_image(self, ship_class: str) -> pygame.Surface:
        """Generate a placeholder Surface with a crosshair."""
        surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(surf, OVERLAY_FALLBACK, surf.get_rect(), 2)
        pygame.draw.line(surf, OVERLAY_FALLBACK, (50, 20), (50, 80), 2)
        pygame.draw.line(surf, OVERLAY_FALLBACK, (20, 50), (80, 50), 2)
        return surf

    def get_available_themes(self) -> list[str]:
        return list(self.theme_data.keys())

    # -- Portrait loading ----------------------------------------------------

    def get_portrait_image(self, theme_name: str, ship_class: str) -> pygame.Surface:
        """Return the portrait Surface for a theme/ship-class.

        PROJ-314: this method always returns a Surface — when the theme
        or ship is unknown, or when ``portrait`` is omitted from the
        theme.json, it returns the synthetic placeholder. Callers no
        longer need to handle ``None``.
        """
        if not self.discovery_complete:
            return self._create_fallback_image(ship_class)

        if theme_name not in self.theme_data:
            logger.debug(
                "get_portrait_image: theme %r not in theme_data (available=%s); "
                "falling back to %r",
                theme_name, list(self.theme_data.keys()), self.default_theme,
            )
            theme_name = self.default_theme

        if theme_name in self.portraits and ship_class in self.portraits[theme_name]:
            return self.portraits[theme_name][ship_class]

        return self._load_portrait_image(theme_name, ship_class)

    def _load_portrait_image(self, theme_name: str, ship_class: str) -> pygame.Surface:
        with self._io_lock:
            if theme_name in self.portraits and ship_class in self.portraits[theme_name]:
                return self.portraits[theme_name][ship_class]

            ship_data = self.theme_data.get(theme_name, {}).get(ship_class)
            portrait_path = ship_data.get('portrait_path') if ship_data else None

            if not portrait_path:
                fallback = self._create_fallback_image(ship_class)
                self.portraits.setdefault(theme_name, {})[ship_class] = fallback
                return fallback

            try:
                surf = pygame.image.load(str(portrait_path)).convert_alpha()
                self.portraits.setdefault(theme_name, {})[ship_class] = surf
                return surf
            except FileNotFoundError as e:
                logger.error("Portrait file not found %s: %s", portrait_path, e)
            except pygame.error as e:
                logger.error(
                    "Failed to load portrait %s (pygame error): %s",
                    portrait_path, e,
                )

            fallback = self._create_fallback_image(ship_class)
            self.portraits.setdefault(theme_name, {})[ship_class] = fallback
            return fallback

    # -- Metadata accessors --------------------------------------------------

    def get_theme_description(self, theme_name: str) -> str:
        """Return the human-readable theme description, or empty string."""
        meta = self.theme_metadata.get(theme_name, {})
        return str(meta.get('description', ''))

    def get_skin_path(self, theme_name: str, ship_class: str) -> Optional[str]:
        """Return the absolute filesystem path to the skin PNG, if any."""
        ship_data = self.theme_data.get(theme_name, {}).get(ship_class)
        return str(ship_data['skin_path']) if ship_data and ship_data.get('skin_path') else None

    def get_portrait_path(self, theme_name: str, ship_class: str) -> Optional[str]:
        """Return the absolute filesystem path to the portrait PNG, if any."""
        ship_data = self.theme_data.get(theme_name, {}).get(ship_class)
        if not ship_data:
            return None
        portrait_path = ship_data.get('portrait_path')
        return str(portrait_path) if portrait_path else None


def get_default_ship_theme_manager() -> ShipThemeManager:
    """Return the module-level :class:`ShipThemeManager`, creating one if needed."""
    global _default_ship_theme_manager
    if _default_ship_theme_manager is None:
        _default_ship_theme_manager = ShipThemeManager()
    return _default_ship_theme_manager


def set_default_ship_theme_manager(manager: ShipThemeManager) -> None:
    """Set the module-level :class:`ShipThemeManager` singleton."""
    global _default_ship_theme_manager
    _default_ship_theme_manager = manager
