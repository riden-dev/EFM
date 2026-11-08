# EFM (Edit Folder Manager)

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Cross--Platform-lightgrey.svg)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-0ea5e9.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

**A modern Windows desktop application to scaffold, organize, and archive creative video editing workflows.**

[Key Features](#-key-features) •
[Architecture](#-repository-structure) •
[Quick Start](#-quick-start) •
[Configuration](#-configuration) •
[Packaging](#-building-the-standalone-executable) •
[Contributing](#-contributing)

</div>

---

## 📖 Overview

**EFM (Edit Folder Manager)** is a dedicated post-production workspace automation tool engineered for video editors, motion designers, content creators, and post-production studios. It replaces manual file management with an automated, standardized pipeline that scaffolds uniform editing directory structures, categorizes raw and stock footage automatically, manages active client and personal projects, and safely archives completed work into clean storage hierarchies.

---

## ⚡ The Problem & The Solution

| The Traditional Editing Bottleneck | The EFM Solution |
| :--- | :--- |
| **Manual Repetition**: Creating the same 6–8 subfolders by hand for every new video or client. | **Instant Scaffolding**: Automatically sets up standardized folders (`Exported`, `Project File`, `Raw`, `Stock`, `Reference`, `Concept.txt`) with one click. |
| **Scattered Media**: SD card dumps, stock clips, voiceovers, and SFX jumbled together. | **Multi-Format Auto-Sorter**: Scans and sorts files by extension into `Video`, `Audio`, `Image`, and `Doc` with duplicate collision protection. |
| **Drive Clutter**: Active and finished projects mixed together across workspace drives. | **Smart Archiving Engine**: Categorizes projects into `Project-Based`, `Rebound Clients`, `Ignored`, or `Learning` storage. |
| **Inconsistent Naming**: Disorganized archives that become impossible to search months later. | **Deterministic Naming**: Enforces timestamped sanitization (`ProjectName_YYYYMMDD`). |

---

## 🎬 Standardized Project Directory Structure

Every project generated through EFM complies with a production-grade folder structure:

```text
📁 <ProjectName>_YYYYMMDD/
├── 📁 Exported/                     # Drafts, review cuts, and final client masters
├── 📁 Project File/                 # .prproj, .aep, .blend, .drp project files
├── 📁 Files/
│   ├── 📄 Concept.txt               # Creative brief, brainstorm notes, and links
│   ├── 📁 Reference/                # Moodboards, style guides, client reference clips
│   ├── 📁 Raw/                      # Production shoot footage and source assets
│   │   ├── 📁 Video/                # Camera footage (.mp4, .mov, .mkv, .m2ts)
│   │   ├── 📁 Audio/                # Production audio, boom/lav tracks (.wav, .mp3)
│   │   ├── 📁 Image/                # Stills, textures, graphics (.png, .jpg, .heic, .psd)
│   │   └── 📁 Doc/                  # Scripts, storyboards, releases (.pdf, .docx, .txt)
│   └── 📁 Stock/                    # Licensed and external assets
│       ├── 📁 Video/                # B-roll, overlays, VFX elements
│       ├── 📁 Audio/                # Background music, SFX, foley
│       ├── 📁 Image/                # Stock images, brand logos, vector art
│       └── 📁 Doc/                  # Asset licenses, invoices, clearance documents
```

---

## ✨ Key Features

### 1. 🏠 Executive Dashboard
- Inspired by modern post-production design concepts (`Render1.png`), built with a clean dark-slate interface.
- Instant hero cards for **Open Project**, **New Project**, and **Move Project**.
- Real-time statistics badge reporting active Client vs. Personal projects.

### 2. 📁 Active Projects Hub
- Automatically aggregates ongoing projects across both Client and Personal directories.
- Real-time instant search bar and category filters (`All`, `Client`, `Personal`).
- Direct action triggers: **Open in Explorer**, **Auto-Sort Files**, and **Move/Archive**.

### 3. 🧹 Multi-Format Media Classifier & Sorter
- Automatically sorts loose files into dedicated subfolders based on extension:
  - **Video**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.wmv`, `.m4v`, `.flv`, `.webm`, `.m2ts`, `.mts`
  - **Audio**: `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`, `.m4a`, `.wma`, `.aiff`, `.alac`
  - **Image**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.heic`, `.webp`, `.svg`, `.psd`, `.ai`
  - **Doc / Project**: `.pdf`, `.docx`, `.txt`, `.pptx`, `.xlsx`, `.doc`, `.rtf`, `.csv`, `.prproj`, `.aep`, `.blend`
- **Collision Protection**: If a target file already exists, appends a micro-timestamp (`_HHMMSS`) to prevent data loss.
- **Universal Sorter Utility**: Allows pointing to *any* folder (such as Downloads or an external drive) to organize loose media.

### 4. 📦 Structured Archiving & Client Management
- **Client Projects**:
  - `Finished Project ➔ Project-Based Clients`: Categorized by discipline (`Animation`, `Video Editing`, `Image Editing`, `Graphics Design`, `Whole Package`).
  - `Finished Project ➔ Rebound Clients`: Move directly into recurring/retainer client folders, or create a new client folder on the fly.
  - `Ignored Project`: Clean storage for cancelled or abandoned client work.
- **Personal Projects**:
  - `Finished Project`, `Ignored Project`, or `Learning Project` (dedicated space for tutorials and R&D).
- Displays a visual origin-to-destination path preview and confirmation check before moving.

---

## 🏛️ Repository Structure

```text
efm/
├── .github/                         # GitHub issue templates and PR configuration
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── assets/                          # Application icons, graphics, and visual assets
│   └── icons/
│       ├── efm_icon.ico
│       └── efm_icon.png
├── docs/                            # Deep-dive architecture and design documentation
│   └── ARCHITECTURE.md
├── legacy/                          # Archived early prototype scripts (sanitized)
├── scripts/                         # Build, packaging, and CI helper scripts
│   └── build_exe.py                 # Standalone PyInstaller compilation script
├── src/                             # Core application source code
│   └── efm/
│       ├── __init__.py              # Package metadata and version definition
│       ├── app.py                   # CustomTkinter GUI presentation layer
│       └── core.py                  # Headless core business logic engine
├── tests/                           # Unit and integration test suite
│   ├── __init__.py
│   └── test_core.py                 # Core engine unit tests
├── .env.example                     # Environment configuration template
├── .gitignore                       # Production gitignore rules
├── CONTRIBUTING.md                  # Open-source contribution guidelines
├── LICENSE                          # MIT License
├── main.py                          # Primary application entry point
├── pyproject.toml                   # Modern PEP 517/621 packaging metadata
├── requirements.txt                 # Pinned runtime dependencies
└── requirements-dev.txt             # Testing and development dependencies
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (Tested on Python 3.10, 3.11, 3.12, 3.13, and 3.14).
- **Windows 10 / 11** (recommended; core headless logic is cross-platform).

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/efm.git
cd efm
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements-dev.txt
pip install -e .
```

### 4. Configure Your Workspace
Copy the example environment file and customize your storage location:
```bash
cp .env.example .env
```
Open `.env` in any editor and specify where your editing projects should live:
```env
EFM_BASE_DIR=D:\Projects
EFM_APPEARANCE_MODE=dark
EFM_AUTO_SORT=true
```

### 5. Launch the Application
```bash
python main.py
```

---

## 🧪 Running Tests

The test suite validates path sanitization, folder tree creation, file classification, destination calculation, and project moving:

```bash
python -m pytest
```

---

## 📦 Building the Standalone Executable

To compile a self-contained Windows `.exe` that does not require Python on the target machine:

```bash
python scripts/build_exe.py
```

The compiled binary will be placed at:
```text
dist/EFM.exe
```

---

## ⚙️ Configuration Reference

EFM can be configured via environment variables, `.env`, or the in-app **Settings** panel:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `EFM_BASE_DIR` | `string` | `~/Documents/EFM_Projects` | Absolute path to the root projects directory. |
| `EFM_CONFIG_PATH` | `string` | OS Default (`%APPDATA%`) | Custom path for `efm_config.json`. |
| `EFM_APPEARANCE_MODE` | `string` | `dark` | Default theme: `dark`, `light`, or `system`. |
| `EFM_AUTO_SORT` | `boolean` | `true` | Automatically sorts Raw and Stock files when opening a project. |

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on code style, branch naming, and our pull request process.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
