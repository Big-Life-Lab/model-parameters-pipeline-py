"""Generate expected output for model parameters step tests.

This script generates expected output files for unit tests of the model
parameters pipeline steps. It iterates through subdirectories in the
tests/testdata/step-tests folder, runs the model pipeline on each test case,
and saves the results as expected output CSV files for comparison in pytest
unit tests.

Usage::

    # From the project root directory:

    # Generate expected output for all steps
    python -m tests.generate_step_tests_expected

    # Generate expected output for specific steps only
    python -m tests.generate_step_tests_expected dummy
    python -m tests.generate_step_tests_expected center rcs
"""

from __future__ import annotations

import argparse
from pathlib import Path

from model_parameters_pipeline import ModelPipeline

STEP_TESTS_DIR = Path(__file__).parent / "testdata" / "step-tests"


def generate_step_tests_expected(steps: list[str] | None = None) -> None:
    """Generate expected output files for step tests.

    Args:
        steps: List of step names to generate expected output for. If ``None``
            (default), generates output for all steps. Step names should be
            provided without the ``test-`` prefix (e.g., ``"dummy"``,
            ``"center"``, ``"rcs"``).
    """
    data_file = STEP_TESTS_DIR / "test-data.csv"

    if steps is not None:
        step_dirs = [f"test-{s}" for s in steps]
    else:
        step_dirs = None

    for cur_dir in sorted(STEP_TESTS_DIR.iterdir()):
        if not cur_dir.is_dir():
            continue
        if step_dirs is not None and cur_dir.name not in step_dirs:
            continue

        model_export_file = cur_dir / "test-model-export.csv"
        pipeline = ModelPipeline(str(model_export_file))
        pipeline.run(dat=str(data_file))
        output_data = pipeline.get_output(mode="full")

        output_file = cur_dir / "test-expected.csv"
        print(f"Saving expected output for {cur_dir.name}")
        output_data.to_csv(output_file, index=False)


def main() -> None:
    """CLI entry point for generating step test expected output."""
    parser = argparse.ArgumentParser(
        description="Generate expected output for step tests."
    )
    parser.add_argument(
        "steps",
        nargs="*",
        default=None,
        help=(
            'Step names to generate output for (without "test-" prefix). '
            "If omitted, generates output for all steps."
        ),
    )
    args = parser.parse_args()
    generate_step_tests_expected(args.steps or None)


if __name__ == "__main__":
    main()
