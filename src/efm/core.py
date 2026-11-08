"""
EFM (Edit Folder Manager) - Core Logic Module
Handles project scaffolding, folder management, file sorting, and configuration.
"""

import os
import sys
import shutil
import subprocess
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

CONFIG_FILE_NAME = "efm_config.json"


def load_dotenv_if_present(dotenv_path: Optional[Path] = None) -> None:
    """Lightweight .env loader that runs without requiring third-party libraries."""
    if dotenv_path is None:
        dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if Path(dotenv_path).exists():
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val
        except Exception:
            pass


# Execute dotenv loading on module initialization
load_dotenv_if_present()


def get_default_base_dir() -> str:
    """Returns the default base directory from environment or user documents."""
    env_dir = os.environ.get("EFM_BASE_DIR")
    if env_dir:
        return env_dir
    try:
        docs = Path.home() / "Documents" / "EFM_Projects"
        return str(docs)
    except Exception:
        return os.path.abspath("EFM_Projects")


FILE_EXTENSIONS: Dict[str, List[str]] = {
    'Image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.webp', '.svg', '.psd', '.ai'],
    'Video': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.m4v', '.flv', '.webm', '.m2ts', '.mts'],
    'Audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma', '.aiff', '.alac'],
    'Doc': ['.pdf', '.docx', '.txt', '.pptx', '.xlsx', '.doc', '.rtf', '.csv', '.prproj', '.aep', '.blend']
}

PROJECT_TYPES: List[str] = [
    'Animation',
    'Video Editing',
    'Image Editing',
    'Graphics Design',
    'Whole Package'
]


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource.
    Resolves correctly for:
      - PyInstaller standalone binary (_MEIPASS)
      - Package source layout (src/efm/...)
      - Assets directory layout (assets/icons/...)
    """
    # 1. Check PyInstaller temp directory
    try:
        base_path = Path(sys._MEIPASS)
        bundled_direct = base_path / relative_path
        if bundled_direct.exists():
            return bundled_direct
        # Also check root of _MEIPASS by filename
        filename = Path(relative_path).name
        if (base_path / filename).exists():
            return base_path / filename
    except Exception:
        pass

    # 2. Check relative to root directory (src/efm/ -> 3 levels up)
    root_dir = Path(__file__).resolve().parent.parent.parent
    candidate = root_dir / relative_path
    if candidate.exists():
        return candidate

    # 3. Check assets/icons/
    candidate = root_dir / "assets" / "icons" / Path(relative_path).name
    if candidate.exists():
        return candidate

    # 4. Check directly in src/efm/
    candidate = Path(__file__).resolve().parent / relative_path
    if candidate.exists():
        return candidate

    # 5. Fallback to current working directory
    return Path.cwd() / relative_path


def get_config_path() -> Path:
    """Returns the path to the configuration file with clean multi-tier fallback."""
    # 1. Environment variable override
    env_cfg = os.environ.get("EFM_CONFIG_PATH")
    if env_cfg:
        return Path(env_cfg)

    # 2. Frozen binary execution next to executable
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        local_cfg = exe_dir / CONFIG_FILE_NAME
        if local_cfg.exists():
            return local_cfg
        try:
            test_file = exe_dir / ".write_test"
            with open(test_file, 'w') as f:
                f.write("1")
            test_file.unlink()
            return local_cfg
        except Exception:
            pass
    else:
        # Development mode: check project root
        root_dir = Path(__file__).resolve().parent.parent.parent
        local_cfg = root_dir / CONFIG_FILE_NAME
        if local_cfg.exists():
            return local_cfg

    # 3. User standard AppData / Home config directory
    appdata = os.environ.get('APPDATA')
    if appdata:
        app_dir = Path(appdata) / "EFM_Program"
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir / CONFIG_FILE_NAME

    home_config = Path.home() / ".efm"
    home_config.mkdir(parents=True, exist_ok=True)
    return home_config / CONFIG_FILE_NAME


def load_config() -> Dict[str, Any]:
    """Loads configuration from JSON file or returns environment-aware defaults."""
    config_path = get_config_path()
    defaults = {
        "base_dir": os.environ.get("EFM_BASE_DIR") or get_default_base_dir(),
        "appearance_mode": os.environ.get("EFM_APPEARANCE_MODE", "dark"),
        "auto_sort_on_open": os.environ.get("EFM_AUTO_SORT", "true").lower() == "true",
        "open_explorer_on_create": True,
        "open_concept_on_create": False,
        "last_client_type": "project",
        "last_project_type": "Video Editing"
    }

    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                defaults.update(data)
        except Exception as e:
            print(f"[EFM] Error loading config: {e}")

    # Fallback if base directory is invalid or empty
    if not defaults.get("base_dir"):
        defaults["base_dir"] = get_default_base_dir()

    return defaults


def save_config(config: Dict[str, Any]) -> bool:
    """Saves configuration to JSON file."""
    config_path = get_config_path()
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"[EFM] Error saving config: {e}")
        return False


def get_base_dir() -> str:
    """Gets the active base directory from config."""
    cfg = load_config()
    return cfg.get("base_dir") or get_default_base_dir()


def ensure_directory_structure(base_dir: Optional[str] = None) -> None:
    """Ensures key base directory folders exist."""
    if not base_dir:
        base_dir = get_base_dir()

    paths = [
        os.path.join(base_dir, 'Client Project', 'Ongoing Project'),
        os.path.join(base_dir, 'Client Project', 'Finished Project', 'Project Based Clients'),
        os.path.join(base_dir, 'Client Project', 'Finished Project', 'Rebound Clients'),
        os.path.join(base_dir, 'Client Project', 'Ignored Project'),
        os.path.join(base_dir, 'Personal Project', 'Ongoing Project'),
        os.path.join(base_dir, 'Personal Project', 'Finished Project'),
        os.path.join(base_dir, 'Personal Project', 'Ignored Project'),
        os.path.join(base_dir, 'Personal Project', 'Learning Project'),
    ]

    for p in paths:
        os.makedirs(p, exist_ok=True)


def sanitize_folder_name(name: str) -> str:
    """Removes invalid characters for Windows/POSIX folder names."""
    # Invalid Windows chars: < > : " / \ | ? *
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', name.strip())
    # Strip trailing periods and spaces
    cleaned = cleaned.rstrip('. ')
    return cleaned


def open_folder(path: str) -> Tuple[bool, str]:
    """Opens a folder in native OS File Explorer safely."""
    try:
        if os.path.exists(path):
            if os.name == 'nt':
                os.startfile(os.path.realpath(path))
            else:
                subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', path])
            return True, f"Opened {path}"
        else:
            return False, f"Folder does not exist: {path}"
    except Exception:
        # Fallback to subprocess on Windows
        try:
            subprocess.Popen(['explorer', os.path.realpath(path)])
            return True, f"Opened {path}"
        except Exception as e2:
            return False, f"Failed to open folder: {e2}"


def create_project_subfolders(project_path: str) -> str:
    """Creates default subfolders and files within a new project folder."""
    subfolders = [
        'Exported',
        'Project File',
        'Files/Raw',
        'Files/Stock',
        'Files/Reference'
    ]
    for subfolder in subfolders:
        os.makedirs(os.path.join(project_path, subfolder), exist_ok=True)

    concept_file_path = os.path.join(project_path, 'Files', 'Concept.txt')
    if not os.path.exists(concept_file_path):
        with open(concept_file_path, 'w', encoding='utf-8') as f:
            f.write("Concept Ideas and Notes:\n")

    sorting_folders = ['Image', 'Video', 'Audio', 'Doc']
    for folder in ['Raw', 'Stock']:
        for sorting_folder in sorting_folders:
            os.makedirs(os.path.join(project_path, 'Files', folder, sorting_folder), exist_ok=True)

    return concept_file_path


def list_ongoing_projects(base_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lists all ongoing projects under Client Project and Personal Project.
    Returns list of dicts sorted by most recently modified.
    """
    if not base_dir:
        base_dir = get_base_dir()

    projects: List[Dict[str, Any]] = []

    category_dirs = [
        ("Client", os.path.join(base_dir, 'Client Project', 'Ongoing Project')),
        ("Personal", os.path.join(base_dir, 'Personal Project', 'Ongoing Project'))
    ]

    for category, pdir in category_dirs:
        if os.path.exists(pdir):
            try:
                for name in os.listdir(pdir):
                    full_path = os.path.join(pdir, name)
                    if os.path.isdir(full_path):
                        mtime = os.path.getmtime(full_path)
                        mod_dt = datetime.fromtimestamp(mtime)
                        projects.append({
                            "name": name,
                            "path": full_path,
                            "category": category,
                            "modified_time": mod_dt,
                            "date_display": mod_dt.strftime('%b %d, %Y')
                        })
            except Exception as e:
                print(f"[EFM] Error reading {pdir}: {e}")

    # Sort by most recently modified
    projects.sort(key=lambda x: x["modified_time"], reverse=True)
    return projects


def create_new_project(
    project_name: str,
    is_client_project: bool = True,
    base_dir: Optional[str] = None
) -> Tuple[bool, str, Optional[str]]:
    """
    Creates a new project folder with standard subfolder structure.
    Returns (success: bool, message: str, project_path: Optional[str])
    """
    if not base_dir:
        base_dir = get_base_dir()

    project_name = sanitize_folder_name(project_name)
    if not project_name:
        return False, "Project name cannot be empty or contain only invalid characters.", None

    date_str = datetime.now().strftime('%Y%m%d')
    project_folder_name = f"{project_name}_{date_str}"

    if is_client_project:
        ongoing_dir = os.path.join(base_dir, 'Client Project', 'Ongoing Project')
    else:
        ongoing_dir = os.path.join(base_dir, 'Personal Project', 'Ongoing Project')

    target_path = os.path.join(ongoing_dir, project_folder_name)

    if os.path.exists(target_path):
        return False, f"Project folder already exists:\n{target_path}", target_path

    try:
        os.makedirs(target_path, exist_ok=True)
        create_project_subfolders(target_path)
        return True, f"Project '{project_folder_name}' created successfully!", target_path
    except Exception as e:
        return False, f"Failed to create project: {str(e)}", None


def sort_files_into_subfolders(folder_path: str) -> Dict[str, Any]:
    """
    Sorts files in folder_path into 'Image', 'Video', 'Audio', and 'Doc'.
    Returns summary dict with moved counts and collision resolution.
    """
    summary: Dict[str, Any] = {
        "moved_count": 0,
        "details": [],
        "by_category": {cat: 0 for cat in FILE_EXTENSIONS.keys()}
    }

    if not os.path.exists(folder_path):
        return summary

    try:
        items = os.listdir(folder_path)
    except Exception as e:
        summary["details"].append(f"Error accessing folder: {e}")
        return summary

    for filename in items:
        file_path = os.path.join(folder_path, filename)

        # Only process files, skip directories
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(filename)[1].lower()

            for category, exts in FILE_EXTENSIONS.items():
                if file_ext in exts:
                    destination_folder = os.path.join(folder_path, category)
                    os.makedirs(destination_folder, exist_ok=True)
                    dest_file_path = os.path.join(destination_folder, filename)

                    # Handle duplicate file names safely in destination
                    if os.path.exists(dest_file_path):
                        base_stem, ext = os.path.splitext(filename)
                        timestamp = datetime.now().strftime("%H%M%S")
                        dest_file_path = os.path.join(destination_folder, f"{base_stem}_{timestamp}{ext}")

                    try:
                        shutil.move(file_path, dest_file_path)
                        summary["moved_count"] += 1
                        summary["by_category"][category] += 1
                        summary["details"].append(f"Moved {filename} -> {category}/")
                    except Exception as e:
                        summary["details"].append(f"Failed to move {filename}: {e}")
                    break

    return summary


def auto_sort_project(project_path: str) -> Dict[str, Any]:
    """
    Sorts files in both Files/Raw and Files/Stock of a project.
    Returns combined summary.
    """
    raw_path = os.path.join(project_path, 'Files', 'Raw')
    stock_path = os.path.join(project_path, 'Files', 'Stock')

    raw_summary = sort_files_into_subfolders(raw_path)
    stock_summary = sort_files_into_subfolders(stock_path)

    total_moved = raw_summary["moved_count"] + stock_summary["moved_count"]
    combined_details: List[str] = []

    if raw_summary["moved_count"] > 0:
        combined_details.append(f"Raw: {raw_summary['moved_count']} files sorted")
        combined_details.extend(raw_summary["details"])
    if stock_summary["moved_count"] > 0:
        combined_details.append(f"Stock: {stock_summary['moved_count']} files sorted")
        combined_details.extend(stock_summary["details"])

    return {
        "total_moved": total_moved,
        "raw_moved": raw_summary["moved_count"],
        "stock_moved": stock_summary["moved_count"],
        "details": combined_details
    }


def get_existing_rebound_clients(base_dir: Optional[str] = None) -> List[str]:
    """Returns list of existing rebound client folder names."""
    if not base_dir:
        base_dir = get_base_dir()

    rebound_path = os.path.join(base_dir, 'Client Project', 'Finished Project', 'Rebound Clients')
    if not os.path.exists(rebound_path):
        return []
    try:
        return [f for f in os.listdir(rebound_path) if os.path.isdir(os.path.join(rebound_path, f))]
    except Exception:
        return []


def calculate_move_destination(
    project_folder_path: str,
    is_client_project: bool,
    status: str,
    client_type: Optional[str] = None,
    project_type: Optional[str] = None,
    rebound_folder: Optional[str] = None,
    base_dir: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Calculates the destination directory path for moving a project.
    Returns (valid: bool, destination_dir: Optional[str], error_msg: Optional[str])
    """
    if not base_dir:
        base_dir = get_base_dir()

    status = status.lower()

    if is_client_project:
        if status == 'finished':
            if client_type == 'project':
                if not project_type:
                    return False, None, "Please select a Project Type (e.g. Video Editing, Animation)."
                dest = os.path.join(base_dir, 'Client Project', 'Finished Project', 'Project Based Clients', project_type)
                return True, dest, None
            elif client_type == 'rebound':
                if not rebound_folder or not sanitize_folder_name(rebound_folder):
                    return False, None, "Please specify a valid Rebound Client folder name."
                dest = os.path.join(base_dir, 'Client Project', 'Finished Project', 'Rebound Clients', sanitize_folder_name(rebound_folder))
                return True, dest, None
            else:
                return False, None, "Please choose either Project Based or Rebound client."
        elif status == 'ignored':
            dest = os.path.join(base_dir, 'Client Project', 'Ignored Project')
            return True, dest, None
        else:
            return False, None, f"Invalid status '{status}' for Client Project."
    else:
        # Personal Project
        if status == 'finished':
            dest = os.path.join(base_dir, 'Personal Project', 'Finished Project')
            return True, dest, None
        elif status == 'ignored':
            dest = os.path.join(base_dir, 'Personal Project', 'Ignored Project')
            return True, dest, None
        elif status == 'learning':
            dest = os.path.join(base_dir, 'Personal Project', 'Learning Project')
            return True, dest, None
        else:
            return False, None, f"Invalid status '{status}' for Personal Project."


def move_project(
    project_folder_path: str,
    is_client_project: bool,
    status: str,
    client_type: Optional[str] = None,
    project_type: Optional[str] = None,
    rebound_folder: Optional[str] = None,
    base_dir: Optional[str] = None
) -> Tuple[bool, str, Optional[str]]:
    """
    Moves an ongoing project folder to the destination.
    Returns (success: bool, message: str, destination_path: Optional[str])
    """
    if not os.path.exists(project_folder_path):
        return False, f"Source project folder does not exist:\n{project_folder_path}", None

    valid, dest_dir, error_msg = calculate_move_destination(
        project_folder_path, is_client_project, status, client_type, project_type, rebound_folder, base_dir
    )

    if not valid or not dest_dir:
        return False, error_msg or "Invalid destination specified.", None

    project_name = os.path.basename(project_folder_path)
    final_dest_path = os.path.join(dest_dir, project_name)

    if os.path.exists(final_dest_path):
        return False, f"A project with the name '{project_name}' already exists in destination:\n{final_dest_path}", final_dest_path

    try:
        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(project_folder_path, dest_dir)
        return True, f"Successfully moved '{project_name}' to:\n{dest_dir}", final_dest_path
    except Exception as e:
        return False, f"Failed to move project: {str(e)}", None
