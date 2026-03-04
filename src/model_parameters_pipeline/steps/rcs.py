"""Restricted cubic spline transformation step.

Creates restricted cubic spline (RCS) transformations using specified knot
positions.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from model_parameters_pipeline._utils import (
    get_rcs,
    get_string_parts,
    verify_columns,
)

if TYPE_CHECKING:
    from model_parameters_pipeline.pipeline import ModelPipeline


def run_step_rcs(mod: ModelPipeline, file: str | Path) -> list[str]:
    """Run restricted cubic spline transformation step.

    Args:
        mod: ModelPipeline instance (mutated in place).
        file: Path to RCS step specification CSV.

    Returns:
        List of output column names created by this step.
    """
    mod._add_file(file)
    step_data = mod._get_file(file)

    verify_columns(
        step_data,
        ["variable", "rcsVariables", "knots"],
        "rcs step file",
        file,
    )

    output_columns: list[str] = []

    for _, row in step_data.iterrows():
        variable = row["variable"]
        rcs_variables = get_string_parts(row["rcsVariables"])
        knots = [float(k) for k in get_string_parts(row["knots"])]

        # Calculate RCS basis functions
        vals = get_rcs(mod.data[variable], knots)

        # Assign each column to the corresponding variable name
        for col_idx, rcs_var in enumerate(rcs_variables):
            mod.data[rcs_var] = vals[:, col_idx]

        output_columns.extend(rcs_variables)

    return output_columns
