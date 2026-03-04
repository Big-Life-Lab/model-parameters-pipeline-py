"""Center transformation step.

Centers variables by subtracting a specified center value from original
variables.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from model_parameters_pipeline._utils import verify_columns

if TYPE_CHECKING:
    from model_parameters_pipeline.pipeline import ModelPipeline


def run_step_center(mod: ModelPipeline, file: str | Path) -> list[str]:
    """Run center transformation step.

    Args:
        mod: ModelPipeline instance (mutated in place).
        file: Path to center step specification CSV.

    Returns:
        List of output column names created by this step.
    """
    mod._add_file(file)
    step_data = mod._get_file(file)

    verify_columns(
        step_data,
        ["origVariable", "centerValue", "centeredVariable"],
        "center step file",
        file,
    )

    output_columns: list[str] = []

    for _, row in step_data.iterrows():
        orig_variable = row["origVariable"]
        center_value = row["centerValue"]
        centered_variable = row["centeredVariable"]

        mod.data[centered_variable] = mod.data[orig_variable] - center_value
        output_columns.append(centered_variable)

    return output_columns
