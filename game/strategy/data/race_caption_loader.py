"""Visual asset caption loader (PROJ-299).

Reads pre-baked structured caption JSON sidecars produced externally by
the user (via the Gemini prompts in `Tools/captioning/prompts/`). Returns
parsed dicts or `None` when the sidecar is missing or malformed.

Sidecar locations:
- Flag:     `<assets>/images/flags/Processed/<flag_id>/<flag_id>.caption.json`
- Portrait: `<assets>/images/race_portraits/<portrait_filename>.caption.json`
- Theme:    `<assets>/images/ship_themes/<theme_id>/theme.caption.json`

Graceful degradation: missing or malformed sidecars do not raise; they
log a debug/warning and return `None`. The downstream prompt builder
substitutes a `{"note": "no visual reference"}` marker so the LLM
doesn't invent visual details.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from game.core.json_utils import load_json
from game.core.paths import Paths

logger = logging.getLogger(__name__)


class RaceCaptionLoader:
    """Stateless loader for visual-asset caption sidecars.

    Construction is cheap; reuse a single instance per session if you
    like, or construct on demand.

    Args:
        assets_dir: Override the assets directory root. Defaults to
            `game.core.paths.Paths.ASSET_DIR`. The override exists for
            tests; production should rely on the default.
    """

    def __init__(self, assets_dir: Optional[Path] = None) -> None:
        self.assets_dir: Path = (
            Path(assets_dir) if assets_dir is not None else Path(Paths.ASSET_DIR)
        )

    # -- Public API ----------------------------------------------------------

    def load_flag(self, flag_id: str) -> Optional[dict]:
        """Load the caption for a flag asset, or None on missing/malformed."""
        sidecar = (
            self.assets_dir / "images" / "flags" / "Processed"
            / flag_id / f"{flag_id}.caption.json"
        )
        return self._load(sidecar, asset_type="flag", asset_id=flag_id)

    def load_portrait(self, portrait_filename: str) -> Optional[dict]:
        """Load the caption for a race portrait, or None on missing/malformed.

        Args:
            portrait_filename: The portrait's image filename, e.g.
                "Gemini_Generated_Image_59rl4259rl4259rl.jpg".
                The sidecar lives next to it as
                "Gemini_Generated_Image_59rl4259rl4259rl.jpg.caption.json".
        """
        sidecar = (
            self.assets_dir / "images" / "race_portraits"
            / f"{portrait_filename}.caption.json"
        )
        return self._load(sidecar, asset_type="portrait", asset_id=portrait_filename)

    def load_theme(self, theme_id: str) -> Optional[dict]:
        """Load the caption for a ship theme, or None on missing/malformed."""
        sidecar = self.assets_dir / "images" / "ship_themes" / theme_id / "theme.caption.json"
        return self._load(sidecar, asset_type="theme", asset_id=theme_id)

    # -- Private -------------------------------------------------------------

    def _load(self, sidecar: Path, *, asset_type: str, asset_id: str) -> Optional[dict]:
        if not sidecar.exists():
            logger.debug(
                "No caption sidecar for %s %s at %s", asset_type, asset_id, sidecar
            )
            return None

        # load_json returns the default (None here) on JSONDecodeError,
        # FileNotFoundError, PermissionError, OSError. It logs internally.
        sentinel = object()
        data = load_json(str(sidecar), default=sentinel)
        if data is sentinel:
            logger.warning(
                "Failed to load caption sidecar for %s %s; treating as malformed",
                asset_type, asset_id,
            )
            return None

        if not isinstance(data, dict):
            logger.warning(
                "Caption sidecar for %s %s is not a JSON object; ignoring",
                asset_type, asset_id,
            )
            return None

        # Defensive minimum schema check — full validation is the
        # validator tool's job; here we just protect against obviously
        # broken sidecars (e.g., old schema, hand-edited corruption).
        if data.get("schema_version") != 1:
            logger.warning(
                "Caption sidecar for %s %s has missing/wrong schema_version "
                "(%r); ignoring", asset_type, asset_id, data.get("schema_version"),
            )
            return None

        return data


__all__ = ["RaceCaptionLoader"]
