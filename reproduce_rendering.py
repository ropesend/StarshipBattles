import unittest
import sys
import os
import pygame
import traceback

# Add parent dir to path
sys.path.append(os.getcwd())

# Ensure headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from tests.unit.test_rendering_logic import TestRenderingLogic

def run_repro():
    try:
        test = TestRenderingLogic()
        test.setUp()
        print("Running test_component_color_coding...")
        test.test_component_color_coding()
        print("Passed!")
        test.tearDown()
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    run_repro()
