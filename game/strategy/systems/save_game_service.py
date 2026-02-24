"""
Save Game Service - Handles game state persistence

This service provides centralized save/load functionality for the strategy layer.
Manages save folder structure, metadata, and version compatibility.

Save Format Version 2.0.0:
- Turn-based saves: turns/turn_N.json
- Per-empire design folders: designs/empire_N/
- Strict version checking (rejects all old saves)
"""
import logging
from json import JSONDecodeError
import os
import shutil
import traceback
from datetime import datetime
from typing import Optional, Tuple, List
from game.core.json_utils import save_json, load_json_required, load_json
from game.core.paths import Paths
from game.core.exceptions import PersistenceException

logger = logging.getLogger(__name__)


class SaveGameService:
    """Manages saving and loading complete game state"""

    SAVE_VERSION = "2.0.0"

    @staticmethod
    def save_game(game_session, save_name: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Save complete game state to disk.

        Args:
            game_session: GameSession instance to save
            save_name: Optional custom save name (uses existing path or generates new)

        Returns:
            Tuple of (success: bool, message: str, save_path: str or None)
        """
        try:
            # Determine save path
            if game_session.save_path:
                # Use existing save path
                save_path = game_session.save_path
            else:
                # Create new save folder
                if save_name is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    first_player_name = game_session.config.players[0].name if game_session.config.players else "Game"
                    player_name = first_player_name.replace(" ", "_")
                    save_name = f"{player_name}_{timestamp}"

                save_path = os.path.join(Paths.SAVES_DIR, save_name)

            # Create save folder structure
            os.makedirs(save_path, exist_ok=True)

            # Create turns subfolder
            turns_folder = os.path.join(save_path, "turns")
            os.makedirs(turns_folder, exist_ok=True)

            # Create per-empire design folders
            designs_folder = os.path.join(save_path, "designs")
            os.makedirs(designs_folder, exist_ok=True)
            for empire in game_session.empires:
                empire_designs_folder = os.path.join(designs_folder, f"empire_{empire.id}")
                os.makedirs(empire_designs_folder, exist_ok=True)

            # Update game session's save_path
            game_session.save_path = save_path

            # Serialize and save game state to turn file
            game_state = game_session.to_dict()
            turn_file = os.path.join(turns_folder, f"turn_{game_session.turn_number}.json")
            if not save_json(turn_file, game_state, indent=4):
                return False, "Failed to save turn state", None

            # Create/update save metadata
            first_player_name = game_session.config.players[0].name if game_session.config.players else "Unknown"
            metadata = {
                'version': SaveGameService.SAVE_VERSION,
                'timestamp': datetime.now().isoformat(),
                'player_name': first_player_name,
                'empire_count': len(game_session.empires),
                'empire_names': [e.name for e in game_session.empires],
                'latest_turn_number': game_session.turn_number,
                'turn_number': game_session.turn_number,  # For compatibility
                'galaxy_radius': game_session.config.galaxy_radius,
                'system_count': len(game_session.systems)
            }

            metadata_path = os.path.join(save_path, "save_metadata.json")
            if not save_json(metadata_path, metadata, indent=4):
                return False, "Failed to save metadata", None

            logger.info(f"SaveGameService: Saved turn {game_session.turn_number} to {os.path.basename(save_path)}")
            return True, f"Game saved: Turn {game_session.turn_number}", save_path

        except PermissionError as e:
            logger.error(f"SaveGameService: Permission denied saving to {save_path} - {e}")
            return False, f"Save failed: Permission denied", None
        except OSError as e:
            logger.error(f"SaveGameService: OS error saving to {save_path} - {e}")
            return False, f"Save failed: {str(e)}", None
        except (TypeError, ValueError) as e:
            logger.error(f"SaveGameService: Serialization error - {e}\n{traceback.format_exc()}")
            return False, f"Save failed: Unable to serialize game state", None
        except (KeyError, AttributeError, ImportError) as e:
            logger.error(f"SaveGameService: Unexpected save error - {e}\n{traceback.format_exc()}")
            return False, f"Save failed: {str(e)}", None

    @staticmethod
    def load_game(save_path: str, turn_number: Optional[int] = None) -> Tuple[Optional[object], str]:
        """
        Load game state from save folder.

        Args:
            save_path: Path to save folder (absolute or relative)
            turn_number: Optional specific turn to load (defaults to latest)

        Returns:
            Tuple of (GameSession or None, message: str)
        """
        try:
            # Resolve path
            if not os.path.isabs(save_path):
                save_path = os.path.join(Paths.SAVES_DIR, save_path)

            # Validate save folder
            is_valid, error_msg = SaveGameService._validate_save(save_path)
            if not is_valid:
                return None, f"Invalid save: {error_msg}"

            # Load metadata
            metadata_path = os.path.join(save_path, "save_metadata.json")
            try:
                metadata = load_json_required(metadata_path)
            except JSONDecodeError as e:
                logger.error(f"SaveGameService: Corrupt metadata JSON at {metadata_path} - {e}")
                return None, f"Save file corrupted: Metadata file contains invalid JSON"
            except FileNotFoundError as e:
                logger.error(f"SaveGameService: Missing metadata at {metadata_path}")
                return None, f"Save file corrupted: Metadata file not found"
            except PermissionError as e:
                logger.error(f"SaveGameService: Permission denied reading {metadata_path}")
                return None, f"Cannot read save: Permission denied"
            except OSError as e:
                logger.error(f"SaveGameService: OS error reading metadata - {e}")
                return None, f"Save file corrupted: Cannot read metadata file"

            # Validate metadata
            required_metadata_keys = ['version', 'timestamp', 'player_name']
            missing_keys = [k for k in required_metadata_keys if k not in metadata]
            if missing_keys:
                return None, f"Save file corrupted: Missing metadata fields: {', '.join(missing_keys)}"

            # Check version compatibility
            save_version = metadata.get('version')
            if not SaveGameService._is_compatible_version(save_version):
                return None, f"Incompatible save version: {save_version} (requires {SaveGameService.SAVE_VERSION})"

            # Determine which turn to load
            if turn_number is None:
                turn_number = metadata.get('latest_turn_number', metadata.get('turn_number', 1))

            # Load turn file
            turns_folder = os.path.join(save_path, "turns")
            turn_file = os.path.join(turns_folder, f"turn_{turn_number}.json")

            if not os.path.exists(turn_file):
                return None, f"Turn {turn_number} not found in save"

            try:
                game_state = load_json_required(turn_file)
            except JSONDecodeError as e:
                logger.error(f"SaveGameService: Corrupt turn JSON at {turn_file} - {e}")
                return None, f"Save file corrupted: Turn {turn_number} contains invalid JSON"
            except FileNotFoundError as e:
                logger.error(f"SaveGameService: Missing turn file at {turn_file}")
                return None, f"Save file corrupted: Turn {turn_number} file not found"
            except PermissionError as e:
                logger.error(f"SaveGameService: Permission denied reading {turn_file}")
                return None, f"Cannot read save: Permission denied"
            except OSError as e:
                logger.error(f"SaveGameService: OS error reading turn {turn_number} - {e}")
                return None, f"Save file corrupted: Cannot read turn {turn_number}"

            # Validate game state
            required_state_keys = ['turn_number', 'config', 'galaxy', 'empires']
            missing_keys = [k for k in required_state_keys if k not in game_state]
            if missing_keys:
                return None, f"Save file corrupted: Missing game state fields: {', '.join(missing_keys)}"

            # Reconstruct GameSession
            try:
                from game.strategy.engine.game_session import GameSession
                game_session = GameSession.from_dict(game_state)
            except KeyError as e:
                logger.error(f"SaveGameService: Missing required data field '{e}' in {turn_file}")
                return None, f"Save file corrupted: Missing required data field"
            except (TypeError, ValueError) as e:
                logger.error(f"SaveGameService: Invalid data format in {turn_file} - {e}")
                return None, f"Save file corrupted: Invalid data format"
            except (AttributeError, ImportError, RuntimeError) as e:
                logger.error(f"SaveGameService: Failed to reconstruct game session from {turn_file} - {e}")
                return None, f"Save file corrupted: Failed to reconstruct game state"

            # Restore save_path reference
            game_session.save_path = save_path

            logger.info(f"SaveGameService: Loaded turn {turn_number} from {os.path.basename(save_path)}")
            return game_session, f"Game loaded: Turn {turn_number}"

        except PermissionError as e:
            logger.error(f"SaveGameService: Permission denied loading {save_path} - {e}")
            return None, f"Cannot load save: Permission denied"
        except OSError as e:
            logger.error(f"SaveGameService: OS error loading {save_path} - {e}")
            return None, f"Failed to load save: {str(e)}"
        except (KeyError, TypeError, ValueError, AttributeError, ImportError) as e:
            logger.error(f"SaveGameService: Unexpected load error from {save_path} - {e}\n{traceback.format_exc()}")
            return None, f"Unexpected error while loading save"

    @staticmethod
    def list_turns(save_path: str) -> List[dict]:
        """
        List all available turns in a save.

        Args:
            save_path: Path to save folder

        Returns:
            List of dicts with turn metadata, sorted by turn number
        """
        turns = []

        # Resolve path
        if not os.path.isabs(save_path):
            save_path = os.path.join(Paths.SAVES_DIR, save_path)

        turns_folder = os.path.join(save_path, "turns")

        if not os.path.exists(turns_folder):
            return turns

        try:
            for filename in os.listdir(turns_folder):
                if filename.startswith("turn_") and filename.endswith(".json"):
                    turn_num_str = filename[5:-5]  # Extract number from "turn_N.json"
                    try:
                        turn_number = int(turn_num_str)
                        turn_file = os.path.join(turns_folder, filename)
                        stat = os.stat(turn_file)

                        turns.append({
                            'turn_number': turn_number,
                            'filename': filename,
                            'path': turn_file,
                            'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'size': stat.st_size
                        })
                    except ValueError:
                        continue

        except PermissionError as e:
            logger.error(f"SaveGameService: Permission denied listing turns in {turns_folder}")
        except OSError as e:
            logger.error(f"SaveGameService: Error listing turns in {turns_folder} - {e}")

        # Sort by turn number
        turns.sort(key=lambda x: x['turn_number'])
        return turns

    @staticmethod
    def list_saves() -> List[dict]:
        """
        List all available save games with metadata.

        Returns:
            List of dicts containing save metadata
        """
        saves = []

        if not os.path.exists(Paths.SAVES_DIR):
            return saves

        try:
            for save_name in os.listdir(Paths.SAVES_DIR):
                save_path = os.path.join(Paths.SAVES_DIR, save_name)

                if not os.path.isdir(save_path):
                    continue

                # Try to load metadata
                metadata_path = os.path.join(save_path, "save_metadata.json")
                metadata = load_json(metadata_path)

                if metadata:
                    metadata['save_name'] = save_name
                    metadata['save_path'] = save_path
                    saves.append(metadata)

        except PermissionError as e:
            logger.error(f"SaveGameService: Permission denied listing saves in {Paths.SAVES_DIR}")
        except OSError as e:
            logger.error(f"SaveGameService: Error listing saves - {e}")

        # Sort by timestamp (newest first)
        saves.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return saves

    @staticmethod
    def delete_save(save_path: str) -> Tuple[bool, str]:
        """
        Delete a save game.

        Args:
            save_path: Path to save folder

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Resolve path
            if not os.path.isabs(save_path):
                save_path = os.path.join(Paths.SAVES_DIR, save_path)

            if not os.path.exists(save_path):
                return False, "Save not found"

            shutil.rmtree(save_path)

            logger.info(f"SaveGameService: Deleted save {os.path.basename(save_path)}")
            return True, "Save deleted successfully"

        except PermissionError as e:
            logger.error(f"SaveGameService: Permission denied deleting {save_path} - {e}")
            return False, f"Delete failed: Permission denied"
        except OSError as e:
            logger.error(f"SaveGameService: OS error deleting {save_path} - {e}")
            return False, f"Delete failed: {str(e)}"
        except shutil.Error as e:
            logger.error(f"SaveGameService: Unexpected error deleting {save_path} - {e}")
            return False, f"Delete failed: {str(e)}"

    @staticmethod
    def _validate_save(save_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate save folder structure.

        For v2.0.0: Requires turns/ folder and save_metadata.json.
        """
        if not os.path.exists(save_path):
            return False, "Save folder not found"

        if not os.path.isdir(save_path):
            return False, "Save path is not a directory"

        # Check required files
        metadata_path = os.path.join(save_path, "save_metadata.json")
        if not os.path.exists(metadata_path):
            return False, "Missing save_metadata.json"

        # Check for turns folder (v2.0.0 format)
        turns_folder = os.path.join(save_path, "turns")
        if not os.path.exists(turns_folder):
            return False, "Missing turns folder (old save format not supported)"

        return True, None

    @staticmethod
    def _is_compatible_version(save_version: Optional[str]) -> bool:
        """
        Check if save version is compatible (strict version check).

        Only accepts the exact current version. Old saves are rejected.
        """
        return save_version == SaveGameService.SAVE_VERSION

    @staticmethod
    def get_save_info(save_path: str) -> Optional[dict]:
        """
        Get metadata for a specific save.

        Args:
            save_path: Path to save folder

        Returns:
            Metadata dict or None if invalid
        """
        try:
            # Resolve path
            if not os.path.isabs(save_path):
                save_path = os.path.join(Paths.SAVES_DIR, save_path)

            metadata_path = os.path.join(save_path, "save_metadata.json")
            metadata = load_json(metadata_path)

            if metadata:
                metadata['save_name'] = os.path.basename(save_path)
                metadata['save_path'] = save_path

            return metadata

        except (PermissionError, OSError, json.JSONDecodeError) as e:
            logger.error(f"SaveGameService: Error reading save info from {save_path} - {e}")
            return None
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"SaveGameService: Unexpected error reading save info from {save_path} - {e}")
            return None
