"""
EFM (Edit Folder Manager)
Application Entry Point
"""

import sys
from pathlib import Path

# Add 'src' to python path for clean package imports
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from efm.app import main

if __name__ == "__main__":
    main()
