"""Shared test fixtures and helpers for the model parameters pipeline tests."""

from pathlib import Path

import pandas as pd

from model_parameters_pipeline import ModelPipeline

TESTDATA_DIR = Path(__file__).parent / "testdata"


def get_htnport_paths(sex: str) -> dict[str, Path]:
    """Construct file paths for HTNPoRT model files based on sex.

    Args:
        sex: "male" or "female".

    Returns:
        Dictionary with root_dir, data_file, model_steps_file,
        variables_file, and model_export_file paths.
    """
    root_dir = TESTDATA_DIR / "htnport-reduced"
    return {
        "root_dir": root_dir,
        "data_file": root_dir / f"HTNPoRT-{sex}-validation-data.csv",
        "model_steps_file": root_dir / f"HTNPoRT-{sex}-model-steps.csv",
        "variables_file": root_dir / f"HTNPoRT-{sex}-variables.csv",
        "model_export_file": root_dir / f"HTNPoRT-{sex}-model-export.csv",
    }


def run_test_data(dir_name: str, input_data_file: str) -> None:
    """Run test data through model pipeline and validate output.

    Args:
        dir_name: Test directory name within step-tests/.
        input_data_file: Input data file name.
    """
    root_dir = TESTDATA_DIR / "step-tests"
    data_file = root_dir / input_data_file
    model_export_file = root_dir / dir_name / "test-model-export.csv"

    pipeline = ModelPipeline(str(model_export_file))
    pipeline.run(dat=str(data_file))
    output_data = pipeline.get_output(mode="full")

    # Compare the pipeline output to the expected output
    valid_data_file = root_dir / dir_name / "test-expected.csv"
    valid_data = pd.read_csv(valid_data_file)

    pd.testing.assert_frame_equal(
        output_data.reset_index(drop=True),
        valid_data.reset_index(drop=True),
        check_dtype=False,
        atol=1e-10,
        obj=f"transformation step {dir_name}",
    )
