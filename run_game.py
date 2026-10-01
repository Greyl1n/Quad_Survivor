"""
Top-level game launcher for Quad Survivor: The Pixel Swarm.

This entry script:
1. Resolves and adds the 'Source' directory to sys.path so modules can import cleanly.
2. Instantiates and launches the main Game loop.
3. Supports direct terminal execution on Windows, Linux, and macOS.
"""

import sys
import os

# Add the 'Source' directory to the Python search path to resolve game modules
SOURCE_DIR = os.path.join(os.path.dirname(__file__), "Source")
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

from main import main

if __name__ == "__main__":
    # Launch the main game loop
    main()
