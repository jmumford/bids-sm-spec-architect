# GUI Version 2 - Pydantic-based Implementation

This directory will contain the next-generation GUI that integrates with the Pydantic validation models.

## Architecture Plan

### Core Components

1. **main_gui.py** - Main window and application entry point
2. **input_widgets.py** - Top-level input widgets (Name, Version, Description, Input fields)
3. **node_widgets.py** - Node configuration widgets
4. **transformation_widgets.py** - Transformation widgets built from Pydantic models
5. **edge_widgets.py** - Edge configuration widgets
6. **json_builder.py** - JSON construction with validation
7. **utils.py** - Shared utilities and widget factories

### Key Improvements Over v1

- **Pydantic Model Integration**: Widgets auto-generated from Pydantic model definitions
- **Real-time Validation**: Integration with `EnhancedBIDSValidator`
- **Better Error Display**: Structured validation feedback with field-level highlighting
- **Type Safety**: Automatic type conversion and validation via Pydantic
- **Cleaner Architecture**: Separation of widget creation from data processing

### Development Status

🚧 **Under Development** 🚧

Currently in planning phase. Implementation will begin after v1 stabilization.

## Validation Integration

This GUI will use:
- `stats_spec_architect.validation.enhanced_validator.EnhancedBIDSValidator`
- `stats_spec_architect.validation.transformation_models` for widget generation
- `bsmschema.models.BIDSStatsModel` for official BIDS schema

## Migration Notes

When migrating from v1:
1. Widget creation logic will be rebuilt using Pydantic field introspection
2. Validation will happen both during input and before JSON export
3. Error messages will be more specific and actionable
4. UI layout will remain familiar to ease transition

