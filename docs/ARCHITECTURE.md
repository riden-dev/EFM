# EFM Architecture & Design Principles

## 🏛️ High-Level Overview

**EFM (Edit Folder Manager)** is structured using a strict separation of concerns between presentation and business logic:

```
                  +-----------------------------------+
                  |             main.py               |
                  |     (CLI / Module Launcher)       |
                  +-----------------+-----------------+
                                    |
                    +---------------+---------------+
                    |                               |
    +---------------+---------------+   +-----------+-----------+
    |         src/efm/app.py        |   |    scripts/build_exe  |
    |      (CustomTkinter GUI)      |   |  (PyInstaller Bundler)|
    +---------------+---------------+   +-----------------------+
                    |
                    v
    +-------------------------------+
    |         src/efm/core.py       |
    |  - Path Sanitization          |
    |  - Directory Scaffolding      |
    |  - Extension Categorization   |
    |  - Archival Routing Engine    |
    |  - Config & Env Resolution    |
    +---------------+---------------+
                    |
                    v
    +-------------------------------+
    |  Local / Network Filesystem   |
    |    (Client & Personal Dirs)   |
    +-------------------------------+
```

---

## 🧩 Component Architecture

### 1. Core Logic Engine (`src/efm/core.py`)
- **Zero GUI Dependency**: Can be imported, scripted, and tested completely headlessly without loading Tkinter or GUI libraries.
- **Scaffolding Subsystem**: Generates standardized folder trees with `Exported/`, `Project File/`, `Files/Raw/{Image,Video,Audio,Doc}`, and `Files/Stock/{Image,Video,Audio,Doc}`.
- **Classification Engine**: Fast hash-map dictionary lookup matching lowercased file extensions against standardized media buckets (`Image`, `Video`, `Audio`, `Doc`).
- **Collision Resolution**: Detects duplicate file targets during automated moves and transparently appends a micro-timestamp (`_HHMMSS`) to prevent data loss.
- **Routing & Archiving Rules**:
  - Differentiates between Client and Personal workflows.
  - Automatically isolates client deliverables into discipline folders (`Video Editing`, `Animation`, `Graphics Design`, etc.) or recurring client folders (`Rebound Clients/<ClientName>`).

### 2. Modern Presentation Layer (`src/efm/app.py`)
- Built on top of **CustomTkinter** for high-DPI scaling, native dark/light theme switching, and smooth rounded cards.
- Decoupled view routing via container frame swapping (`show_view("dashboard")`, `show_view("projects")`, etc.).
- Non-blocking execution hooks for folder openings and batch operations.

### 3. Build & Packaging Pipeline (`scripts/build_exe.py`)
- Invokes PyInstaller with portable relative resource paths.
- Embeds multi-size icons (`.ico` and `.png`).
- Packages CustomTkinter JSON themes and assets into a portable single-binary executable (`dist/EFM.exe`).

---

## 🔒 Configuration & Environment Hierarchy
EFM resolves configuration through a deterministic 4-stage hierarchy:
1. **Explicit Environment Variables** (e.g. `EFM_BASE_DIR`, `EFM_THEME`)
2. **Local `.env` File** (loaded via internal parser if present)
3. **Persistent Config File** (`efm_config.json` in project root, exe directory, or `%APPDATA%\EFM_Program`)
4. **OS Fallback Standard** (`~/Documents/EFM_Projects` or `~/Videos/Projects`)
