# Enhanced BIDS Stats Model Validation

This module provides comprehensive validation for BIDS Stats Model JSON files, combining the official BIDSStatsModel validation with enhanced transformation validation capabilities.

## Architecture

The validation system uses a layered approach:

1. **BIDSStatsModel** (Official) - Core BIDS structure validation
2. **EnhancedBIDSValidator** - Combines official validation + transformations
3. **TransformationValidator** - Detailed transformation instruction validation

## Usage

### Basic Validation (Official BIDS Only)

```python
from bsmschema.models import BIDSStatsModel
import json

# Load and validate using official BIDS validator
with open('model.json', 'r') as f:
    data = json.load(f)

model = BIDSStatsModel(**data)  # Raises ValidationError if invalid
```

### Enhanced Validation (BIDS + Transformations)

```python
from stats_spec_architect.validation import EnhancedBIDSValidator

# Create validator
validator = EnhancedBIDSValidator()

# Validate JSON file
result = validator.validate_json_file('model.json')

# Check results
if result.valid:
    print("✅ Validation passed!")
else:
    print(f"❌ Validation failed: {len(result.errors)} errors")
    for error in result.errors:
        print(f"  - {error}")

# Get summary
print(validator.get_validation_summary(result))
```

### Transformation-Only Validation

```python
from stats_spec_architect.validation import TransformationValidator

validator = TransformationValidator()

# Validate individual transformation
instruction = {"Name": "Factor", "Input": ["trial_type"]}
result = validator.validate_instruction(instruction)

# Validate list of transformations
instructions = [
    {"Name": "Factor", "Input": ["trial_type"]},
    {"Name": "Convolve", "Input": ["trial_type"]}
]
result = validator.validate_instructions(instructions)
```

## Available Transformations

The validator supports all transformations from the pybids transformation schema:

- Add, Divide, Multiply, Subtract
- And, Or, Not
- Assign, Constant, Copy
- Convolve, Deconvolve
- Delete, Demean, Derivative
- DropNa, Factor, Filter
- Mean, Name, Orthogonalize
- Power, Product, Replace
- Scale, Select, Split
- StdDev, Sum, Threshold
- ToDense, Variance

## Validation Levels

### Level 1: BIDS Structure
- Required fields (Name, BIDSModelVersion, Nodes, Edges)
- Field types and constraints
- Enum values (Level, ModelType, etc.)
- Basic business logic (duplicate names, edge references)

### Level 2: Transformations
- Transformation instruction validation
- Required fields for each transformation type
- Field types and constraints
- Available transformation types

### Level 3: Business Logic
- Duplicate node names
- Duplicate edges
- Edge source/destination validation
- Additional custom rules

## Error Reporting

The enhanced validator provides detailed error messages:

- **Field-level errors**: Specific field validation failures
- **Transformation errors**: Detailed transformation instruction errors
- **Business logic errors**: Custom validation rule failures
- **Context information**: Node names, instruction numbers, etc.

## Integration with GUI

This validation system is designed to work with GUI applications:

- **Real-time validation**: Validate as users build models
- **Error highlighting**: Show specific field errors
- **Dropdown population**: Use available transformations for UI
- **Type safety**: Ensure generated JSON is always valid

## Future Enhancements

- Additional business logic rules
- Custom transformation types
- Integration with BIDS dataset validation
- Enhanced error reporting and suggestions