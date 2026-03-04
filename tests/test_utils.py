"""Unit tests for utility functions."""

import pandas as pd
import pytest

from model_parameters_pipeline import ModelPipeline
from model_parameters_pipeline._utils import (
    get_string_parts,
    get_unused_column,
    verify_columns,
)

from .conftest import get_htnport_paths


def test_add_file_and_get_file_work() -> None:
    """_add_file and _get_file work correctly."""
    female_paths = get_htnport_paths("female")
    female_data_file = str(female_paths["data_file"])
    female_expected_data = pd.read_csv(female_data_file)

    male_paths = get_htnport_paths("male")
    male_data_file = str(male_paths["data_file"])
    male_expected_data = pd.read_csv(male_data_file)

    # Use a real model export to construct a ModelPipeline, then test
    # _add_file/_get_file with additional files
    pipeline = ModelPipeline(str(female_paths["model_export_file"]))

    # The validation data file was not loaded during __init__, so add it now
    pipeline._add_file(female_data_file)
    test_data = pipeline._get_file(female_data_file)
    pd.testing.assert_frame_equal(test_data, female_expected_data)

    # Add and retrieve second file
    pipeline._add_file(male_data_file)
    test_data = pipeline._get_file(male_data_file)
    pd.testing.assert_frame_equal(test_data, male_expected_data)

    # First file should still be accessible
    test_data = pipeline._get_file(female_data_file)
    pd.testing.assert_frame_equal(test_data, female_expected_data)

    # Adding invalid file should raise
    with pytest.raises(ValueError):
        pipeline._add_file("___unused_name___.csv")

    # Adding already-added file should not raise
    pipeline._add_file(male_data_file)

    # Getting a file not added should raise on a fresh pipeline
    pipeline2 = ModelPipeline(str(male_paths["model_export_file"]))
    with pytest.raises(ValueError):
        pipeline2._get_file(female_data_file)


def test_verify_columns_works() -> None:
    """Utility function verify_columns works."""
    test_data = pd.DataFrame({
        "other": ["1", "2", "3"],
        "col_1": ["a", "b", "c"],
        "col_2": ["d", "e", "f"],
        "col_3": ["g", "h", "i"],
    })

    # Should not raise for existing columns
    verify_columns(test_data, ["col_1"], "test data")
    verify_columns(test_data, ["col_1", "col_2", "col_3"], "test data")

    # Should raise for missing columns
    with pytest.raises(ValueError):
        verify_columns(test_data, ["missing"], "test data")

    with pytest.raises(ValueError):
        verify_columns(test_data, ["col_1", "col_2", "bad"], "test data")


def test_get_unused_column_works() -> None:
    """Utility function get_unused_column works."""
    test_data = pd.DataFrame({
        "other": ["1", "2", "3"],
        "col_1": ["a", "b", "c"],
        "col_2": ["d", "e", "f"],
        "col_4": ["g", "h", "i"],
    })
    assert get_unused_column(test_data, "col_") == "col_3"


def test_get_string_parts_works() -> None:
    """Utility function get_string_parts works."""
    # Basic test with 3 parts
    expected = ["part1", "part2", "part3"]
    assert get_string_parts("part1;part2;part3", split=";") == expected

    # Test with a different split value
    assert get_string_parts("part1,part2,part3", split=",") == expected

    # Test with one part
    assert get_string_parts("part1", split=";") == ["part1"]

    # Test for trimming whitespace
    assert get_string_parts("part1 ;  part2 ;  part3", split=";") == expected
