# Model Parameters Pipeline (Python)

<!-- badges: start -->
[![test](https://github.com/Big-Life-Lab/model-parameters-pipeline-py/actions/workflows/test.yaml/badge.svg?branch=first)](https://github.com/Big-Life-Lab/model-parameters-pipeline-py/actions/workflows/test.yaml)
[![lint](https://github.com/Big-Life-Lab/model-parameters-pipeline-py/actions/workflows/lint.yaml/badge.svg?branch=first)](https://github.com/Big-Life-Lab/model-parameters-pipeline-py/actions/workflows/lint.yaml)
[![docs](https://github.com/Big-Life-Lab/model-parameters-pipeline-py/actions/workflows/sphinx.yaml/badge.svg?branch=first)](https://github.com/Big-Life-Lab/model-parameters-pipeline-py/actions/workflows/sphinx.yaml)
[![Pyodide wheel](https://github.com/Big-Life-Lab/model-parameters-pipeline-py/actions/workflows/release-pyodide-wheel.yaml/badge.svg)](https://github.com/Big-Life-Lab/model-parameters-pipeline-py/actions/workflows/release-pyodide-wheel.yaml)
<!-- badges: end -->

A Python package for applying sequential data transformations according to the
[Model Parameters
specification](https://github.com/Big-Life-Lab/model-parameters) developed by
Big Life Lab.

This is a Python port of the
[R package](https://github.com/Big-Life-Lab/model-parameters-pipeline) of the
same name.

Please view the [project
documentation](https://big-life-lab.github.io/model-parameters-pipeline-py/)
for full details on usage, contributing, and more code examples.

## Supported Transformations

- **Center**: Subtract a specified value from a variable
- **Dummy**: Create binary indicator variables for categorical values
- **Interaction**: Multiply variables together to create interaction terms
- **Restricted Cubic Splines (RCS)**: Create spline basis functions with
  specified knots
- **Logistic Regression**: Apply logistic regression coefficients and the
  sigmoid function

## Installation

### Prerequisites

- Python >= 3.10
- pandas >= 2.0
- numpy >= 1.24

### Install from source

```bash
pip install .
```

### Install in development mode

```bash
pip install -e ".[dev]"
```

## Usage

```python
from model_parameters_pipeline import ModelPipeline

# Step 1: Create the pipeline by loading model configuration
pipeline = ModelPipeline("path/to/model-export.csv")

# Step 2: Run the pipeline on input data (file path or DataFrame)
pipeline.run(dat="path/to/input-data.csv")

# Step 3: Get the output
output = pipeline.get_output(mode="output")  # Final step output only
output_full = pipeline.get_output(mode="full")  # All columns
```

### Using DataFrames

```python
import pandas as pd

input_data = pd.read_csv("path/to/input-data.csv")
pipeline.run(dat=input_data)
```

### Processing Multiple Datasets

```python
pipeline = ModelPipeline("path/to/model-export.csv")
for data_file in data_files:
    pipeline.run(dat=data_file)
    result = pipeline.get_output(mode="output")
    # Process result (a pandas DataFrame)
```

### Method Chaining

```python
pipeline = ModelPipeline("path/to/model-export.csv")
result = pipeline.run(dat="path/to/input-data.csv").get_output()
```

### Restricting File Access

```python
pipeline = ModelPipeline(
    "path/to/model-export.csv",
    sandbox_path="path/to/allowed/directory"
)
```

## Testing

Install the development dependencies, then run the test suite with pytest:

```bash
pip install -e ".[dev]"
pytest
```

## Documentation

Install the docs dependencies and build with Sphinx:

```bash
pip install -e ".[docs]"
sphinx-build -b html docs/ docs/_build/html
```

The generated HTML will be in `docs/_build/html/`. Open
`docs/_build/html/index.html` in a browser to view it.

Alternatively, use the Makefile:

```bash
cd docs
make html
```

## License

MIT

## Authors

Martin Wellman - [Big Life Lab](https://github.com/Big-Life-Lab)
