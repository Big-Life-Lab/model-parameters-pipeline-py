"""Dummy coding transformation step.

Creates dummy variables for categorical values, setting 1 when the
original variable equals the specified category value, 0 otherwise.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from model_parameters_pipeline._utils import verify_columns

if TYPE_CHECKING:
    from model_parameters_pipeline.pipeline import ModelPipeline


def run_step_dummy(mod: ModelPipeline, file: str | Path) -> list[str]:
    """Run dummy coding transformation step.

    Args:
        mod: ModelPipeline instance (mutated in place).
        file: Path to dummy step specification CSV.

    Returns:
        List of output column names created by this step.
    """
    mod._add_file(file)
    step_data = mod._get_file(file)

    verify_columns(
        step_data,
        ["origVariable", "catValue", "dummyVariable"],
        "dummy step file",
        file,
    )

    output_columns: list[str] = []

    for _, row in step_data.iterrows():
        orig_variable = row["origVariable"]
        cat_value = row["catValue"]
        dummy_variable = row["dummyVariable"]

        # Match R's type coercion: if the data column is numeric and
        # cat_value is a string, try to convert cat_value to numeric
        col_data = mod.data[orig_variable]
        if hasattr(col_data.dtype, "kind") and col_data.dtype.kind in ("i", "f", "u"):
            try:
                cat_value = type(col_data.iloc[0])(cat_value)
            except (ValueError, TypeError):
                pass

        mod.data[dummy_variable] = (col_data == cat_value).astype(int)
        output_columns.append(dummy_variable)

    return output_columns
