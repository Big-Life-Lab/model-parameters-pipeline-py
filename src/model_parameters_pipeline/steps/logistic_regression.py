"""Logistic regression transformation step.

Applies logistic regression by multiplying variables by coefficients,
summing, and applying the logistic function (1 / (1 + exp(-x))).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from model_parameters_pipeline._utils import (
    get_unused_column,
    verify_columns,
)

if TYPE_CHECKING:
    from model_parameters_pipeline.pipeline import ModelPipeline


def run_step_logistic_regression(
    mod: ModelPipeline, file: str | Path
) -> list[str]:
    """Run logistic regression transformation step.

    Args:
        mod: ModelPipeline instance (mutated in place).
        file: Path to logistic step specification CSV.

    Returns:
        List containing the single output column name.
    """
    mod._add_file(file)
    step_data = mod._get_file(file)

    verify_columns(
        step_data,
        ["variable", "coefficient"],
        "logistic step file",
        file,
    )

    # Create initial logistic output column (initialized to 0)
    logistic_col = get_unused_column(mod.data, "logistic_")
    logistic_values = np.zeros(len(mod.data))

    for _, row in step_data.iterrows():
        variable = row["variable"]
        coefficient = row["coefficient"]

        if variable == "Intercept":
            logistic_values = logistic_values + coefficient
        else:
            logistic_values = logistic_values + mod.data[variable].to_numpy() * coefficient

    # Apply the logistic function
    logistic_values = 1 / (1 + np.exp(-logistic_values))

    mod.data[logistic_col] = logistic_values

    return [logistic_col]
