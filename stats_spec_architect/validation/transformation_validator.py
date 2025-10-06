"""
Transformation validator for BIDS Stats Model specifications.

This module provides validation for transformation instructions using the
pybids transformation schema, without duplicating the core BIDS validation.
"""

from typing import Any, Dict, List

from pydantic import ValidationError

from .transformation_models import (
    AndInstruction,
    AssignInstruction,
    ConvolveInstruction,
    CopyInstruction,
    DeleteInstruction,
    DemeanInstruction,
    DropNaInstruction,
    FactorInstruction,
    FilterInstruction,
    GroupInstruction,
    LagInstruction,
    NotInstruction,
    OrInstruction,
    OrthogonalizeInstruction,
    ProductInstruction,
    RenameInstruction,
    ReplaceInstruction,
    ResampleInstruction,
    ScaleInstruction,
    SelectInstruction,
    SplitInstruction,
    SumInstruction,
    ThresholdInstruction,
    ToDenseInstruction,
    get_available_transformations,
)


class TransformationValidationResult:
    """Result of transformation validation"""

    def __init__(self, valid: bool, errors: List[str] = None):
        self.valid = valid
        self.errors = errors or []

    def __bool__(self):
        return self.valid


class TransformationValidator:
    """Validator for transformation instructions"""

    def __init__(self):
        self.available_transforms = get_available_transformations()
        self.transform_models = {
            'And': AndInstruction,
            'Assign': AssignInstruction,
            'Convolve': ConvolveInstruction,
            'Copy': CopyInstruction,
            'Demean': DemeanInstruction,
            'Delete': DeleteInstruction,
            'DropNa': DropNaInstruction,
            'Factor': FactorInstruction,
            'Filter': FilterInstruction,
            'Group': GroupInstruction,
            'Lag': LagInstruction,
            'Not': NotInstruction,
            'Or': OrInstruction,
            'Orthogonalize': OrthogonalizeInstruction,
            'Product': ProductInstruction,
            'Rename': RenameInstruction,
            'Replace': ReplaceInstruction,
            'Resample': ResampleInstruction,
            'Scale': ScaleInstruction,
            'Select': SelectInstruction,
            'Split': SplitInstruction,
            'Sum': SumInstruction,
            'Threshold': ThresholdInstruction,
            'ToDense': ToDenseInstruction,
        }

    def validate_instruction(
        self, instruction: Dict[str, Any]
    ) -> TransformationValidationResult:
        """Validate a single transformation instruction"""
        errors = []

        # Check if instruction has a Name field
        if 'Name' not in instruction:
            return TransformationValidationResult(
                False, ["Missing 'Name' field in transformation instruction"]
            )

        transform_name = instruction['Name']

        # Check if transformation is available
        if transform_name not in self.available_transforms:
            available = ', '.join(self.available_transforms)
            return TransformationValidationResult(
                False,
                [f"Unknown transformation '{transform_name}'. Available: {available}"],
            )

        # Get the appropriate model for this transformation
        if transform_name not in self.transform_models:
            return TransformationValidationResult(
                False,
                [
                    f"No validation model available for transformation '{transform_name}'"
                ],
            )

        # Validate using the specific model
        try:
            model_class = self.transform_models[transform_name]
            model_class(**instruction)
            return TransformationValidationResult(True)
        except ValidationError as e:
            for error in e.errors():
                field_path = ' -> '.join(str(x) for x in error['loc'])
                errors.append(f"{transform_name}: {field_path}: {error['msg']}")
            return TransformationValidationResult(False, errors)

    def validate_instructions(
        self, instructions: List[Dict[str, Any]]
    ) -> TransformationValidationResult:
        """Validate a list of transformation instructions"""
        all_errors = []

        for i, instruction in enumerate(instructions):
            result = self.validate_instruction(instruction)
            if not result.valid:
                for error in result.errors:
                    all_errors.append(f'Instruction {i+1}: {error}')

        return TransformationValidationResult(len(all_errors) == 0, all_errors)

    def get_available_transformations(self) -> List[str]:
        """Get list of available transformation types"""
        return self.available_transforms.copy()
