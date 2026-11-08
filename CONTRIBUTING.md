# Contributing to EFM (Edit Folder Manager)

Thank you for your interest in contributing to **EFM**! We welcome contributions from video editors, developers, designers, and workflow specialists.

---

## 🛠️ Code of Conduct
We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone. Please be respectful and constructive in all communications.

---

## 🚀 Getting Started

### 1. Fork and Clone
```bash
git clone https://github.com/<your-username>/efm.git
cd efm
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements-dev.txt
pip install -e .
```

### 4. Create a Local Configuration
```bash
cp .env.example .env
# Edit .env with your local test folder path
```

---

## 🧪 Running Tests
Always verify that unit tests pass before submitting changes:
```bash
python -m pytest
```

---

## 📦 Building the Executable
To test the standalone binary build pipeline:
```bash
python scripts/build_exe.py
```

---

## 📐 Development Guidelines

- **Code Style**: Follow [PEP 8](https://peps.python.org/pep-0008/) naming and formatting conventions. Use explicit type hints for core logic functions.
- **Privacy & Sanitization**: Never commit hardcoded local drive paths, private usernames, or secrets. Rely on `os.environ` and `.env.example`.
- **Decoupled Architecture**: Keep business logic in `src/efm/core.py` and UI components in `src/efm/app.py`. The core engine should never depend on GUI widgets.
- **Cross-Platform Awareness**: While EFM is optimized for Windows post-production workflows, core logic should avoid breaking on macOS/Linux.

---

## 🔀 Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Commit your changes with clear, descriptive commit messages:
   ```bash
   git commit -m "feat(sorter): add support for .m2ts video containers"
   ```
3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
4. Open a Pull Request on GitHub against the `main` branch.
5. Fill out the PR template describing your changes, motivation, and verification steps.
