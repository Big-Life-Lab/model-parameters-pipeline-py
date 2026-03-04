"""Interaction term transformation step.

Creates interaction terms by multiplying specified variables together.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from model_parameters_pipeline._utils import (
    get_string_parts,
    verify_columns,
)

if TYPE_CHECKING:
    from model_parameters_pipeline.pipeline import ModelPipeline


def run_step_interaction(mod: ModelPipeline, file: str | Path) -> list[str]:
    """Run interaction transformation step.

    Args:
        mod: ModelPipeline instance (mutated in place).
        file: Path to interaction step specification CSV.

    Returns:
        List of output column names created by this step.
    """
    mod._add_file(file)
    step_data = mod._get_file(file)

    verify_columns(
        step_data,
        ["interactingVariables", "interactionVariable"],
        "interaction step file",
        file,
    )

    output_columns: list[str] = []

    for _, row in step_data.iterrows():
        interacting_variables = get_string_parts(row["interactingVariables"])
        interaction_variable = row["interactionVariable"]

        # Iteratively create the interaction variable
        mod.data[interaction_variable] = 1
        for var in interacting_variables:
            mod.data[interaction_variable] = (
                mod.data[interaction_variable] * mod.data[var]
            )
        output_columns.append(interaction_variable)

    return output_columns
