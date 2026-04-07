"""
Quickstart Builder - Creates pre-configured game sessions for quick-play testing.

This module provides factory functions for creating standardized game configurations
that bypass the normal NewGameSetupScreen flow, enabling rapid iteration and testing.
"""
import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, TYPE_CHECKING

from game.strategy.engine.game_config import GameConfig, PlayerConfig, THEME_DEFAULTS
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.planet import PlanetaryFacility
from game.strategy.systems.design_library import DesignLibrary
from game.core.json_utils import load_json, save_json

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


INITIAL_COMPLEXES = [
    'qs_complex',           # Shipyard (existing)
    'qs_metals_complex',
    'qs_organics_complex',
    'qs_vapors_complex',
    'qs_radioactives_complex',
    'qs_exotics_complex',
    'qs_resupply_depot',
    'qs_geologic_stabilizer_complex',  # Geologic stabilizer + energy
]


def get_quickstart_fixtures_dir() -> Path:
    """Return the quickstart fixtures directory."""
    # Navigate from this file to project root, then to fixtures
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent  # game/strategy -> game -> StarshipBattles
    return project_root / "tests" / "fixtures" / "quickstart"


def get_quickstart_races_dir() -> Path:
    """Return the quickstart races fixtures directory."""
    return get_quickstart_fixtures_dir() / "races"


def get_quickstart_designs_dir() -> Path:
    """Return the quickstart designs fixtures directory."""
    return get_quickstart_fixtures_dir() / "designs"


class QuickstartBuilder:
    """Factory for creating pre-configured game sessions."""

    @staticmethod
    def load_test_race(race_filename: str) -> Optional[RaceConfig]:
        """
        Load a test race configuration from the quickstart fixtures.

        Args:
            race_filename: Filename (without path) of the race JSON

        Returns:
            RaceConfig if found, None otherwise
        """
        race_path = get_quickstart_races_dir() / race_filename
        if not race_path.exists():
            logger.error(f"Quickstart race not found: {race_path}")
            return None

        data = load_json(str(race_path))
        if data is None:
            logger.error(f"Failed to load quickstart race: {race_path}")
            return None

        return RaceConfig.from_dict(data)

    @staticmethod
    def build_1p_config(
        save_name_prefix: Optional[str] = None,
        galaxy_radius: int = 8000,
        system_count: int = 100,
        galaxy_type: str = "spiral"
    ) -> GameConfig:
        """
        Create a single-player quickstart configuration.

        Args:
            save_name_prefix: Optional custom prefix (default: "Quickstart_1P")
            galaxy_radius: Galaxy size (default: 8000)
            system_count: Number of star systems (default: 100)
            galaxy_type: Galaxy layout type (default: "spiral")

        Returns:
            Configured GameConfig ready for game session creation
        """
        prefix = save_name_prefix or "Quickstart_1P"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_name = f"{prefix}_{timestamp}"

        logger.info(f"Building 1P quickstart: {save_name}")

        # Try to load test race fixture
        race = QuickstartBuilder.load_test_race("test_emp1.json")

        if race:
            player = PlayerConfig(
                name=race.name,
                theme=race.theme_id,
                color=THEME_DEFAULTS[0][1],  # Federation blue
                is_human=True,
                race_id=race.race_id,
                flag_id=race.flag_id,
                portrait_id=race.portrait_id,
                race_config=race
            )
        else:
            # Fallback if fixture not found
            logger.debug("Using fallback player config (fixture not found)")
            player = PlayerConfig(
                name="TestEmp1",
                theme=THEME_DEFAULTS[0][0],
                color=THEME_DEFAULTS[0][1],
                is_human=True
            )

        return GameConfig(
            save_name=save_name,
            players=[player],
            galaxy_radius=galaxy_radius,
            system_count=system_count,
            galaxy_type=galaxy_type
        )

    @staticmethod
    def build_2p_config(
        save_name_prefix: Optional[str] = None,
        galaxy_radius: int = 8000,
        system_count: int = 100,
        galaxy_type: str = "spiral"
    ) -> GameConfig:
        """
        Create a two-player quickstart configuration.

        Args:
            save_name_prefix: Optional custom prefix (default: "Quickstart_2P")
            galaxy_radius: Galaxy size (default: 8000)
            system_count: Number of star systems (default: 100)
            galaxy_type: Galaxy layout type (default: "spiral")

        Returns:
            Configured GameConfig ready for game session creation
        """
        prefix = save_name_prefix or "Quickstart_2P"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_name = f"{prefix}_{timestamp}"

        logger.info(f"Building 2P quickstart: {save_name}")

        players = []

        # Player 1
        race1 = QuickstartBuilder.load_test_race("test_emp1.json")
        if race1:
            players.append(PlayerConfig(
                name=race1.name,
                theme=race1.theme_id,
                color=THEME_DEFAULTS[0][1],  # Federation blue
                is_human=True,
                race_id=race1.race_id,
                flag_id=race1.flag_id,
                portrait_id=race1.portrait_id,
                race_config=race1
            ))
        else:
            players.append(PlayerConfig(
                name="TestEmp1",
                theme=THEME_DEFAULTS[0][0],
                color=THEME_DEFAULTS[0][1],
                is_human=True
            ))

        # Player 2
        race2 = QuickstartBuilder.load_test_race("test_emp2.json")
        if race2:
            players.append(PlayerConfig(
                name=race2.name,
                theme=race2.theme_id,
                color=THEME_DEFAULTS[1][1],  # Atlantians teal
                is_human=True,
                race_id=race2.race_id,
                flag_id=race2.flag_id,
                portrait_id=race2.portrait_id,
                race_config=race2
            ))
        else:
            players.append(PlayerConfig(
                name="TestEmp2",
                theme=THEME_DEFAULTS[1][0],
                color=THEME_DEFAULTS[1][1],
                is_human=True
            ))

        return GameConfig(
            save_name=save_name,
            players=players,
            galaxy_radius=galaxy_radius,
            system_count=system_count,
            galaxy_type=galaxy_type
        )

    @staticmethod
    def copy_quickstart_designs(
        save_path: str,
        empire_ids: List[int],
        empire_themes: Optional[Dict[int, str]] = None
    ) -> bool:
        """
        Copy pre-made quickstart designs to a save folder.

        Args:
            save_path: Path to the save folder
            empire_ids: List of empire IDs to copy designs for
            empire_themes: Optional mapping of empire_id -> theme_id.
                If provided, each copied design's theme_id is updated
                to match the empire's theme.

        Returns:
            True if successful, False otherwise
        """
        designs_source = get_quickstart_designs_dir()
        if not designs_source.exists():
            logger.error(f"Quickstart designs directory not found: {designs_source}")
            return False

        design_files = list(designs_source.glob("*.json"))
        if not design_files:
            logger.error(f"No quickstart design files found in: {designs_source}")
            return False

        success = True
        for empire_id in empire_ids:
            dest_folder = Path(save_path) / "designs" / f"empire_{empire_id}"
            dest_folder.mkdir(parents=True, exist_ok=True)

            theme_id = empire_themes.get(empire_id) if empire_themes else None

            for design_file in design_files:
                dest_path = dest_folder / design_file.name
                try:
                    if theme_id:
                        # Copy and update theme_id in the design data
                        data = load_json(design_file)
                        if data is not None:
                            if "theme_id" in data:
                                data["theme_id"] = theme_id
                            save_json(dest_path, data, indent=4)
                    else:
                        shutil.copy2(design_file, dest_path)
                    logger.debug(f"Copied design {design_file.name} to empire_{empire_id}")
                except (OSError, PermissionError, shutil.Error) as e:
                    logger.error(f"Failed to copy design {design_file.name}: {e}")
                    success = False

        if success:
            logger.info(f"Copied {len(design_files)} designs to {len(empire_ids)} empires")

        return success

    @staticmethod
    def spawn_initial_complexes(save_path: str, session: 'GameSession') -> bool:
        """
        Spawn pre-built complexes on all home planets.

        Called after designs are copied and save_path is set.

        Args:
            save_path: Path to save folder (designs already copied here)
            session: GameSession with empires and colonies initialized

        Returns:
            True if all complexes spawned successfully
        """
        success = True

        for empire in session.empires:
            # Get home planet (first colony)
            if not empire.colonies:
                logger.warning(f"Empire {empire.id} has no colonies - skipping complex spawn")
                continue

            home_planet = empire.colonies[0]
            library = DesignLibrary(save_path, empire.id)

            for design_id in INITIAL_COMPLEXES:
                load_result = library.load_design_data(design_id)

                if not load_result.success:
                    logger.warning(f"Could not load design {design_id} for empire {empire.id}: {load_result.error}")
                    success = False
                    continue

                design_data = load_result.data
                facility = PlanetaryFacility(
                    instance_id=str(uuid.uuid4()),
                    design_id=design_id,
                    name=design_data.get("name", design_id),
                    design_data=design_data,
                    is_operational=True
                )

                home_planet.facilities.append(facility)
                logger.info(f"Spawned {facility.name} on {home_planet.name} (Empire {empire.id})")

        return success
