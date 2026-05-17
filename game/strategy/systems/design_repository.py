"""PROJ-427 Phase 1: DesignRepository (filesystem + JSON persistence).

The repository is the new home for the disk-bound responsibilities
that today live on ``DesignLibrary``:

- Folder location and creation.
- ``scan_designs()`` — list ``DesignMetadata`` for all designs on disk.
- ``save_design_data(design_id, data)`` — write a design JSON file.
- ``load_design_data(design_id)`` — read a design JSON file into a
  ``DesignLoadResult`` (shape unchanged).
- ``mark_design_obsolete(design_id, is_obsolete)`` — toggle the
  metadata flag on disk.
- ``increment_built_count(design_id)`` — bump ``times_built`` on disk.
- Save-folder and temp-folder policy (per-empire subfolder layout).

PROJ-427 Phase 6: ``DesignLoadResult`` was relocated from
``design_library`` to this module so the dependency direction inverts
in preparation for ``DesignLibrary`` deletion. ``design_library`` now
re-exports the value type for backwards compatibility during the
in-flight UI migration; callers should import it from
``game.strategy.systems.design_repository`` going forward.
"""
from __future__ import annotations

import glob
import logging
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from json import JSONDecodeError
from typing import Any, List, Optional, Set, Tuple, TYPE_CHECKING

from game.core.exceptions import ValidationException
from game.core.json_utils import load_json_required, save_json
from game.core.string_utils import slugify
from game.strategy.data.design_metadata import DesignMetadata

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DesignLoadResult:
    """Result of attempting to load a ship design.

    PROJ-251: Replaces bare Optional[dict] return so callers can distinguish
    between not-found, corrupt JSON, invalid schema, and permission errors.
    PROJ-427 Phase 6: relocated from ``design_library`` to this module; the
    legacy ``design_library`` location re-exports for backwards compatibility.
    """
    data: Optional[dict] = None
    error: Optional[str] = None
    error_type: Optional[str] = None

    @property
    def success(self) -> bool:
        """True if design was loaded successfully."""
        return self.data is not None

    @staticmethod
    def ok(data: dict) -> "DesignLoadResult":
        return DesignLoadResult(data=data)

    @staticmethod
    def not_found(design_id: str) -> "DesignLoadResult":
        return DesignLoadResult(
            error=f"Design '{design_id}' not found",
            error_type="not_found",
        )

    @staticmethod
    def corrupt(design_id: str, detail: str) -> "DesignLoadResult":
        return DesignLoadResult(
            error=f"Design '{design_id}' has corrupt JSON: {detail}",
            error_type="corrupt_json",
        )

    @staticmethod
    def invalid_schema(design_id: str, detail: str) -> "DesignLoadResult":
        return DesignLoadResult(
            error=f"Design '{design_id}' has invalid schema: {detail}",
            error_type="invalid_schema",
        )

    @staticmethod
    def permission_denied(design_id: str, detail: str) -> "DesignLoadResult":
        return DesignLoadResult(
            error=f"Design '{design_id}' permission denied: {detail}",
            error_type="permission_denied",
        )

    @staticmethod
    def io_error(design_id: str, detail: str) -> "DesignLoadResult":
        return DesignLoadResult(
            error=f"Design '{design_id}' IO error: {detail}",
            error_type="io_error",
        )


class DesignRepository:
    """Filesystem + JSON persistence for ship designs.

    Owns the per-empire ``designs/empire_<id>/`` folder, creation
    policy, JSON read/write, and disk-side metadata mutations
    (``mark_design_obsolete``, ``increment_built_count``).

    Constructed once per session and threaded into ``DesignCatalog``
    (Phase 2) and into the save-time flush in ``SaveGameService``
    (Phase 5). Not reachable from runtime production spawn paths after
    Phase 3.
    """

    def __init__(self, savegame_path: Optional[str], empire_id: int) -> None:
        """Initialize the repository.

        Args:
            savegame_path: Path to the savegame directory, or ``None``
                for the standalone Workshop (temp-folder) mode.
            empire_id: ID of the empire whose designs this repository
                owns.
        """
        self.savegame_path = savegame_path
        self.empire_id = empire_id

        if isinstance(savegame_path, str) and savegame_path != "":
            self.designs_folder = os.path.join(
                savegame_path, "designs", f"empire_{empire_id}"
            )
        else:
            temp_base = os.path.join(
                tempfile.gettempdir(), "starship_battles_temp_designs"
            )
            self.designs_folder = os.path.join(temp_base, f"empire_{empire_id}")

        try:
            os.makedirs(self.designs_folder, exist_ok=True)
        except PermissionError as e:
            logger.error(
                "DesignRepository: permission denied creating designs folder "
                "'%s' for empire_%d: %s",
                self.designs_folder, empire_id, e,
            )
        except OSError as e:
            logger.error(
                "DesignRepository: OS error creating designs folder '%s' for "
                "empire_%d: %s",
                self.designs_folder, empire_id, e,
            )
            # Mirror DesignLibrary's fallback to a temp folder if the
            # primary save folder is unwritable.
            temp_base = os.path.join(
                tempfile.gettempdir(), "starship_battles_temp_designs"
            )
            self.designs_folder = os.path.join(temp_base, f"empire_{empire_id}")
            os.makedirs(self.designs_folder, exist_ok=True)

    # ------------------------------------------------------------------
    # scan
    # ------------------------------------------------------------------

    def scan_designs(self) -> List[DesignMetadata]:
        """Scan the designs folder and return ``DesignMetadata`` for each
        design file.

        Returns:
            List of ``DesignMetadata`` objects. Empty if the folder is
            missing or contains no valid designs. Corrupt / unreadable
            files are skipped and logged, matching ``DesignLibrary``
            today.
        """
        return [m for m, _ in self.scan_designs_with_data()]

    def scan_designs_with_data(self) -> List[Tuple[DesignMetadata, dict]]:
        """Scan the designs folder and return ``(metadata, data)`` pairs.

        PROJ-427 Phase 2: a single pass that yields both the lightweight
        ``DesignMetadata`` and the full design data dict per file, so the
        catalog's ``repopulate_from`` boundary can seed both views without
        reading each file twice.
        """
        if self.designs_folder is None:
            logger.warning(
                "DesignRepository.scan_designs_with_data: designs_folder is None"
            )
            return []

        designs: List[Tuple[DesignMetadata, dict]] = []
        pattern = os.path.join(self.designs_folder, "*.json")
        for filepath in glob.glob(pattern):
            try:
                design_id = os.path.splitext(os.path.basename(filepath))[0]
                data = load_json_required(filepath)
                stat = os.stat(filepath)
                from datetime import datetime as _dt
                created_date = _dt.fromtimestamp(stat.st_ctime).isoformat()
                last_modified = _dt.fromtimestamp(stat.st_mtime).isoformat()
                metadata = DesignMetadata.from_design_data(
                    data, design_id,
                    created_date=created_date, last_modified=last_modified,
                )
                designs.append((metadata, data))
            except JSONDecodeError as e:
                logger.error(
                    "DesignRepository.scan_designs_with_data: corrupt JSON in '%s': %s",
                    filepath, e,
                )
                continue
            except KeyError as e:
                logger.error(
                    "DesignRepository.scan_designs_with_data: missing required field "
                    "in '%s': %s",
                    filepath, e,
                )
                continue
            except (PermissionError, OSError) as e:
                logger.error(
                    "DesignRepository.scan_designs_with_data: cannot read '%s': %s",
                    filepath, e,
                )
                continue
            except ValidationException as e:
                logger.exception(
                    "DesignRepository.scan_designs_with_data: validation error loading "
                    "'%s': %s",
                    filepath, e,
                )
                continue
        return designs

    # ------------------------------------------------------------------
    # save
    # ------------------------------------------------------------------

    def save_design_data(self, design_id: str, data: dict) -> Tuple[bool, str]:
        """Persist raw design data to disk.

        Phase 1 splits the disk-write from the rich
        ``DesignLibrary.save_design`` flow (which embeds metadata,
        guards against overwriting built designs, and invalidates the
        UI cache). The repository owns only the disk-write step; the
        higher-level workshop-save flow stays on ``DesignLibrary``
        until Phase 6 migrates it.

        Args:
            design_id: Slugified design ID (filename without
                extension).
            data: Design payload dict to write.

        Returns:
            ``(success, message)`` tuple.
        """
        if self.designs_folder is None:
            return False, "Repository not initialized"

        filepath = os.path.join(self.designs_folder, f"{design_id}.json")
        try:
            save_json(filepath, data, indent=4)
            return True, f"Saved design data: {design_id}"
        except PermissionError as e:
            logger.error(
                "DesignRepository.save_design_data: permission denied "
                "writing '%s': %s",
                filepath, e,
            )
            return False, "Failed to save design: Permission denied"
        except OSError as e:
            logger.error(
                "DesignRepository.save_design_data: OS error writing '%s': %s",
                filepath, e,
            )
            return False, f"Failed to save design: {e}"

    # ------------------------------------------------------------------
    # load
    # ------------------------------------------------------------------

    def load_design_data(self, design_id: str) -> DesignLoadResult:
        """Load raw design data from disk.

        Returns:
            ``DesignLoadResult`` with the same shape ``DesignLibrary``
            returns today. ``not_found`` / ``corrupt_json`` /
            ``permission_denied`` / ``io_error`` tokens are byte-
            identical.
        """
        if self.designs_folder is None:
            return DesignLoadResult.not_found(design_id)

        filepath = os.path.join(self.designs_folder, f"{design_id}.json")
        if not os.path.exists(filepath):
            return DesignLoadResult.not_found(design_id)

        try:
            data = load_json_required(filepath)
            return DesignLoadResult.ok(data)
        except JSONDecodeError as e:
            logger.warning(
                "DesignRepository.load_design_data: corrupt JSON for '%s' "
                "at '%s': %s",
                design_id, filepath, e,
            )
            return DesignLoadResult.corrupt(design_id, str(e))
        except PermissionError as e:
            logger.error(
                "DesignRepository.load_design_data: permission denied for "
                "'%s' at '%s': %s",
                design_id, filepath, e,
            )
            return DesignLoadResult.permission_denied(design_id, str(e))
        except OSError as e:
            logger.error(
                "DesignRepository.load_design_data: IO error for '%s' at "
                "'%s': %s",
                design_id, filepath, e,
            )
            return DesignLoadResult.io_error(design_id, str(e))

    # ------------------------------------------------------------------
    # metadata mutations
    # ------------------------------------------------------------------

    def mark_design_obsolete(
        self, design_id: str, is_obsolete: bool
    ) -> Tuple[bool, str]:
        """Toggle the ``_metadata.is_obsolete`` flag on disk."""
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")
        if not os.path.exists(filepath):
            return False, f"Design not found: {design_id}"

        try:
            data = load_json_required(filepath)
            metadata_dict = data.get("_metadata", {})
            metadata_dict["is_obsolete"] = is_obsolete
            data["_metadata"] = metadata_dict
            save_json(filepath, data, indent=4)
            status = "obsolete" if is_obsolete else "active"
            return True, f"Marked design as {status}"
        except JSONDecodeError:
            return False, "Design file is corrupted"
        except (PermissionError, OSError) as e:
            return False, f"Failed to update design: {e}"
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            logger.error(
                "DesignRepository.mark_design_obsolete: unexpected error for "
                "'%s': %s",
                design_id, e,
            )
            return False, f"Failed to update design: {e}"

    # ------------------------------------------------------------------
    # UI-facing methods (PROJ-434 Phase 0) — parity with DesignLibrary
    # ------------------------------------------------------------------

    def get_design_path(self, design_id: str) -> str:
        """Return the full path to ``<design_id>.json``.

        Mirrors ``DesignLibrary.get_design_path``. Used by
        ``BuildQueuePortraitLoader`` for portrait cache keying.
        """
        return os.path.join(self.designs_folder, f"{design_id}.json")

    def has_design(self, design_id: str) -> bool:
        """Return ``True`` if the design file exists on disk."""
        return os.path.exists(self.get_design_path(design_id))

    @staticmethod
    def _sanitize_design_id(name: str) -> str:
        """Convert a design name to a safe filename slug.

        Mirrors ``DesignLibrary._sanitize_design_id`` byte-for-byte.
        """
        result = slugify(name)
        return result if result else "unnamed_design"

    def save_design(
        self, ship: Any, design_name: str, built_designs: Set[str]
    ) -> Tuple[bool, str]:
        """Rich workshop-save flow (metadata embedding + overwrite guard).

        Parity contract with ``DesignLibrary.save_design``:

        - Returns ``(success, message)``.
        - Refuses to overwrite a design whose slug is in
          ``built_designs`` (the design has been built in-game).
        - Preserves ``created_date`` / ``times_built`` / ``is_obsolete``
          from the existing on-disk metadata when updating.
        - Embeds the fresh metadata via
          ``DesignMetadata.embed_in_ship_data``.

        Does NOT touch any catalog cache — that's the catalog wrapper's
        responsibility (``DesignCatalog.save_design`` delegates here
        then calls ``upsert_design`` / ``invalidate``).
        """
        if self.designs_folder is None:
            return False, "Design repository not properly initialized"

        design_id = self._sanitize_design_id(design_name)
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")

        if os.path.exists(filepath) and design_id in built_designs:
            return (
                False,
                f"Cannot overwrite '{design_name}' - this design has "
                "been built in-game",
            )

        try:
            metadata = DesignMetadata.from_ship(ship, design_id)

            if os.path.exists(filepath):
                old_data = load_json_required(filepath)
                old_metadata = old_data.get("_metadata", {})
                metadata.created_date = old_metadata.get(
                    "created_date", metadata.created_date
                )
                metadata.times_built = old_metadata.get("times_built", 0)
                metadata.is_obsolete = old_metadata.get("is_obsolete", False)

            metadata.last_modified = datetime.now().isoformat()

            ship_data = ship.to_dict()
            ship_data = metadata.embed_in_ship_data(ship_data)

            save_json(filepath, ship_data, indent=4)
            return True, f"Saved design: {design_name}"
        except PermissionError as e:
            logger.error(
                "DesignRepository.save_design: permission denied "
                "writing '%s': %s",
                filepath, e,
            )
            return False, "Failed to save design: Permission denied"
        except OSError as e:
            logger.error(
                "DesignRepository.save_design: OS error writing '%s': %s",
                filepath, e,
            )
            return False, f"Failed to save design: {e}"
        except ValidationException as e:
            logger.exception(
                "DesignRepository.save_design: serialization error for "
                "'%s': %s",
                design_name, e,
            )
            return False, "Failed to save design: Invalid design data"
        except (AttributeError, KeyError) as e:
            logger.exception(
                "DesignRepository.save_design: unexpected error for "
                "'%s': %s",
                design_name, e,
            )
            return False, f"Failed to save design: {e}"

    def mark_obsolete(
        self, design_id: str, is_obsolete: bool
    ) -> Tuple[bool, str]:
        """UI-facing alias for :meth:`mark_design_obsolete`.

        ``DesignLibrary`` callers used ``library.mark_obsolete(id, flag)``;
        the lower-level method on the repository is named
        ``mark_design_obsolete`` to keep the disk-mutation verb obvious.
        Both expose the same contract.
        """
        return self.mark_design_obsolete(design_id, is_obsolete)

    def increment_built_count(self, design_id: str) -> bool:
        """Bump ``_metadata.times_built`` by one and persist to disk.

        Returns ``True`` on success, ``False`` on any failure path
        (logged). Matches ``DesignLibrary.increment_built_count``
        byte-for-byte.
        """
        filepath = os.path.join(self.designs_folder, f"{design_id}.json")
        if not os.path.exists(filepath):
            return False

        try:
            data = load_json_required(filepath)
            metadata_dict = data.get("_metadata", {})
            metadata_dict["times_built"] = (
                metadata_dict.get("times_built", 0) + 1
            )
            data["_metadata"] = metadata_dict
            save_json(filepath, data, indent=4)
            return True
        except JSONDecodeError as e:
            logger.warning(
                "DesignRepository.increment_built_count: corrupt JSON for "
                "'%s': %s",
                design_id, e,
            )
            return False
        except (PermissionError, OSError) as e:
            logger.warning(
                "DesignRepository.increment_built_count: cannot update "
                "'%s': %s",
                design_id, e,
            )
            return False
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            logger.warning(
                "DesignRepository.increment_built_count: unexpected error "
                "for '%s': %s",
                design_id, e,
            )
            return False
