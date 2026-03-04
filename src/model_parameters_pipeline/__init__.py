"""Model Parameters Pipeline.

A Python package for applying sequential data transformations according to the
Model Parameters specification developed by Big Life Lab.

Usage::

    from model_parameters_pipeline import ModelPipeline

    pipeline = ModelPipeline("path/to/model-export.csv")
    pipeline.run(dat="path/to/input-data.csv")
    result = pipeline.get_output(mode="output")
"""

from model_parameters_pipeline.pipeline import ModelPipeline, StepInfo

__all__ = [
    "ModelPipeline",
    "StepInfo",
]
