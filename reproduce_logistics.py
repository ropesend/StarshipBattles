import sys
import os
import traceback

# Add parent dir to path
sys.path.append(os.getcwd())

# Ensure headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()

from tests.repro_issues.test_bug_05_logistics import test_missing_logistics_details

def run_repro():
    try:
        print("Running test_missing_logistics_details...")
        test_missing_logistics_details()
        print("Passed!")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    run_repro()
