"""
Enhanced Pydantic models for BIDS Stats Model validation.

These models extend the base models in assets/schema/models.py with additional
validation capabilities and GUI-friendly features.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from .transformation_models import TransformationInstruction


class BIDSModelVersion(str, Enum):
    """BIDS Model specification versions"""

    V1_0_0 = '1.0.0'


class Level(str, Enum):
    """Node levels in BIDS Stats Model"""

    RUN = 'Run'
    SESSION = 'Session'
    SUBJECT = 'Subject'
    DATASET = 'Dataset'


class ModelType(str, Enum):
    """Model types"""

    GLM = 'glm'
    META = 'meta'


class TestType(str, Enum):
    """Statistical test types"""

    PASS = 'pass'
    T = 't'
    F = 'F'


class TransformerType(str, Enum):
    """Transformation types"""

    PYBIDS_TRANSFORMS_V1 = 'pybids-transforms-v1'


class InputSpec(BaseModel):
    """Input specification for BIDS Stats Model"""

    subject: Optional[List[str]] = None
    run: Optional[List[str]] = None
    task: Optional[List[str]] = None
    session: Optional[List[str]] = None


class ModelSpec(BaseModel):
    """Model specification within a node"""

    Type: ModelType
    X: List[str] = Field(..., description='List of predictor variables')
    Formula: Optional[str] = None
    HRF: Optional[str] = None
    Options: Optional[str] = None
    Software: Optional[str] = None


class ContrastSpec(BaseModel):
    """Contrast specification"""

    Name: str
    ConditionList: List[str]
    Weights: List[float]
    Test: TestType


class DummyContrastSpec(BaseModel):
    """Dummy contrast specification"""

    Contrasts: Optional[List[str]] = None
    Test: TestType


class TransformationSpec(BaseModel):
    """Transformation specification"""

    Transformer: TransformerType = TransformerType.PYBIDS_TRANSFORMS_V1
    Instructions: List[TransformationInstruction]


class NodeSpec(BaseModel):
    """Node specification"""

    Level: Level
    Name: str
    GroupBy: List[str] = Field(..., description='Grouping variables')
    Model: ModelSpec
    Transformations: Optional[TransformationSpec] = None
    Contrasts: Optional[List[ContrastSpec]] = None
    DummyContrasts: Optional[DummyContrastSpec] = None

    @validator('GroupBy')
    def validate_group_by(cls, v):
        """Validate GroupBy values"""
        valid_values = ['run', 'session', 'subject', 'contrast']
        for value in v:
            if value not in valid_values:
                raise ValueError(
                    f'Invalid GroupBy value: {value}. Must be one of {valid_values}'
                )
        return v


class EdgeSpec(BaseModel):
    """Edge specification"""

    Source: str
    Destination: str
    Filter: Optional[Dict[str, Any]] = None


class BIDSStatsModelSpec(BaseModel):
    """Complete BIDS Stats Model specification"""

    Name: str
    BIDSModelVersion: BIDSModelVersion
    Description: Optional[str] = None
    Input: Optional[InputSpec] = None
    Nodes: List[NodeSpec]
    Edges: List[EdgeSpec]

    @validator('Nodes')
    def validate_nodes(cls, v):
        """Ensure at least one node exists"""
        if not v:
            raise ValueError('At least one node is required')
        return v

    @validator('Edges')
    def validate_edges(cls, v, values):
        """Validate edge references to existing nodes"""
        if 'Nodes' in values:
            node_names = [node.Name for node in values['Nodes']]
            for edge in v:
                if edge.Source not in node_names:
                    raise ValueError(f"Edge source '{edge.Source}' not found in nodes")
                if edge.Destination not in node_names:
                    raise ValueError(
                        f"Edge destination '{edge.Destination}' not found in nodes"
                    )
        return v


class DynamicBIDSValidator(BaseModel):
    """Validator that can incorporate BIDS dataset information"""

    available_subjects: Optional[List[str]] = Field(default_factory=list, exclude=True)
    available_tasks: Optional[List[str]] = Field(default_factory=list, exclude=True)
    available_runs: Optional[List[str]] = Field(default_factory=list, exclude=True)
    available_sessions: Optional[List[str]] = Field(default_factory=list, exclude=True)

    def validate_input_spec(self, input_spec: InputSpec) -> List[str]:
        """Validate input specification against available BIDS data"""
        errors = []

        if input_spec.subject:
            invalid_subjects = set(input_spec.subject) - set(self.available_subjects)
            if invalid_subjects:
                errors.append(
                    f'Subjects not found in dataset: {list(invalid_subjects)}'
                )

        if input_spec.task:
            invalid_tasks = set(input_spec.task) - set(self.available_tasks)
            if invalid_tasks:
                errors.append(f'Tasks not found in dataset: {list(invalid_tasks)}')

        if input_spec.run:
            invalid_runs = set(input_spec.run) - set(self.available_runs)
            if invalid_runs:
                errors.append(f'Runs not found in dataset: {list(invalid_runs)}')

        if input_spec.session:
            invalid_sessions = set(input_spec.session) - set(self.available_sessions)
            if invalid_sessions:
                errors.append(
                    f'Sessions not found in dataset: {list(invalid_sessions)}'
                )

        return errors
