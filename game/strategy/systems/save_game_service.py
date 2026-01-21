"""
Save Game Service - Handles game state persistence

This service provides centralized save/load functionality for the strategy layer.
Manages save folder structure, metadata, and version compatibility.

Save Format Version 2.0.0:
- Turn-based saves: turns/turn_N.json
- Per-empire design folders: designs/empire_N/
- Strict version checking (no backward compatibility)
"""
import os
import shutil
import tempfile
from datetime import datetime
from typing import Optional, Tuple, List
from game.core.json_utils import save_json, load_json_required, load_json
from game.core.logger import log_info, log_error, log_debug


class SaveGameService:
    """Manages saving and loading complete game state"""

    SAVE_VERSION = "2.0.0"
    DEFAULT_SAVES_FOLDER = "saves"

    # Versions that can be migrated to current version
    # The modifier system was refactored in 2.0.0, but save format is compatible
    # since modifier IDs and values are version-agnostic (stored as {"id": "xxx", "value": N})
    MIGRATABLE_VERSIONS = ["1.0.0", "1.1.0", "1.2.0", "1.9.0"]

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

                saves_folder = os.path.join(os.getcwd(), SaveGameService.DEFAULT_SAVES_FOLDER)
                save_path = os.path.join(saves_folder, save_name)

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

            # BUG-29 FIX: Do NOT migrate designs from temp folder
            # New games should start with empty design libraries
            # The temp folder migration was causing designs from other games to appear
            # SaveGameService._migrate_temp_designs(game_session, designs_folder)

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

            log_info(f"SaveGameService: Saved turn {game_session.turn_number} to {os.path.basename(save_path)}")
            return True, f"Game saved: Turn {game_session.turn_number}", save_path

        except Exception as e:
            log_error(f"SaveGameService: Save failed - {e}")
            import traceback
            traceback.print_exc()
            return False, f"Save failed: {str(e)}", None

    @staticmethod
    def _migrate_temp_designs(game_session, target_designs_folder: str):
        """
        Migrate ship designs from temp folder to save folder.

        Migrates to per-empire subfolders (designs/empire_N/).
        """
        try:
            temp_base = os.path.join(tempfile.gettempdir(), "starship_battles_temp_designs")

            # Migrate all empire designs
            for empire in game_session.empires:
                empire_id = empire.id
                temp_empire_folder = os.path.join(temp_base, f"empire_{empire_id}")
                target_empire_folder = os.path.join(target_designs_folder, f"empire_{empire_id}")

                os.makedirs(target_empire_folder, exist_ok=True)

                if os.path.exists(temp_empire_folder):
                    design_files = [f for f in os.listdir(temp_empire_folder) if f.endswith('.json')]

                    if design_files:
                        log_info(f"Migrating {len(design_files)} designs for empire {empire_id}")

                        for filename in design_files:
                            src_path = os.path.join(temp_empire_folder, filename)
                            dst_path = os.path.join(target_empire_folder, filename)

                            # Copy design file (don't move, in case save fails)
                            shutil.copy2(src_path, dst_path)
                            log_debug(f"  Migrated design: {filename}")

        except Exception as e:
            log_error(f"Failed to migrate temp designs: {e}")

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
                saves_folder = os.path.join(os.getcwd(), SaveGameService.DEFAULT_SAVES_FOLDER)
                save_path = os.path.join(saves_folder, save_path)

            # Validate save folder
            is_valid, error_msg = SaveGameService._validate_save(save_path)
            if not is_valid:
                return None, f"Invalid save: {error_msg}"

            # Load metadata
            metadata_path = os.path.join(save_path, "save_metadata.json")
            try:
                metadata = load_json_required(metadata_path)
            except Exception as e:
                log_error(f"SaveGameService: Failed to load metadata - {e}")
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

            # Log migration if loading older version
            if save_version != SaveGameService.SAVE_VERSION:
                log_info(f"SaveGameService: Migrating save from version {save_version} to {SaveGameService.SAVE_VERSION}")

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
            except Exception as e:
                log_error(f"SaveGameService: Failed to load turn {turn_number} - {e}")
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
                log_error(f"SaveGameService: Missing required data - {e}")
                return None, f"Save file corrupted: Missing required data field: {str(e)}"
            except Exception as e:
                log_error(f"SaveGameService: Failed to reconstruct game session - {e}")
                return None, f"Save file corrupted: Failed to reconstruct game state"

            # Restore save_path reference
            game_session.save_path = save_path

            log_info(f"SaveGameService: Loaded turn {turn_number} from {os.path.basename(save_path)}")
            return game_session, f"Game loaded: Turn {turn_number}"

        except Exception as e:
            log_error(f"SaveGameService: Unexpected load error - {e}")
            import traceback
            traceback.print_exc()
            return None, f"Unexpected error while loading save: {str(e)}"

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
            saves_folder = os.path.join(os.getcwd(), SaveGameService.DEFAULT_SAVES_FOLDER)
            save_path = os.path.join(saves_folder, save_path)

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

        except Exception as e:
            log_error(f"SaveGameService: Error listing turns - {e}")

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
        saves_folder = os.path.join(os.getcwd(), SaveGameService.DEFAULT_SAVES_FOLDER)

        if not os.path.exists(saves_folder):
            return saves

        try:
            for save_name in os.listdir(saves_folder):
                save_path = os.path.join(saves_folder, save_name)

                if not os.path.isdir(save_path):
                    continue

                # Try to load metadata
                metadata_path = os.path.join(save_path, "save_metadata.json")
                metadata = load_json(metadata_path)

                if metadata:
                    metadata['save_name'] = save_name
                    metadata['save_path'] = save_path
                    saves.append(metadata)

        except Exception as e:
            log_error(f"SaveGameService: Error listing saves - {e}")

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
                saves_folder = os.path.join(os.getcwd(), SaveGameService.DEFAULT_SAVES_FOLDER)
                save_path = os.path.join(saves_folder, save_path)

            if not os.path.exists(save_path):
                return False, "Save not found"

            shutil.rmtree(save_path)

            log_info(f"SaveGameService: Deleted save {os.path.basename(save_path)}")
            return True, "Save deleted successfully"

        except Exception as e:
            log_error(f"SaveGameService: Delete failed - {e}")
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
        Check if save version is compatible (current or migratable).

        Accepts current version directly, or migratable older versions
        that can be upgraded on load.
        """
        if save_version is None:
            return False

        # Current version is always compatible
        if save_version == SaveGameService.SAVE_VERSION:
            return True

        # Check if version can be migrated
        return SaveGameService._can_migrate_version(save_version)

    @staticmethod
    def _can_migrate_version(save_version: Optional[str]) -> bool:
        """
        Check if a save version can be migrated to current version.

        The modifier system refactor (V2) changed internal processing but not
        the save format - modifier IDs and values remain version-agnostic.

        Args:
            save_version: The version string from the save metadata

        Returns:
            True if this version can be migrated to current
        """
        if save_version is None:
            return False

        # Current version doesn't need migration
        if save_version == SaveGameService.SAVE_VERSION:
            return True

        # Check against known migratable versions
        return save_version in SaveGameService.MIGRATABLE_VERSIONS

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
                saves_folder = os.path.join(os.getcwd(), SaveGameService.DEFAULT_SAVES_FOLDER)
                save_path = os.path.join(saves_folder, save_path)

            metadata_path = os.path.join(save_path, "save_metadata.json")
            metadata = load_json(metadata_path)

            if metadata:
                metadata['save_name'] = os.path.basename(save_path)
                metadata['save_path'] = save_path

            return metadata

        except Exception:
            return None
