"""
EFM (Edit Folder Manager)
Backward-compatibility entrypoint shim.
Recommended modern execution: python main.py
"""

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from efm.app import main, EFMApp

if __name__ == "__main__":
    main()
