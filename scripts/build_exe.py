"""
Build script to compile EFM (Edit Folder Manager) into a standalone Windows executable.
Usage:
    python scripts/build_exe.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def build():
    # Resolve project root (one level up from scripts/)
    root_dir = Path(__file__).resolve().parent.parent
    print(f"[EFM Build] Working from repository root: {root_dir}")

    icon_ico = root_dir / "assets" / "icons" / "efm_icon.ico"
    icon_png = root_dir / "assets" / "icons" / "efm_icon.png"
    main_script = root_dir / "main.py"

    if not icon_ico.exists():
        print(f"[EFM Build Error] Icon not found at {icon_ico}")
        sys.exit(1)

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--clean",
        f"--icon={icon_ico}",
        f"--add-data={icon_ico};assets/icons",
        f"--add-data={icon_png};assets/icons",
        "--collect-all=customtkinter",
        "--name=EFM",
        str(main_script)
    ]

    print("[EFM Build] Running PyInstaller command:")
    print(" ".join(cmd))

    result = subprocess.run(cmd, cwd=str(root_dir))

    if result.returncode == 0:
        dist_exe = root_dir / "dist" / "EFM.exe"
        print(f"\n[EFM Build] SUCCESS! Executable created at:\n{dist_exe}")
        if dist_exe.exists():
            print(f"[EFM Build] File size: {dist_exe.stat().st_size / (1024 * 1024):.2f} MB")
        return True
    else:
        print(f"\n[EFM Build] PyInstaller failed with return code {result.returncode}")
        return False


if __name__ == "__main__":
    build()
