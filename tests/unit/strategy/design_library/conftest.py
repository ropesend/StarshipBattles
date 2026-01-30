"""
Shared fixtures for DesignLibrary tests.
"""

import pytest
import tempfile
import shutil
import os
from game.strategy.systems.design_library import DesignLibrary


@pytest.fixture
def setup_library():
    """Create temporary directory for test designs."""
    tmpdir = tempfile.mkdtemp()
    # Create per-empire folder structure (empire_id=1)
    designs_folder = os.path.join(tmpdir, "designs", "empire_1")
    os.makedirs(designs_folder)

    library = DesignLibrary(tmpdir, empire_id=1)

    yield tmpdir, designs_folder, library

    shutil.rmtree(tmpdir)


@pytest.fixture
def setup_tmpdir():
    """Create temporary directory for test designs."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)
