"""Internal utility functions for the model parameters pipeline.

This module contains standalone utility functions for string manipulation,
data validation, path handling, and restricted cubic spline calculations.

Functions that operate on a ``ModelPipeline`` instance are defined as methods
on the ``ModelPipeline`` class in ``pipeline.py``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


def get_string_parts(s: str, split: str = ";") -> list[str]:
    """Split and trim string parts.

    Args:
        s: String to split.
        split: Delimiter character. Defaults to ";".

    Returns:
        List of trimmed string parts.
    """
    return [part.strip() for part in s.split(split)]


def get_unused_column(data: pd.DataFrame, column_prefix: str) -> str:
    """Find an unused column name in the data.

    Generates a unique column name by appending an integer to a prefix.
    Iteratively checks for column_prefix1, column_prefix2, etc. until
    finding a name that doesn't exist in the data.

    Args:
        data: DataFrame to check for existing column names.
        column_prefix: Prefix for the column name.

    Returns:
        An unused column name (e.g., "prefix1", "prefix2").
    """
    col_i = 1
    while True:
        cur_col = f"{column_prefix}{col_i}"
        if cur_col not in data.columns:
            return cur_col
        col_i += 1


def verify_columns(
    data: pd.DataFrame,
    columns: list[str],
    data_description: str,
    file: Optional[str | Path] = None,
) -> None:
    """Verify required columns exist in the data.

    Args:
        data: DataFrame to validate.
        columns: Required column names.
        data_description: Description of the data for error messages.
        file: Optional file path for error context.

    Raises:
        ValueError: If any required columns are missing.
    """
    missing_columns = [col for col in columns if col not in data.columns]
    if missing_columns:
        missing_str = ", ".join(f"'{col}'" for col in missing_columns)
        message = (
            f"The following columns are missing in the "
            f"{data_description}: {missing_str}"
        )
        if file is not None and str(file).strip():
            message = f"{message} in file {Path(file).name}"
        raise ValueError(message)


def expand_and_normalize_path(
    p: str | Path, add_trailing_slash: bool = False
) -> Optional[Path]:
    """Expand and normalize a file path.

    Symbolic links and ".." will be followed and expanded.

    Args:
        p: The path to expand and normalize.
        add_trailing_slash: If True, a trailing slash is appended. Useful for
            directory paths.

    Returns:
        The normalized Path, or None if the path is invalid or does not exist.
    """
    try:
        resolved = Path(p).resolve(strict=True)
    except (OSError, ValueError):
        return None

    if add_trailing_slash:
        # Return as string with trailing separator, then convert back
        s = str(resolved)
        if not s.endswith(os.sep):
            s = s + os.sep
        # We store it as a Path but the trailing slash is used in string
        # comparisons, so we return a special object. Since Path strips
        # trailing slashes, we handle this in is_file_descendant_of.
        return resolved

    return resolved


def is_file_descendant_of(file: Path, top_level_directory: str | Path) -> bool:
    """Check if a file is a descendant of a directory.

    Both paths are resolved to handle symbolic links and ".." components.

    Args:
        file: The path to the file to check.
        top_level_directory: The directory that ``file`` should be within.

    Returns:
        True if file is a descendant of top_level_directory, False otherwise.
        Returns False if either path does not exist.
    """
    norm_file = expand_and_normalize_path(file)
    norm_dir = expand_and_normalize_path(top_level_directory, add_trailing_slash=True)

    if norm_file is None or norm_dir is None:
        return False

    # Use string comparison with trailing separator to prevent prefix attacks
    dir_str = str(norm_dir)
    if not dir_str.endswith(os.sep):
        dir_str = dir_str + os.sep

    return str(norm_file).startswith(dir_str)


def file_relative_to_path(
    file: str | Path, relative_to_path: Optional[str | Path]
) -> str:
    """Format a file path relative to a reference path.

    This is for informational purposes to report to the user, hiding full
    system paths in error messages.

    Args:
        file: The file path to format.
        relative_to_path: The path to make the file relative to.

    Returns:
        The formatted file path. If either path doesn't exist or file is not
        a descendant of relative_to_path, returns just the basename.
    """
    if relative_to_path is not None:
        norm_rel = expand_and_normalize_path(
            relative_to_path, add_trailing_slash=True
        )
        if norm_rel is not None:
            rel_str = str(norm_rel)
            if not rel_str.endswith(os.sep):
                rel_str = rel_str + os.sep

            norm_file = expand_and_normalize_path(file)
            if norm_file is not None and str(norm_file).startswith(rel_str):
                return str(norm_file)[len(rel_str):]

        return Path(file).name

    return str(file)


def get_rcs(x: pd.Series, knots: list[float]) -> np.ndarray:
    """Calculate restricted cubic spline basis functions.

    Computes RCS basis functions for a given vector and knot positions.
    This implementation follows the algorithm from Hmisc::rcspline.eval.

    Args:
        x: Numeric values to transform.
        knots: Knot positions.

    Returns:
        2D numpy array with RCS basis functions as columns.
        Column 0 is the original x values, columns 1..k-2 are the spline
        basis functions.
    """
    x_vals = x.to_numpy(dtype=float)
    k = len(knots)

    # First column is the original x values
    result = [x_vals.copy()]

    for j in range(k - 2):
        kd = (knots[k - 1] - knots[0]) ** (2 / 3)

        vec1 = x_vals - knots[j]
        val2 = knots[k - 2] - knots[j]
        vec2 = x_vals - knots[k - 1]
        val3 = knots[k - 1] - knots[j]
        vec3 = x_vals - knots[k - 2]
        val4 = knots[k - 1] - knots[k - 2]

        vec_j = (
            np.maximum(vec1 / kd, 0) ** 3
            + (val2 * np.maximum(vec2 / kd, 0) ** 3) / val4
            - (val3 * np.maximum(vec3 / kd, 0) ** 3) / val4
        )

        result.append(vec_j)

    return np.column_stack(result)
