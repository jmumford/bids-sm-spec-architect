"""
To begin, I'm using this: https://github.com/bids-standard/stats-models/blob/main/bsmschema/bsmschema/models.py

The objects defined here are nested as follows:

* :py:class:`BIDSStatsModel`
   * :py:class:`Node`
      * :py:class:`Transformations`
      * :py:class:`Model`
         * :py:class:`HRF`
         * :py:class:`Options`
      * :py:class:`Contrast`
      * :py:class:`DummyContrasts`
   * :py:class:`Edge`

Note that these are the structured and validatable objects.
"""

import sys
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

__all__ = [
    'BIDSStatsModel',
    'Node',
    'Edge',
    'Transformations',
    'Model',
    'HRF',
    'Options',
    'Contrast',
    'DummyContrasts',
]

# Hack to avoid unnecessary verbosity when generating documentation
# Has no impact on emitted JSON, only on whether Python will attempt to cast instead of error
if not TYPE_CHECKING and 'sphinxcontrib.autodoc_pydantic' in sys.modules:
    StrictStr = str  # noqa: F811
    StrictInt = int  # noqa: F811
    StrictFloat = float  # noqa: F811
else:
    from pydantic import StrictFloat, StrictInt, StrictStr

# Notes
# HRF model parameters are unclear how to specify
# Transformation instructions should be doable (if tedious), but unclear
# how to make the restriction to them contingent on Transformer == "pybids-transforms-v1"
# Skipping Variance structure and Error distribution for now

# Controlled vocabularies

NodeLevel = Literal[
    'Run',
    'Session',
    'Subject',
    'Dataset',
]

ModelType = Literal[
    'glm',
    'meta',
]

TransformerID = Literal['pybids-transforms-v1',]

Aggregate = Literal[
    'none',
    'mean',
    'pca',
]

StatisticalTest = Literal[
    'pass',
    't',
    'F',
]

# Aliases
Filter = Dict[StrictStr, List[Any]]
VariableList = List[Union[Literal[1], StrictStr]]
Weights = List[Union[StrictInt, StrictFloat, StrictStr]]

# Python 3.10 at least weirdly annotates "X: Optional[X] = None" as NoneType
OptionalFilter = Optional[Filter]
OptionalAggregate = Optional[Aggregate]


class _BSMBase(BaseModel):
    # Docstring missing to avoid polluting every object description with this field
    # This permits users to write comments on objects.
    Description: Optional[str] = None

    class Config:
        extra = Extra.forbid


class BIDSStatsModelTopMatter(_BSMBase):
    """Top level options for the BIDS Stats Model"""

    Name: StrictStr
    """A name identifying the model, ideally short.
    While no hard constraints are imposed on the specific format of the name,
    each model's name should be unique for any given BIDS project
    (i.e., if a single BIDS project contains multiple model specifications in different files and/or folders,
    care should be taken to ensure that each model has a unique name)."""

    BIDSModelVersion: StrictStr
    """A string identifying the version of the specification adhered to.
    Note this is different from BIDSVersion"""
