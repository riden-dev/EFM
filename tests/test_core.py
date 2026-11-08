"""
Unit tests for EFM Core logic engine.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from efm import core


def test_sanitize_folder_name():
    # Test removing invalid Windows/POSIX characters
    raw = 'Project: "The *Best* Edit" <Episode 1> / 2026? | Test. '
    sanitized = core.sanitize_folder_name(raw)
    assert ":" not in sanitized
    assert '"' not in sanitized
    assert "*" not in sanitized
    assert "<" not in sanitized
    assert ">" not in sanitized
    assert "/" not in sanitized
    assert "?" not in sanitized
    assert "|" not in sanitized
    assert not sanitized.endswith(".")
    assert not sanitized.endswith(" ")


def test_project_scaffolding():
    with tempfile.TemporaryDirectory() as temp_dir:
        proj_path = os.path.join(temp_dir, "TestProject_20261108")
        os.makedirs(proj_path, exist_ok=True)
        concept_path = core.create_project_subfolders(proj_path)

        assert os.path.exists(concept_path)
        assert os.path.exists(os.path.join(proj_path, "Exported"))
        assert os.path.exists(os.path.join(proj_path, "Project File"))
        assert os.path.exists(os.path.join(proj_path, "Files", "Reference"))

        # Verify sorting folders inside Raw and Stock
        for folder in ["Raw", "Stock"]:
            for cat in ["Image", "Video", "Audio", "Doc"]:
                assert os.path.exists(os.path.join(proj_path, "Files", folder, cat))


def test_create_new_project():
    with tempfile.TemporaryDirectory() as temp_dir:
        success, msg, path = core.create_new_project("Commercial Ad", is_client_project=True, base_dir=temp_dir)
        assert success is True
        assert path is not None
        assert os.path.exists(path)
        assert "Commercial Ad" in os.path.basename(path)
        assert "Client Project" in path


def test_sort_files_into_subfolders():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = ["clip1.mp4", "song.wav", "poster.png", "script.docx", "unknown.xyz"]
        for fname in test_files:
            with open(os.path.join(temp_dir, fname), "w") as f:
                f.write("content")

        summary = core.sort_files_into_subfolders(temp_dir)
        assert summary["moved_count"] == 4
        assert summary["by_category"]["Video"] == 1
        assert summary["by_category"]["Audio"] == 1
        assert summary["by_category"]["Image"] == 1
        assert summary["by_category"]["Doc"] == 1

        # Check files were moved to their category subdirectories
        assert os.path.exists(os.path.join(temp_dir, "Video", "clip1.mp4"))
        assert os.path.exists(os.path.join(temp_dir, "Audio", "song.wav"))
        assert os.path.exists(os.path.join(temp_dir, "Image", "poster.png"))
        assert os.path.exists(os.path.join(temp_dir, "Doc", "script.docx"))
        # Unrecognized extension stays put
        assert os.path.exists(os.path.join(temp_dir, "unknown.xyz"))


def test_calculate_move_destination_client():
    with tempfile.TemporaryDirectory() as temp_dir:
        proj_path = os.path.join(temp_dir, "Nike_20261108")

        # Finished project-based
        valid, dest, err = core.calculate_move_destination(
            proj_path, is_client_project=True, status="finished",
            client_type="project", project_type="Video Editing", base_dir=temp_dir
        )
        assert valid is True
        assert "Project Based Clients" in dest
        assert "Video Editing" in dest

        # Finished rebound
        valid, dest, err = core.calculate_move_destination(
            proj_path, is_client_project=True, status="finished",
            client_type="rebound", rebound_folder="Nike Global", base_dir=temp_dir
        )
        assert valid is True
        assert "Rebound Clients" in dest
        assert "Nike Global" in dest

        # Ignored
        valid, dest, err = core.calculate_move_destination(
            proj_path, is_client_project=True, status="ignored", base_dir=temp_dir
        )
        assert valid is True
        assert "Ignored Project" in dest


def test_calculate_move_destination_personal():
    with tempfile.TemporaryDirectory() as temp_dir:
        proj_path = os.path.join(temp_dir, "Vlog_20261108")

        valid, dest, _ = core.calculate_move_destination(proj_path, is_client_project=False, status="learning", base_dir=temp_dir)
        assert valid is True
        assert "Learning Project" in dest

        valid, dest, _ = core.calculate_move_destination(proj_path, is_client_project=False, status="finished", base_dir=temp_dir)
        assert valid is True
        assert "Finished Project" in dest


def test_move_project_execution():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a new project
        _, _, project_path = core.create_new_project("Short Film", is_client_project=False, base_dir=temp_dir)
        assert os.path.exists(project_path)

        # Move to finished
        success, msg, final_path = core.move_project(
            project_path, is_client_project=False, status="finished", base_dir=temp_dir
        )
        assert success is True
        assert not os.path.exists(project_path)
        assert os.path.exists(final_path)
        assert "Finished Project" in final_path
