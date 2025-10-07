# GUI Refactoring Summary

## ✅ Completed Changes

### Directory Structure Created

```
stats_spec_architect/
├── gui_v1/                    # Legacy GUI (moved from root)
│   ├── __init__.py
│   ├── DoubleScrolledFrame.py
│   ├── edges_setup.py
│   ├── input_setup.py
│   ├── layout_loading.py
│   ├── main_gui.py
│   ├── make_json.py
│   ├── nodes_transformations_setup_try_tabs.py
│   ├── nodes_transformations_setup.py
│   └── utils.py
│
├── gui_v2/                    # New Pydantic-based GUI (placeholder)
│   ├── __init__.py
│   ├── README.md
│   └── widget_factory.py
│
├── validation/                # Shared validation (unchanged)
│   ├── enhanced_validator.py
│   ├── models.py
│   ├── transformation_models.py
│   └── transformation_validator.py
│
└── __main__.py               # Updated to use gui_v1
```

### Changes Made

1. **Moved GUI files to `gui_v1/`**
   - All existing GUI components moved using `git mv` (preserves history)
   - Added `__init__.py` with documentation

2. **Updated all imports**
   - Changed `from stats_spec_architect.X` → `from stats_spec_architect.gui_v1.X`
   - Fixed asset path in `utils.py` to point to parent directory
   - Updated `__main__.py` to import from `gui_v1`

3. **Created `gui_v2/` placeholder**
   - Added `__init__.py` with description
   - Created comprehensive `README.md` with architecture plan
   - Added skeleton `widget_factory.py` for Pydantic-based widget generation

### Testing

✅ Import test passed: `uv run python -c "from stats_spec_architect.gui_v1.main_gui import launch_main_gui"`

### How to Run

The GUI still works exactly as before:
```bash
uv run make_spec
```

### Known Items for Cleanup

The following items were identified for cleanup:

1. **Duplicate Pydantic functions** (can be removed):
   - `CreateInputWidgetsPydantic` in `input_setup.py` (lines 53-94)
   - `launch_main_gui_pydantic` in `main_gui.py` (lines 70-111)

2. **Old transformation setup** (can be removed if not used):
   - `nodes_transformations_setup.py` (seems superseded by `nodes_transformations_setup_try_tabs.py`)

3. **Junk files in main directory**:
   - `junk_test_layout_loading.py`
   - `junk_test_layout_loading2.py`
   - `junk_test.py`

### Next Steps for GUI v2

When ready to implement the new Pydantic-based GUI:

1. **Phase 1**: Build `TransformationWidgetFactory` using Pydantic models
2. **Phase 2**: Create node and input widgets
3. **Phase 3**: Integrate `EnhancedBIDSValidator` for real-time validation
4. **Phase 4**: Test both versions side-by-side
5. **Phase 5**: Deprecate v1 after v2 is stable

See `stats_spec_architect/gui_v2/README.md` for detailed architecture plan.

