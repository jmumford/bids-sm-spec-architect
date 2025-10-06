"""
Enhanced BIDS Stats Model validator.

This validator combines the official BIDSStatsModel validation with
enhanced transformation validation, providing comprehensive validation
for BIDS Stats Model JSON files.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union

from bsmschema.models import BIDSStatsModel
from pydantic import ValidationError

from .transformation_validator import (
    TransformationValidator,
)


class ValidationResult:
    """Result of enhanced validation operation"""

    def __init__(
        self, valid: bool, errors: List[str] = None, warnings: List[str] = None
    ):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []

    def __bool__(self):
        return self.valid

    def __str__(self):
        if self.valid:
            return 'Validation passed'
        else:
            return f"Validation failed: {'; '.join(self.errors)}"


class EnhancedBIDSValidator:
    """Enhanced validator that combines BIDSStatsModel + transformation validation"""

    def __init__(self):
        self.transformation_validator = TransformationValidator()

    def validate_json_file(self, json_file: Union[str, Path]) -> ValidationResult:
        """Validate a JSON file containing BIDS Stats Model specification"""
        json_file = Path(json_file)
        if not json_file.exists():
            return ValidationResult(False, [f'File not found: {json_file}'])

        try:
            with open(json_file) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return ValidationResult(False, [f'Invalid JSON: {e}'])

        return self.validate_data(data)

    def validate_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate BIDS Stats Model data"""
        errors = []
        warnings = []

        # Step 1: Validate using official BIDSStatsModel
        try:
            model = BIDSStatsModel(**data)
        except ValidationError as e:
            for error in e.errors():
                field_path = ' -> '.join(str(x) for x in error['loc'])
                errors.append(f"BIDS validation: {field_path}: {error['msg']}")
            return ValidationResult(False, errors)

        # Step 2: Validate transformations in each node
        for i, node in enumerate(model.Nodes):
            if hasattr(node, 'Transformations') and node.Transformations:
                if hasattr(node.Transformations, 'Instructions'):
                    instructions = node.Transformations.Instructions
                    if instructions:
                        transform_result = (
                            self.transformation_validator.validate_instructions(
                                instructions
                            )
                        )
                        if not transform_result.valid:
                            for error in transform_result.errors:
                                errors.append(f'Node {i+1} ({node.Name}): {error}')

        # Step 3: Additional business logic validation
        business_errors = self._validate_business_logic(model)
        errors.extend(business_errors)

        return ValidationResult(len(errors) == 0, errors, warnings)

    def _validate_business_logic(self, model: BIDSStatsModel) -> List[str]:
        """Validate additional business logic rules"""
        errors = []

        # Check for duplicate node names
        node_names = [node.Name for node in model.Nodes]
        if len(node_names) != len(set(node_names)):
            duplicates = [
                name for name in set(node_names) if node_names.count(name) > 1
            ]
            errors.append(f'Duplicate node names: {duplicates}')

        # Check for duplicate edge source-destination pairs
        edge_pairs = [(edge.Source, edge.Destination) for edge in model.Edges]
        if len(edge_pairs) != len(set(edge_pairs)):
            duplicates = [
                pair for pair in set(edge_pairs) if edge_pairs.count(pair) > 1
            ]
            errors.append(f'Duplicate edges: {duplicates}')

        # Check that edge sources and destinations exist
        node_names_set = set(node_names)
        for edge in model.Edges:
            if edge.Source not in node_names_set:
                errors.append(f"Edge source '{edge.Source}' not found in nodes")
            if edge.Destination not in node_names_set:
                errors.append(
                    f"Edge destination '{edge.Destination}' not found in nodes"
                )

        return errors

    def get_validation_summary(self, result: ValidationResult) -> str:
        """Get a human-readable validation summary"""
        if result.valid:
            summary = '✅ Validation passed'
            if result.warnings:
                summary += f'\n⚠️  Warnings: {len(result.warnings)}'
                for warning in result.warnings:
                    summary += f'\n  - {warning}'
        else:
            summary = f'❌ Validation failed with {len(result.errors)} errors:'
            for error in result.errors:
                summary += f'\n  - {error}'

        return summary

    def get_available_transformations(self) -> List[str]:
        """Get list of available transformation types"""
        return self.transformation_validator.get_available_transformations()
