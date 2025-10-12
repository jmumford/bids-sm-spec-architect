# BIDS Stats Model Architect

A GUI application for creating and editing BIDS Stats Model specification JSON files.

Built with dynamic Pydantic-based widget generation, this tool ensures your statistical models conform to the [BIDS Stats Models specification](https://bids-standard.github.io/stats-models/).

---

## Features

- ✨ **Dynamic GUI** - Automatically adapts to the BIDS Stats Model schema
- 🔍 **Real-time Validation** - Validates your model against the full BIDS specification
- 📦 **JSON Import/Export** - Load existing models, edit, and save
- 🎯 **24 PyBIDS Transformations** - Full support for all data transformations
- 💡 **Contextual Help** - Hover tooltips with field descriptions
- 🎨 **Modern UI** - Clean, collapsible sections with accordion transformations

---

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

### 1. Install uv (if you haven't already)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

### 2. Clone and Install

```bash
git clone https://github.com/YOUR_USERNAME/bids-sm-spec-architect.git
cd bids-sm-spec-architect
uv sync
```

That's it! `uv` will:
- Create a virtual environment (`.venv/`)
- Install all dependencies (including `bsmschema` from PyPI)
- Install the `stats_spec_architect` package

---

## Usage

Launch the GUI with:

```bash
uv run build_model
```

This will open the BIDS Stats Model Architect interface where you can:

1. **Configure Input** - Set your BIDS dataset filters (task, subject, run, session)
2. **Add Nodes** - Define hierarchical analysis levels (run, subject, dataset)
3. **Add Transformations** - Apply PyBIDS data transformations
4. **Define Models** - Specify GLM design matrices, HRF models, and contrasts
5. **Connect with Edges** - Link nodes in multi-level analyses
6. **Export & Validate** - Generate valid BIDS Stats Model JSON

### Saving Your Work

- **Show Model Spec (JSON)** - Preview the generated JSON
- **Save to File** - Export to a `.json` file
- **Load from File** - Import and edit existing models
- **Validate** - Check your model against BIDS specification

---

## Project Structure

```
bids-sm-spec-architect/
├── src/
│   └── stats_spec_architect/
│       ├── gui/              # GUI components (Pydantic-driven)
│       ├── validation/       # Enhanced BIDS validators
│       └── assets/          # UI icons
├── pyproject.toml           # Modern hatchling-based config
├── uv.lock                 # Locked dependencies
└── README.md
```

---

## Troubleshooting

### macOS: GUI Not Responding to Clicks (Sonoma Users)

**Symptom:** The GUI opens but doesn't register mouse clicks properly.

**Cause:** Older versions of tcl/tk (< 8.6.13) have compatibility issues with macOS Sonoma.

**Solution:** Verify your Python's tcl/tk version:

```python
import tkinter as tk
print("Tcl Version:", tk.Tcl().eval('info patchlevel'))
print("Tk Version:", tk.Tk().eval('info patchlevel'))
```

Both should be **> 8.6.13**. If not, reinstall Python with a newer version:

```bash
# Using Homebrew
brew reinstall python@3.12

# Then recreate your virtual environment
rm -rf .venv
uv sync
```

**Note:** This issue has been resolved in recent Python builds (3.12.11+). If you installed Python recently, you should be fine!

---

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check code
uv run ruff check .

# Format code
uv run ruff format .
```

---

## Dependencies

- **[bsmschema](https://pypi.org/project/bsmschema/)** - BIDS Stats Model Pydantic schemas
- **[pybids](https://pypi.org/project/pybids/)** - BIDS dataset interface
- **[ttkbootstrap](https://pypi.org/project/ttkbootstrap/)** - Modern themed Tkinter widgets
- **[pydantic](https://pypi.org/project/pydantic/)** - Data validation

See `pyproject.toml` for full dependency list.

---

## License

See [LICENSE](LICENSE) file.

---

## Contributing

Issues and pull requests welcome! This is a research tool under active development.

---

## Citation

If you use this tool in your research, please cite:

```
Mumford, J. (2025). BIDS Stats Model Architect. 
https://github.com/YOUR_USERNAME/bids-sm-spec-architect
```

---

## Acknowledgments

Built with support from the [BIDS Stats Models](https://bids-standard.github.io/stats-models/) community.
