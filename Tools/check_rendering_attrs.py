
import sys
import os
sys.path.append(os.getcwd())
import rendering
print(f"Has pygame? {'pygame' in dir(rendering)}")
print(f"pygame type: {type(rendering.pygame)}")
