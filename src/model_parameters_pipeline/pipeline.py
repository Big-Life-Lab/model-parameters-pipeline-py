"""Model Parameters Pipeline.

This module provides the ``ModelPipeline`` class for preparing and running a
model parameters pipeline that applies sequential data transformations as
defined by the Model Parameters specification developed by Big Life Lab.

Workflow::

    pipeline = ModelPipeline("path/to/model-export.csv")
    pipeline.run(dat="path/to/input-data.csv")
    result = pipeline.get_output(mode="output")
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from model_parameters_pipeline._utils import (
    expand_and_normalize_path,
    file_relative_to_path,
    is_file_descendant_of,
    verify_columns,
)
from model_parameters_pipeline.steps.center import run_step_center
from model_parameters_pipeline.steps.dummy import run_step_dummy
from model_parameters_pipeline.steps.interaction import run_step_interaction
from model_parameters_pipeline.steps.logistic_regression import (
    run_step_logistic_regression,
)
from model_parameters_pipeline.steps.rcs import run_step_rcs


@dataclass
class StepInfo:
    """Information about a completed pipeline step."""

    step_name: str
    output_columns: list[str]


# Step dispatch table
_STEP_DISPATCH: dict[str, Callable[[ModelPipeline, str | Path], list[str]]] = {
    "center": run_step_center,
    "dummy": run_step_dummy,
    "interaction": run_step_interaction,
    "logistic-regression": run_step_logistic_regression,
    "rcs": run_step_rcs,
}


class ModelPipeline:
    """Model parameters pipeline for sequential data transformations.

    Loads and validates model configuration files, then applies transformation
    steps (centering, dummy coding, interactions, restricted cubic splines,
    and logistic regression) to input data.

    Args:
        model_export: File path to a model export CSV file. The model export
            must contain columns 'fileType' and 'filePath' that specify the
            locations of the variables and model-steps files. The directory
            containing the model export file is used as the root directory
            for resolving relative file paths.
        sandbox_path: If specified, all file paths referenced in the model
            parameters configuration files must be descendants of this
            directory. If any file resolves outside of sandbox_path, an error
            is raised. This prevents access to files outside the expected
            directory structure, which is useful when running on a server or
            other public-facing system. Note that this restriction does not
            apply to data files passed to ``run()``. Defaults to None (no
            restriction).

    Raises:
        ValueError: If required files or columns are missing, or if files
            are outside the sandbox path.

    Examples::

        # Basic usage
        pipeline = ModelPipeline("path/to/model-export.csv")
        pipeline.run(dat="path/to/input-data.csv")
        result = pipeline.get_output(mode="output")

        # Processing multiple datasets with the same model
        pipeline = ModelPipeline("path/to/model-export.csv")
        for data_file in data_files:
            pipeline.run(dat=data_file)
            result = pipeline.get_output(mode="output")

        # With sandbox path restriction
        pipeline = ModelPipeline(
            "path/to/model-export.csv",
            sandbox_path="path/to/allowed/directory",
        )
    """

    def __init__(
        self,
        model_export: str | Path,
        sandbox_path: Optional[str | Path] = None,
    ) -> None:
        self.sandbox_path: Optional[str] = (
            str(sandbox_path) if sandbox_path is not None else None
        )
        self.root_dir: Optional[str] = None
        self.model_export: Optional[pd.DataFrame] = None
        self.variables: Optional[pd.DataFrame] = None
        self.model_steps: Optional[pd.DataFrame] = None
        self.predictor_variables: list[str] = []
        self.files: dict[str, pd.DataFrame] = {}
        self.data: Optional[pd.DataFrame] = None
        self.steps_info: list[StepInfo] = []

        self._prepare(model_export)

    def _prepare(self, model_export: str | Path) -> None:
        """Load and validate model configuration files.

        Args:
            model_export: File path to a model export CSV file.
        """
        # Get the root dir from the model_export path
        model_export_path = Path(model_export)
        self.root_dir = str(
            expand_and_normalize_path(str(model_export_path.parent))
        )

        # Load and validate model export file
        self._add_file(model_export)
        self.model_export = self._get_file(model_export)
        verify_columns(
            self.model_export,
            ["fileType", "filePath"],
            "model export file",
            model_export,
        )

        # Get the variables and model_steps files from the model export
        variables_row = self.model_export[
            self.model_export["fileType"] == "variables"
        ]
        variables_file = os.path.join(
            self.root_dir, variables_row["filePath"].iloc[0]
        )

        model_steps_row = self.model_export[
            self.model_export["fileType"] == "model-steps"
        ]
        model_steps_file = os.path.join(
            self.root_dir, model_steps_row["filePath"].iloc[0]
        )

        # Load and validate variables
        self._add_file(variables_file)
        self.variables = self._get_file(variables_file)
        verify_columns(
            self.variables,
            ["role", "variable"],
            "variables file",
            variables_file,
        )

        # Load and validate model steps
        self._add_file(model_steps_file)
        self.model_steps = self._get_file(model_steps_file)
        verify_columns(
            self.model_steps,
            ["step", "filePath"],
            "model steps file",
            None,
        )

        # Get predictor variables
        self.predictor_variables = self.variables.loc[
            self.variables["role"] == "Predictor", "variable"
        ].tolist()

        # Preload all files in the model steps
        for _, step_row in self.model_steps.iterrows():
            file_path = step_row["filePath"]
            if pd.isna(file_path) or str(file_path).strip() == "":
                continue
            file_path = os.path.join(self.root_dir, file_path)
            self._add_file(file_path)

    def run(self, dat: str | Path | pd.DataFrame) -> ModelPipeline:
        """Execute the transformation pipeline on input data.

        Applies each transformation step defined in the model steps file in
        sequence, modifying the data accordingly.

        Args:
            dat: Either a file path to a CSV file, or a pandas DataFrame.
                The data must contain all columns specified as predictors in
                the variables file.

        Returns:
            This ``ModelPipeline`` instance (for method chaining).

        Raises:
            ValueError: If required predictor columns are missing from the
                data, or if an unrecognized step type is encountered.
            FileNotFoundError: If dat is a file path that does not exist.

        Examples::

            pipeline = ModelPipeline("path/to/model-export.csv")

            # Run with a file path
            pipeline.run(dat="path/to/input-data.csv")

            # Run with a DataFrame
            import pandas as pd
            input_data = pd.read_csv("path/to/input-data.csv")
            pipeline.run(dat=input_data)
        """
        # Load data if it is a file path
        if isinstance(dat, (str, Path)):
            dat_path = Path(dat).resolve(strict=True)
            dat = pd.read_csv(dat_path)

        # Check that all predictor variables exist in the data
        missing_columns = [
            col for col in self.predictor_variables if col not in dat.columns
        ]
        if missing_columns:
            missing_str = ", ".join(f"'{col}'" for col in missing_columns)
            raise ValueError(
                f"The following columns specified in the "
                f"variables file are missing in the data: {missing_str}"
            )

        self.data = dat[self.predictor_variables].copy()
        self.steps_info = []

        # Run each step in the model steps file
        for i, (_, step_row) in enumerate(self.model_steps.iterrows()):
            step_name = step_row["step"]

            file_path = step_row["filePath"]
            if pd.isna(file_path) or str(file_path).strip() == "":
                raise ValueError(
                    f"File path is empty for step #{i + 1}: {step_name}"
                )
            file_path = os.path.join(self.root_dir, file_path)

            step_fn = _STEP_DISPATCH.get(step_name)
            if step_fn is None:
                raise ValueError(
                    f"Unrecognized or unimplemented step type for step "
                    f"#{i + 1}: {step_name}"
                )

            output_columns = step_fn(self, file_path)

            self.steps_info.append(
                StepInfo(step_name=step_name, output_columns=output_columns)
            )

        return self

    def get_output(self, mode: str = "output") -> pd.DataFrame:
        """Extract a DataFrame from the pipeline results.

        If multiple calls to ``run()`` have been made, only the results of
        the last call will be returned.

        Args:
            mode: What data to return:

                - ``"output"``: Only the final output columns from the last
                  transformation step (e.g., the logistic prediction column
                  when the last step is logistic-regression).
                - ``"full"``: All columns including the original predictor
                  columns plus every new column created by each
                  transformation step.

                Defaults to ``"output"``.

        Returns:
            A DataFrame containing the requested data.

        Raises:
            ValueError: If mode is not ``"output"`` or ``"full"``.

        Examples::

            pipeline = ModelPipeline("path/to/model-export.csv")
            pipeline.run(dat="path/to/input-data.csv")

            # Default: only the final step's output columns
            output = pipeline.get_output()

            # Full: all columns including intermediate transformations
            output_full = pipeline.get_output(mode="full")
        """
        if mode == "output":
            output_columns = self.steps_info[-1].output_columns
            return self.data[output_columns]
        elif mode == "full":
            return self.data
        else:
            raise ValueError(
                f'Unrecognized value for "mode" in get_output. '
                f'Must be one of "output" or "full", instead found "{mode}"'
            )

    def _reportable_file(self, file: str | Path) -> str:
        """Get a file path safe to include in user-facing error messages.

        If ``sandbox_path`` is set, returns the path of ``file`` relative to
        the sandbox path, or just the filename if ``file`` is not inside the
        sandbox path or if it does not exist. If ``sandbox_path`` is not set,
        returns ``file`` unchanged.

        Args:
            file: The file path to make reportable.

        Returns:
            A file path safe to display in error messages.
        """
        if self.sandbox_path is None:
            return str(file)
        return file_relative_to_path(file, self.sandbox_path)

    def _add_file(self, file: str | Path) -> None:
        """Load and add a CSV file to the file cache.

        Args:
            file: Path to CSV file to load.

        Raises:
            ValueError: If the file does not exist or is outside the
                sandbox path.
        """
        reportable = self._reportable_file(file)

        general_error_message = (
            f"The file does not exist or is outside of the sandbox path: "
            f"{reportable}"
        )

        normalized = expand_and_normalize_path(file)
        if normalized is None:
            if self.sandbox_path is None:
                raise ValueError(f"The file does not exist: {reportable}")
            else:
                raise ValueError(general_error_message)

        norm_key = str(normalized)
        if norm_key not in self.files:
            # Make sure the file is a descendant of the sandbox path
            if (
                self.sandbox_path is not None
                and not is_file_descendant_of(normalized, self.sandbox_path)
            ):
                raise ValueError(general_error_message)

            # Load and cache the file
            try:
                data = pd.read_csv(normalized)
                self.files[norm_key] = data
            except Exception:
                raise ValueError(f"Could not load the file {reportable}")

    def _get_file(self, file: str | Path) -> pd.DataFrame:
        """Retrieve a previously loaded file from the cache.

        Args:
            file: Path to file to retrieve.

        Returns:
            DataFrame from the file cache.

        Raises:
            ValueError: If the file was not previously added with
                ``_add_file()``.
        """
        normalized = expand_and_normalize_path(file)
        norm_key = str(normalized)
        if norm_key not in self.files:
            raise ValueError(
                f"The file must be added by calling "
                f"_add_file before calling _get_file: "
                f"{self._reportable_file(file)}"
            )
        return self.files[norm_key]
