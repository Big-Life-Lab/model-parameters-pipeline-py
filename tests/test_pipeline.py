"""Integration tests for the model parameters pipeline."""

import os
import shutil
import tempfile

import numpy as np
import pandas as pd
import pytest

from model_parameters_pipeline import ModelPipeline

from .conftest import TESTDATA_DIR, get_htnport_paths, run_test_data


@pytest.mark.parametrize("sex", ["female", "male"])
def test_pipeline_matches_predicted_risk_with_htnport(sex: str) -> None:
    """Model pipeline matches predicted risk with HTNPoRT."""
    paths = get_htnport_paths(sex)

    pipeline = ModelPipeline(str(paths["model_export_file"]))
    pipeline.run(dat=str(paths["data_file"]))
    output_data = pipeline.get_output()

    validation_data = pd.read_csv(paths["data_file"])

    np.testing.assert_allclose(
        output_data.to_numpy().flatten(),
        validation_data["predicted_risk"].to_numpy(),
        atol=1e-6,
        rtol=0,
        err_msg=f"HTNPoRT {sex} predicted risk mismatch",
    )


@pytest.mark.parametrize("sex", ["female", "male"])
def test_pipeline_works_with_dataframes(sex: str) -> None:
    """Model pipeline works with dataframes (instead of files)."""
    paths = get_htnport_paths(sex)

    # Run with dataframe
    pipeline = ModelPipeline(str(paths["model_export_file"]))
    input_df = pd.read_csv(paths["data_file"])
    pipeline.run(dat=input_df)
    output_data = pipeline.get_output(mode="full")

    # Run with file names
    pipeline2 = ModelPipeline(str(paths["model_export_file"]))
    pipeline2.run(dat=str(paths["data_file"]))
    output_data2 = pipeline2.get_output(mode="full")

    pd.testing.assert_frame_equal(
        output_data.reset_index(drop=True),
        output_data2.reset_index(drop=True),
        check_dtype=False,
    )


def test_transformation_steps_work() -> None:
    """All transformation steps work correctly."""
    root_dir = TESTDATA_DIR / "step-tests"
    for cur_dir in sorted(root_dir.iterdir()):
        if cur_dir.is_dir():
            run_test_data(cur_dir.name, "test-data.csv")


def test_sandbox_path_allows_files_within_sandbox() -> None:
    """sandbox_path allows files within the sandbox."""
    paths = get_htnport_paths("female")
    # Should not raise
    ModelPipeline(
        str(paths["model_export_file"]),
        sandbox_path=str(paths["root_dir"]),
    )


def test_sandbox_path_raises_error_for_files_outside_sandbox() -> None:
    """sandbox_path raises an error for files outside the sandbox."""
    paths = get_htnport_paths("female")
    with pytest.raises(ValueError):
        ModelPipeline(
            str(paths["model_export_file"]),
            sandbox_path=tempfile.mkdtemp(),
        )


def test_sandbox_path_null_imposes_no_restriction() -> None:
    """sandbox_path = None imposes no restriction."""
    paths = get_htnport_paths("female")
    # Should not raise
    ModelPipeline(
        str(paths["model_export_file"]),
        sandbox_path=None,
    )


def test_sandbox_path_prefix_match_without_trailing_slash_rejected() -> None:
    """sandbox_path prefix match without trailing slash is rejected.

    Guards against naive startsWith() that omits trailing slash. Given:
        model files in:  <base>/htnport-reduced/
        sandbox_path:    <base>/htnport-reduce   (no trailing slash)
    A bare startsWith() would incorrectly return True.
    """
    base_tmp = tempfile.mkdtemp(prefix="sandbox_prefix_test_")
    try:
        # Copy all HTNPoRT female model files into <base_tmp>/htnport-reduced/
        model_dir = os.path.join(base_tmp, "htnport-reduced")
        os.makedirs(model_dir)
        src_paths = get_htnport_paths("female")
        for f in src_paths["root_dir"].iterdir():
            if f.is_file():
                shutil.copy2(str(f), model_dir)

        model_export_file = os.path.join(
            model_dir, src_paths["model_export_file"].name
        )

        # Create <base_tmp>/htnport-reduce/ -- sibling, not parent
        sandbox_dir = os.path.join(base_tmp, "htnport-reduce")
        os.makedirs(sandbox_dir)

        with pytest.raises(ValueError):
            ModelPipeline(model_export_file, sandbox_path=sandbox_dir)
    finally:
        shutil.rmtree(base_tmp)
