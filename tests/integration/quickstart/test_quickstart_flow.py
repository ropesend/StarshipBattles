"""Integration tests for full quickstart flow with initial complexes."""
import pytest
import shutil
import uuid

from game.strategy.quickstart_builder import QuickstartBuilder, INITIAL_COMPLEXES
from game.strategy.engine.game_session import GameSession
from game.strategy.systems.save_game_service import SaveGameService


def _unique_save_name(prefix: str) -> str:
    """Generate a unique save name to avoid xdist parallel collisions."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestQuickstartWithComplexes:
    """Integration tests verifying quickstart creates playable scenario."""

    @pytest.fixture(scope="class")
    def full_quickstart_1p(self):
        """Run complete 1P quickstart flow including complex spawning."""
        config = QuickstartBuilder.build_1p_config(
            galaxy_radius=4000,
            system_count=5,
            save_name_prefix=_unique_save_name("QS_Test_1P"),
        )
        session = GameSession(config=config)

        success, message, save_path = SaveGameService.save_game(session, config.save_name)
        assert success, f"Save failed: {message}"

        session.save_path = save_path

        QuickstartBuilder.copy_quickstart_designs(save_path, [0])
        QuickstartBuilder.spawn_initial_complexes(save_path, session)

        yield session

        # Cleanup
        shutil.rmtree(save_path, ignore_errors=True)

    @pytest.fixture(scope="class")
    def full_quickstart_2p(self):
        """Run complete 2P quickstart flow including complex spawning."""
        config = QuickstartBuilder.build_2p_config(
            galaxy_radius=4000,
            system_count=10,
            save_name_prefix=_unique_save_name("QS_Test_2P"),
        )
        session = GameSession(config=config)

        success, message, save_path = SaveGameService.save_game(session, config.save_name)
        assert success, f"Save failed: {message}"

        session.save_path = save_path

        QuickstartBuilder.copy_quickstart_designs(save_path, [0, 1])
        QuickstartBuilder.spawn_initial_complexes(save_path, session)

        yield session

        # Cleanup
        shutil.rmtree(save_path, ignore_errors=True)

    def test_home_planet_has_eight_facilities(self, full_quickstart_1p):
        """Home planet should have exactly 8 facilities after quickstart (PROJ-237: +shield complex)."""
        session = full_quickstart_1p
        home_planet = session.empires[0].colonies[0]
        assert len(home_planet.facilities) == 8

    def test_home_planet_has_shipyard(self, full_quickstart_1p):
        """Home planet should have operational shipyard."""
        session = full_quickstart_1p
        home_planet = session.empires[0].colonies[0]
        assert home_planet.has_space_shipyard is True

    def test_home_planet_has_all_resource_harvesters(self, full_quickstart_1p):
        """Home planet should have all 5 resource harvester complexes."""
        session = full_quickstart_1p
        home_planet = session.empires[0].colonies[0]

        design_ids = {f.design_id for f in home_planet.facilities}
        assert 'qs_metals_complex' in design_ids
        assert 'qs_organics_complex' in design_ids
        assert 'qs_vapors_complex' in design_ids
        assert 'qs_radioactives_complex' in design_ids
        assert 'qs_exotics_complex' in design_ids

    def test_home_planet_has_resupply_depot(self, full_quickstart_1p):
        """Home planet should have fuel depot."""
        session = full_quickstart_1p
        home_planet = session.empires[0].colonies[0]

        design_ids = {f.design_id for f in home_planet.facilities}
        assert 'qs_resupply_depot' in design_ids

    def test_all_facilities_operational(self, full_quickstart_1p):
        """All spawned facilities should be operational."""
        session = full_quickstart_1p
        home_planet = session.empires[0].colonies[0]

        for facility in home_planet.facilities:
            assert facility.is_operational is True, (
                f"Facility {facility.design_id} is not operational"
            )

    def test_2p_both_empires_have_facilities(self, full_quickstart_2p):
        """Both empires should have 7 facilities on home planets in 2P game."""
        session = full_quickstart_2p

        for i, empire in enumerate(session.empires):
            home_planet = empire.colonies[0]
            assert len(home_planet.facilities) == 8, (
                f"Empire {i} has {len(home_planet.facilities)} facilities, expected 8"
            )
            assert home_planet.has_space_shipyard is True, (
                f"Empire {i} home planet missing shipyard"
            )

    def test_2p_both_empires_have_all_complex_types(self, full_quickstart_2p):
        """Both empires should have all complex types."""
        session = full_quickstart_2p

        for i, empire in enumerate(session.empires):
            home_planet = empire.colonies[0]
            design_ids = {f.design_id for f in home_planet.facilities}
            for expected_id in INITIAL_COMPLEXES:
                assert expected_id in design_ids, (
                    f"Empire {i} missing complex: {expected_id}"
                )

    def test_facilities_have_valid_design_data(self, full_quickstart_1p):
        """All facilities should have populated design data."""
        session = full_quickstart_1p
        home_planet = session.empires[0].colonies[0]

        for facility in home_planet.facilities:
            assert isinstance(facility.design_data, dict), (
                f"Facility {facility.design_id} has no design_data"
            )
            assert "name" in facility.design_data, (
                f"Facility {facility.design_id} missing 'name' in design_data"
            )
            assert "layers" in facility.design_data, (
                f"Facility {facility.design_id} missing 'layers' in design_data"
            )
