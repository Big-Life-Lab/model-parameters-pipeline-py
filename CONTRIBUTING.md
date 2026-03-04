# Contributing to Model Parameters Pipeline

Thank you for your interest in contributing to the Model Parameters Pipeline!
This document outlines the guidelines for contributing to this project.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a
welcoming environment for contributors of all backgrounds and experience levels.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on
[GitHub](https://github.com/Big-Life-Lab/model-parameters-pipeline-py/issues) with:

- A clear description of the problem
- A minimal reproducible example
- Your Python version and package version

### Suggesting Features

Feature requests are welcome. Open an issue describing:

- The use case you are trying to address
- How the proposed feature would work
- Any relevant references to the [Model Parameters
  specification](https://big-life-lab.github.io/model-parameters/)

### Submitting Changes

1. Fork the repository and create a branch from `main`
2. Make your changes, following the code style guidelines below
3. Add or update tests as needed
4. Run `pytest` to ensure all tests pass
5. Submit a pull request with a clear description of your changes

## Code Style

Key style conventions:

- Use `snake_case` for variable and function names
- Internal (non-public) methods on `ModelPipeline` are prefixed with `_` (e.g.,
  `_add_file`)
- Step functions remain as standalone functions in their own modules under
  `src/model_parameters_pipeline/steps/`
- Use type hints for all function signatures
- Document all public classes and functions using Google-style docstrings

## Running Tests

```bash
pytest
```

To regenerate expected test outputs after changing a step's behaviour:

```python
# From the project root
exec(open("tests/generate_step_tests_expected.py").read())
generate_step_tests_expected()
```

## Package Structure

- `src/model_parameters_pipeline/` - Source package
  - `pipeline.py` - `ModelPipeline` class with core pipeline logic
  - `_utils.py` - Standalone utility functions (string parsing, path handling,
    RCS calculations)
  - `steps/` - One module per transformation step (`{stepname}.py`)
- `tests/` - Unit tests and test data
  - `testdata/` - Test CSV files

---

## Adding a New Transformation Step

See the full guide in the [project
documentation](https://big-life-lab.github.io/model-parameters-pipeline-py/adding-a-step.html).
