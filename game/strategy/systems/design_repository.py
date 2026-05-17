"""PROJ-427 Phase 1: DesignRepository (filesystem + JSON persistence).

The repository is the new home for the disk-bound responsibilities
that today live on ``DesignLibrary``:

- Folder location and creation.
- ``scan_designs()`` — list ``DesignMetadata`` for all designs on disk.
- ``save_design_data(design_id, data)`` — write a design JSON file.
- ``load_design_data(design_id)`` — read a design JSON file into a
  ``DesignLoadResult`` (shape unchanged from ``DesignLibrary``).
- ``mark_design_obsolete(design_id, is_obsolete)`` — toggle the
  metadata flag on disk.
- ``increment_built_count(design_id)`` — bump ``times_built`` on disk.
- Save-folder and temp-folder policy (per-empire subfolder layout).

Phase 1 is **additive**: no existing caller is migrated, and
``DesignLibrary`` continues to own runtime lookup + UI cache + spawn
disk reads. Phase 2 layers ``DesignCatalog`` on top; Phases 3-6 migrate
callers off ``DesignLibrary`` and eventually delete it.

The ``DesignLoadResult`` value type is imported from
``design_library`` so the shape is byte-identical to today's contract;
Phase 6 will swap the import direction once ``DesignLibrary`` goes
away.
"""
from __future__ import annotations

import glob
import logging
import os
import tempfile
from json import JSONDecodeError
from typing import List, Optional, Tuple, TYPE_CHECKING

from game.core.exceptions import ValidationException
from game.core.json_utils import load_json_required, save_json
from game.strategy.data.design_metadata import DesignMetadata
from game.strategy.systems.design_library import DesignLoadResult

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


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
        if self.designs_folder is None:
            logger.warning(
                "DesignRepository.scan_designs: designs_folder is None"
            )
            return []

        designs: List[DesignMetadata] = []
        pattern = os.path.join(self.designs_folder, "*.json")
        for filepath in glob.glob(pattern):
            try:
                design_id = os.path.splitext(os.path.basename(filepath))[0]
                metadata = DesignMetadata.from_design_file(filepath, design_id)
                designs.append(metadata)
            except JSONDecodeError as e:
                logger.error(
                    "DesignRepository.scan_designs: corrupt JSON in '%s': %s",
                    filepath, e,
                )
                continue
            except KeyError as e:
                logger.error(
                    "DesignRepository.scan_designs: missing required field "
                    "in '%s': %s",
                    filepath, e,
                )
                continue
            except (PermissionError, OSError) as e:
                logger.error(
                    "DesignRepository.scan_designs: cannot read '%s': %s",
                    filepath, e,
                )
                continue
            except ValidationException as e:
                logger.exception(
                    "DesignRepository.scan_designs: validation error loading "
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
