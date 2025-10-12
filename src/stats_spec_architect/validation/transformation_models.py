"""
Pydantic models for pybids transformation instructions.

These models are extracted from the pybids_xform_schema_JM.json file and provide
type-safe validation for transformation instructions.
"""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator


# Individual transformation instruction models (only pybids transformations)
class AndInstruction(BaseModel):
    """Logical AND operation"""

    Name: Literal['And'] = 'And'
    Input: List[str] = Field(..., description='Variables for AND operation')
    Output: str = Field(..., description='Output variable name')


class AssignInstruction(BaseModel):
    """Assign one variable's amplitude, duration, or onset attribute to another (sparse variables only)"""

    Name: Literal['Assign'] = 'Assign'
    Input: List[str] = Field(
        ..., description='Variables from which attribute values are to be drawn'
    )
    Target: List[str] = Field(
        ..., description='Variables to which attribute values are to be assigned'
    )
    Output: Optional[List[str]] = Field(None, description='Output variable names')
    InputAttr: Optional[Union[str, List[str]]] = Field(
        'amplitude', description='Attribute of input column to assign'
    )
    TargetAttr: Optional[Union[str, List[str]]] = Field(
        'amplitude', description='Attribute of output column to assign to'
    )


class ConvolveInstruction(BaseModel):
    """Convolve input with HRF model"""

    Name: Literal['Convolve'] = 'Convolve'
    Input: List[str] = Field(..., description='Variables to convolve')
    Model: Optional[str] = Field(
        'spm',
        description='HRF model to use. Nilearn: spm, glover, fir. FSL: Double-Gamma HRF, Gamma HRF, Custom basis set, Gamma basis set, Sine basis set, FIR basis set. AFNI: BLOCK, GAM, TWOGAM, SPMG1, WAV, MION',
    )
    Derivative: Optional[bool] = Field(False, description='Include temporal derivative')
    Dispersion: Optional[bool] = Field(
        False, description='Include dispersion derivative'
    )
    FirDelays: Optional[List[float]] = Field(
        None, description='FIR delays (used only if model is fir)'
    )

    @field_validator('Model')
    @classmethod
    def validate_model(cls, v):
        """Validate that Model is one of the allowed values"""
        valid_models = [
            # Nilearn models
            'spm',
            'glover',
            'fir',
            # FSL models
            'Double-Gamma HRF',
            'Gamma HRF',
            'Custom basis set',
            'Gamma basis set',
            'Sine basis set',
            'FIR basis set',
            # AFNI models
            'BLOCK',
            'GAM',
            'TWOGAM',
            'SPMG1',
            'WAV',
            'MION',
        ]
        if v is not None and v not in valid_models:
            raise ValueError(f'Model must be one of: {", ".join(valid_models)}')
        return v


class CopyInstruction(BaseModel):
    """Copy or clone variables"""

    Name: Literal['Copy'] = 'Copy'
    Input: List[str] = Field(..., description='Variables to copy')
    Output: List[str] = Field(..., description='Output variable names')


class DeleteInstruction(BaseModel):
    """Delete variables from namespace"""

    Name: Literal['Delete'] = 'Delete'
    Input: List[str] = Field(..., description='Variables to delete')


class DemeanInstruction(BaseModel):
    """Mean-centers the input column(s)"""

    Name: Literal['Demean'] = 'Demean'
    Input: List[str] = Field(..., description='Variables to demean')
    Output: Optional[List[str]] = Field(None, description='Output variable names')


class DropNaInstruction(BaseModel):
    """Drop rows with missing values"""

    Name: Literal['DropNa'] = 'DropNa'
    Input: List[str] = Field(..., description='Variables to check for missing values')
    Output: Optional[List[str]] = Field(None, description='Output variable names')


class FactorInstruction(BaseModel):
    """Convert variables to factors (dummy-coded categorical variables)"""

    Name: Literal['Factor'] = 'Factor'
    Input: List[str] = Field(..., description='Variables to dummy-code')
    Prefix: Optional[List[str]] = Field(
        None,
        description='Prefix for factor levels. Length must match Input list. If unspecified, uses original column name as prefix (e.g., "condition.A", "condition.B")',
    )
    Constraint: Optional[str] = Field(
        'none',
        description='Constraint for dummy variables: "none" (N dummies), "drop_one" (N-1 dummies), "mean_zero" (N-1 dummies with mean-zero constraint)',
    )
    RefLevel: Optional[str] = Field(
        None,
        description='Reference level for "drop_one" and "mean_zero" constraints. Default: first level alphabetically',
    )
    Sep: Optional[str] = Field(
        '.',
        description='Separator between variable name and level (e.g., "condition.A")',
    )

    @field_validator('Constraint')
    @classmethod
    def validate_constraint(cls, v):
        """Validate that Constraint is one of the allowed values"""
        if v is not None and v not in ['none', 'drop_one', 'mean_zero']:
            raise ValueError('Constraint must be one of: none, drop_one, mean_zero')
        return v

    @field_validator('Prefix')
    @classmethod
    def validate_prefix_length(cls, v, info):
        """Validate that Prefix length matches Input length"""
        if v is not None and 'Input' in info.data:
            input_length = len(info.data['Input'])
            if len(v) != input_length:
                raise ValueError(
                    f'Prefix length ({len(v)}) must match Input length ({input_length})'
                )
        return v


class FilterInstruction(BaseModel):
    """Subsets rows using a boolean expression."""

    Name: Literal['Filter'] = 'Filter'
    Input: List[str] = Field(..., description='Variables to filter')
    Output: Optional[List[str]] = Field(None, description='Output variable names')
    Query: str = Field(..., description='Boolean expression used to filter')
    By: Optional[Union[str, List[str]]] = Field(
        None, description='Name of column to group filter operation by'
    )


class NotInstruction(BaseModel):
    """Returns the logical negation of the input column(s)"""

    Name: Literal['Not'] = 'Not'
    Input: List[str] = Field(..., description='Variables for NOT operation')
    Output: Optional[List[str]] = Field(None, description='Output variable names')


class OrInstruction(BaseModel):
    """Logical OR operation"""

    Name: Literal['Or'] = 'Or'
    Input: List[str] = Field(..., description='Variables for OR operation')
    Output: str = Field(..., description='Output variable name')


class OrthogonalizeInstruction(BaseModel):
    """Orthogonalize variable(s) with respect to other variables"""

    Name: Literal['Orthogonalize'] = 'Orthogonalize'
    Input: List[str] = Field(
        ..., description='Variables to orthogonalize (each orthogonalized individually)'
    )
    Output: Optional[List[str]] = Field(None, description='Output variable names')
    Wrt: List[str] = Field(
        ..., description='Variables to orthogonalize with respect to (required)'
    )


class ProductInstruction(BaseModel):
    """Compute rows-wise product of variables"""

    Name: Literal['Product'] = 'Product'
    Input: List[str] = Field(..., description='Variables to multiply')
    Output: List[str] = Field(..., description='Output variable names')


class ReplaceInstruction(BaseModel):
    """Replace values in the values, onset, or duration attributes"""

    Name: Literal['Replace'] = 'Replace'
    Input: List[str] = Field(..., description='Variables to replace values in')
    Output: Optional[List[str]] = Field(None, description='Output variable names')
    Replace: Dict[str, Any] = Field(
        ..., description='Replacement mapping (old_value: new_value)'
    )
    Attribute: Optional[str] = Field(
        'value', description='Attribute to replace: value, onset, or duration'
    )

    @field_validator('Attribute')
    @classmethod
    def validate_attribute(cls, v):
        """Validate that Attribute is one of the allowed values"""
        if v is not None and v not in ['value', 'onset', 'duration']:
            raise ValueError('Attribute must be one of: value, onset, duration')
        return v


class ScaleInstruction(BaseModel):
    """Scale variables"""

    Name: Literal['Scale'] = 'Scale'
    Input: List[str] = Field(..., description='Variables to scale')
    Output: Optional[List[str]] = Field(None, description='Output variable names')
    Demean: Optional[bool] = Field(True, description='Remove mean before scaling')
    Rescale: Optional[bool] = Field(True, description='Rescale to unit variance')
    ReplaceNa: Optional[str] = Field(
        None, description='Whether/when to replace missing values with 0'
    )


class SelectInstruction(BaseModel):
    """Select specific variables to retain for subsequent analysis"""

    Name: Literal['Select'] = 'Select'
    Input: List[str] = Field(..., description='Variables to retain')


class SplitInstruction(BaseModel):
    """Split a variable into N variables as defined by the levels of one or more other variables."""

    Name: Literal['Split'] = 'Split'
    Input: List[str] = Field(..., description='Variables to split')
    Output: Optional[List[str]] = Field(None, description='Output variable names')
    By: Union[str, List[str]] = Field(
        ..., description='Name(s) of variable(s) to split on'
    )


class SumInstruction(BaseModel):
    """Compute (optionally weighted) sum of variables"""

    Name: Literal['Sum'] = 'Sum'
    Input: List[str] = Field(..., description='Variables to sum')
    Output: List[str] = Field(..., description='Output variable names')
    Weights: Optional[List[float]] = Field(
        None,
        description='Optional weights for each variable. If provided, length must match Input length',
    )


class ThresholdInstruction(BaseModel):
    """Apply threshold to variables"""

    Name: Literal['Threshold'] = 'Threshold'
    Input: List[str] = Field(..., description='Variables to threshold')
    Output: Optional[List[str]] = Field(None, description='Output variable names')
    Threshold: Optional[float] = Field(0.0, description='Threshold value')
    Binarize: Optional[bool] = Field(False, description='Binarize output')
    Above: Optional[bool] = Field(True, description='Threshold above or below')
    Signed: Optional[bool] = Field(True, description='Use signed threshold')


class ToDenseInstruction(BaseModel):
    """Convert sparse variables to dense format"""

    Name: Literal['ToDense'] = 'ToDense'
    Input: List[str] = Field(..., description='Variables to convert to dense')
    Output: Optional[List[str]] = Field(None, description='Output variable names')
    SamplingRate: Optional[float] = Field(
        10.0, description='Sampling rate to use for densified variable'
    )


class GroupInstruction(BaseModel):
    """Creates a new variable group that can be used as an alias for the named variables"""

    Name: Literal['Group'] = 'Group'
    Input: List[str] = Field(
        ..., description='Names of variables to include in the group'
    )
    GroupName: str = Field(..., description='Name of the new variable group')


class LagInstruction(BaseModel):
    """Returns a variable that is lagged by a specified number of time points"""

    Name: Literal['Lag'] = 'Lag'
    Input: List[str] = Field(..., description='Variables to lag')
    Output: Optional[List[str]] = Field(None, description='Output variable names')
    Shift: Optional[float] = Field(1.0, description='Number of places to shift values')
    Order: Optional[int] = Field(3, description='Order of spline interpolation')
    Mode: Optional[str] = Field('nearest', description='Mode for extending boundaries')
    Constant: Optional[float] = Field(0.0, description='Value to fill past edges')
    Difference: Optional[bool] = Field(False, description='Calculate difference')


class RenameInstruction(BaseModel):
    """Rename a variable"""

    Name: Literal['Rename'] = 'Rename'
    Input: List[str] = Field(..., description='Variables to rename')
    Output: List[str] = Field(..., description='New variable names')


class ResampleInstruction(BaseModel):
    """Resamples one or more columns to a specified sampling rate"""

    Name: Literal['Resample'] = 'Resample'
    Input: List[str] = Field(..., description='Variables to resample')
    Output: Optional[List[str]] = Field(None, description='Output variable names')
    SamplingRate: Optional[float] = Field(10, description='Sampling frequency in hertz')


# Union type for all transformation instructions (only pybids transformations)
TransformationInstruction = Union[
    AndInstruction,
    AssignInstruction,
    ConvolveInstruction,
    CopyInstruction,
    DemeanInstruction,
    DeleteInstruction,
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
]


def get_available_transformations() -> List[str]:
    """Get list of available transformation types (only pybids transformations)"""
    return [
        'And',
        'Assign',
        'Convolve',
        'Copy',
        'Demean',
        'Delete',
        'DropNa',
        'Factor',
        'Filter',
        'Group',
        'Lag',
        'Not',
        'Or',
        'Orthogonalize',
        'Product',
        'Rename',
        'Replace',
        'Resample',
        'Scale',
        'Select',
        'Split',
        'Sum',
        'Threshold',
        'ToDense',
    ]
