"""
Save Game Service - Handles game state persistence

This service provides centralized save/load functionality for the strategy layer.
Manages save folder structure, metadata, and version compatibility.
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

    SAVE_VERSION = "1.0.0"
    DEFAULT_SAVES_FOLDER = "saves"

    @staticmethod
    def save_game(game_session, save_name: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Save complete game state to disk.

        Args:
            game_session: GameSession instance to save
            save_name: Optional custom save name (uses timestamp if None)

        Returns:
            Tuple of (success: bool, message: str, save_path: str or None)
        """
        try:
            # Generate save folder name
            if save_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                player_name = game_session.config.player_name.replace(" ", "_")
                save_name = f"{player_name}_{timestamp}"

            # Create save folder structure
            saves_folder = os.path.join(os.getcwd(), SaveGameService.DEFAULT_SAVES_FOLDER)
            save_path = os.path.join(saves_folder, save_name)

            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)

            # Create designs subfolder
            designs_folder = os.path.join(save_path, "designs")
            os.makedirs(designs_folder, exist_ok=True)

            # Migrate designs from temp folder if this is the first save
            SaveGameService._migrate_temp_designs(game_session, designs_folder)

            # Update game session's save_path
            game_session.save_path = save_path

            # Create save metadata
            metadata = {
                'version': SaveGameService.SAVE_VERSION,
                'timestamp': datetime.now().isoformat(),
                'player_name': game_session.config.player_name,
                'turn_number': game_session.turn_number,
                'galaxy_radius': game_session.config.galaxy_radius,
                'system_count': len(game_session.systems)
            }

            # Save metadata
            metadata_path = os.path.join(save_path, "save_metadata.json")
            if not save_json(metadata_path, metadata, indent=4):
                return False, "Failed to save metadata", None

            # Serialize and save game state
            game_state = game_session.to_dict()
            state_path = os.path.join(save_path, "game_state.json")
            if not save_json(state_path, game_state, indent=4):
                return False, "Failed to save game state", None

            log_info(f"SaveGameService: Saved game to {save_name}")
            return True, f"Game saved successfully: {save_name}", save_path

        except Exception as e:
            log_error(f"SaveGameService: Save failed - {e}")
            return False, f"Save failed: {str(e)}", None

    @staticmethod
    def _migrate_temp_designs(game_session, target_designs_folder: str):
        """
        Migrate ship designs from temp folder to save folder.

        This is called during the first save to move designs that were created
        before the game was saved from the temporary storage to the permanent save folder.

        Args:
            game_session: GameSession with empire information
            target_designs_folder: Path to the save's designs folder
        """
        try:
            # Get temp folder path for each empire
            temp_base = os.path.join(tempfile.gettempdir(), "starship_battles_temp_designs")

            # Migrate player empire designs
            if hasattr(game_session, 'player_empire'):
                empire_id = game_session.player_empire.id
                temp_empire_folder = os.path.join(temp_base, f"empire_{empire_id}")

                if os.path.exists(temp_empire_folder):
                    # Copy all design files from temp to save folder
                    design_files = [f for f in os.listdir(temp_empire_folder) if f.endswith('.json')]

                    if design_files:
                        log_info(f"Migrating {len(design_files)} designs from temp folder to save folder")

                        for filename in design_files:
                            src_path = os.path.join(temp_empire_folder, filename)
                            dst_path = os.path.join(target_designs_folder, filename)

                            # Copy design file (don't move, in case save fails)
                            shutil.copy2(src_path, dst_path)
                            log_debug(f"  Migrated design: {filename}")

                        log_info("Design migration complete")

            # Migrate enemy empire designs (if needed for multiplayer)
            if hasattr(game_session, 'enemy_empire'):
                empire_id = game_session.enemy_empire.id
                temp_empire_folder = os.path.join(temp_base, f"empire_{empire_id}")

                if os.path.exists(temp_empire_folder):
                    design_files = [f for f in os.listdir(temp_empire_folder) if f.endswith('.json')]

                    if design_files:
                        log_info(f"Migrating {len(design_files)} enemy designs from temp folder")

                        for filename in design_files:
                            src_path = os.path.join(temp_empire_folder, filename)
                            dst_path = os.path.join(target_designs_folder, filename)

                            # Only copy if not already exists (avoid conflicts)
                            if not os.path.exists(dst_path):
                                shutil.copy2(src_path, dst_path)
                                log_debug(f"  Migrated enemy design: {filename}")

        except Exception as e:
            # Don't fail the save if migration fails - designs are still in temp folder
            log_error(f"Failed to migrate temp designs: {e}")

    @staticmethod
    def load_game(save_path: str) -> Tuple[Optional[object], str]:
        """
        Load game state from save folder.

        Args:
            save_path: Path to save folder (absolute or relative)

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

            # Load metadata with error handling
            metadata_path = os.path.join(save_path, "save_metadata.json")
            try:
                metadata = load_json_required(metadata_path)
            except Exception as e:
                log_error(f"SaveGameService: Failed to load metadata - {e}")
                return None, f"Save file corrupted: Cannot read metadata file"

            # Validate metadata structure
            required_metadata_keys = ['version', 'timestamp', 'player_name', 'turn_number']
            missing_keys = [k for k in required_metadata_keys if k not in metadata]
            if missing_keys:
                return None, f"Save file corrupted: Missing metadata fields: {', '.join(missing_keys)}"

            # Check version compatibility
            save_version = metadata.get('version')
            if not SaveGameService._is_compatible_version(save_version):
                return None, f"Incompatible save version: {save_version} (current version: {SaveGameService.SAVE_VERSION})"

            # Load game state with error handling
            state_path = os.path.join(save_path, "game_state.json")
            try:
                game_state = load_json_required(state_path)
            except Exception as e:
                log_error(f"SaveGameService: Failed to load game state - {e}")
                return None, f"Save file corrupted: Cannot read game state file"

            # Validate game state structure
            required_state_keys = ['turn_number', 'config', 'galaxy', 'empires']
            missing_keys = [k for k in required_state_keys if k not in game_state]
            if missing_keys:
                return None, f"Save file corrupted: Missing game state fields: {', '.join(missing_keys)}"

            # Reconstruct GameSession
            try:
                from game.strategy.engine.game_session import GameSession
                game_session = GameSession.from_dict(game_state)
            except KeyError as e:
                log_error(f"SaveGameService: Missing required data during reconstruction - {e}")
                return None, f"Save file corrupted: Missing required data field: {str(e)}"
            except Exception as e:
                log_error(f"SaveGameService: Failed to reconstruct game session - {e}")
                return None, f"Save file corrupted: Failed to reconstruct game state"

            # Restore save_path reference
            game_session.save_path = save_path

            log_info(f"SaveGameService: Loaded game from {os.path.basename(save_path)}")
            turn = metadata.get('turn_number', 1)
            return game_session, f"Game loaded: Turn {turn}"

        except Exception as e:
            log_error(f"SaveGameService: Unexpected load error - {e}")
            import traceback
            traceback.print_exc()
            return None, f"Unexpected error while loading save: {str(e)}"

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

            # Delete folder and all contents
            import shutil
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

        Args:
            save_path: Path to save folder

        Returns:
            Tuple of (is_valid: bool, error_message: str or None)
        """
        if not os.path.exists(save_path):
            return False, "Save folder not found"

        if not os.path.isdir(save_path):
            return False, "Save path is not a directory"

        # Check required files
        metadata_path = os.path.join(save_path, "save_metadata.json")
        if not os.path.exists(metadata_path):
            return False, "Missing save_metadata.json"

        state_path = os.path.join(save_path, "game_state.json")
        if not os.path.exists(state_path):
            return False, "Missing game_state.json"

        return True, None

    @staticmethod
    def _is_compatible_version(save_version: Optional[str]) -> bool:
        """
        Check if save version is compatible with current version.

        Args:
            save_version: Version string from save file

        Returns:
            True if compatible, False otherwise
        """
        if save_version is None:
            return False

        # For now, only accept exact version match
        # Future: implement semantic versioning compatibility
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
