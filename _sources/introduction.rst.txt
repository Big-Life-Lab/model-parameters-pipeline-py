Introduction
============

Overview
--------

The Model Parameters Pipeline is a Python package for applying transformations
to data according to the `Model Parameters
<https://github.com/Big-Life-Lab/model-parameters>`_ specification developed by
Big Life Lab. This package implements a pipeline for sequential data
transformations that are commonly used in predictive health models.

This guide will walk you through:

1. Understanding the Model Parameters specification
2. Setting up your model configuration files
3. Running the transformation pipeline
4. Working with the results

What is the Model Parameters Specification?
--------------------------------------------

The Model Parameters specification is a standardized way to define and apply
data transformations used in predictive algorithms. It was developed by Big Life
Lab for their predictive health models such as:

- **HTNPoRT**: Hypertension Population Risk Tool
- **DemPoRT**: Dementia Population Risk Tool
- **CVDPoRT**: Cardiovascular Disease Population Risk Tool
- **MPoRT**: Mortality Population Risk Tool

The specification uses CSV files to define transformations, making algorithms:

- **Transparent**: All parameters and transformations are documented in
  human-readable files
- **Portable**: The same model can be deployed across different platforms and
  programming languages
- **Reproducible**: Transformations are applied consistently

Supported Transformations
-------------------------

The pipeline supports five types of transformations:

1. **Center**: Subtracts a constant value from variables (e.g., age - 50)
2. **Dummy**: Creates binary indicator variables for categorical values
3. **Interaction**: Multiplies variables together to create interaction terms
4. **RCS**: Applies restricted cubic spline transformations for non-linear
   relationships
5. **Logistic Regression**: Applies logistic regression to generate predictions

Installation
------------

Prerequisites:

- Python >= 3.10
- pandas >= 2.0
- numpy >= 1.24

.. code-block:: bash

    # Install from GitHub (if published)
    pip install git+https://github.com/Big-Life-Lab/model-parameters-pipeline-py.git

    # Or install from local source
    pip install /path/to/model-parameters-pipeline-py

Install in development mode::

    pip install -e ".[dev]"

Basic Usage
-----------

The package uses a class-based workflow with three steps:

1. ``ModelPipeline(...)`` -- Load and validate model configuration files
2. ``.run(...)`` -- Apply transformations to data
3. ``.get_output(...)`` -- Extract results

.. code-block:: python

    from model_parameters_pipeline import ModelPipeline

    # Step 1: Create the pipeline (loads and validates configuration)
    pipeline = ModelPipeline("path/to/model-export.csv")

    # Step 2: Run the pipeline on your data
    pipeline.run(dat="path/to/input-data.csv")

    # Step 3: Extract the output as a DataFrame
    result = pipeline.get_output()

    # View the first few rows
    print(result.head())

Using DataFrames for Input Data
-------------------------------

You can pass a pandas DataFrame instead of a file path for the input data:

.. code-block:: python

    import pandas as pd

    # Create the pipeline
    pipeline = ModelPipeline("path/to/model-export.csv")

    # Load and preprocess your data
    input_data = pd.read_csv("path/to/input-data.csv")

    # Run pipeline with DataFrame
    pipeline.run(dat=input_data)

    # Extract the output
    result = pipeline.get_output()

This is useful when your data is already loaded or needs preprocessing.

Processing Multiple Datasets
-----------------------------

If you need to apply the same model to multiple datasets (e.g., processing
batches), reuse the pipeline object for better performance:

.. code-block:: python

    # Create the pipeline once -- configuration files are loaded and cached
    pipeline = ModelPipeline("path/to/model-export.csv")

    # Run on multiple datasets using method chaining
    result1 = pipeline.run(dat="batch1_data.csv").get_output()
    result2 = pipeline.run(dat="batch2_data.csv").get_output()
    result3 = pipeline.run(dat="batch3_data.csv").get_output()

This avoids re-reading and parsing the configuration files for each batch.

Method Chaining
---------------

``run()`` returns ``self``, so you can chain calls:

.. code-block:: python

    pipeline = ModelPipeline("path/to/model-export.csv")
    result = pipeline.run(dat="path/to/input-data.csv").get_output()

Restricting File Access with ``sandbox_path``
---------------------------------------------

When running on a server or any public-facing system, the model configuration
files can reference arbitrary paths on the filesystem. Use the ``sandbox_path``
parameter to restrict which files the pipeline is allowed to read.

.. code-block:: python

    pipeline = ModelPipeline(
        "path/to/model-files/model-export.csv",
        sandbox_path="path/to/model-files/",
    )

When ``sandbox_path`` is set, every file referenced inside the model
configuration (the model export, variables file, model-steps file, and any
step parameter files) must be located within that directory. If any path
resolves outside of it, the constructor raises a ``ValueError``.

This restriction applies only to the **model configuration files** -- it does
not affect data files passed to ``run()``. It does, however, affect the model
export file passed to the constructor.

**When to use it:**

- You expose the pipeline as a web service or API and the model export path
  (or paths inside it) could be influenced by user input.
- You want to enforce that a model package stays self-contained within a
  specific directory and never reads files from elsewhere on the filesystem.

**When you can omit it:**

- You are running the pipeline locally in a trusted environment where all
  model files are under your control and path traversal is not a concern.
  The default (``sandbox_path=None``) imposes no restriction.

Working with Results
--------------------

``run()`` applies transformations in place and returns ``self`` for method
chaining. Use ``get_output()`` to extract a DataFrame. The ``mode`` argument
(default ``"output"``) controls what columns are returned:

- ``"output"``: only the columns produced by the final transformation step
- ``"full"``: all columns -- original predictors plus every intermediate and
  output column

.. code-block:: python

    pipeline.run(dat="path/to/input-data.csv")

    # Default mode: only the final step's output columns
    output = pipeline.get_output()

    # Full mode: all columns including intermediate transformation variables
    output_full = pipeline.get_output(mode="full")

    # If the model includes a logistic-regression step, extract predictions
    # Logistic predictions are stored in columns starting with "logistic_"
    predictions = output_full.filter(regex=r"^logistic_")

    # View column names to see what transformations were created
    print(output_full.columns.tolist())

Real-World Example: HTNPoRT Model
---------------------------------

The HTNPoRT (Hypertension Population Risk Tool) is a validated predictive model
for hypertension risk. Here's how to use this package with HTNPoRT:

.. code-block:: python

    # Clone the HTNPoRT repository to get model parameters and validation data
    # In your terminal:
    # git clone https://github.com/Big-Life-Lab/htnport.git

    import pandas as pd
    from pathlib import Path
    from model_parameters_pipeline import ModelPipeline

    # Set path to cloned HTNPoRT repository
    htnport_dir = Path("/path/to/htnport")

    # Load validation data
    data_file = (
        htnport_dir
        / "output/validation-data/HTNPoRT-female-validation-data.csv"
    )
    data = pd.read_csv(data_file)

    # View the input data structure
    print(data.head())

    # Path to model export file
    model_export_file = (
        htnport_dir
        / "output/logistic-model-export/female/HTNPoRT-female-model-export.csv"
    )

    # Create and run the pipeline, extract full output
    pipeline = ModelPipeline(model_export_file)
    pipeline.run(dat=data)
    result_full = pipeline.get_output(mode="full")

    # View the transformed data with all intermediate steps
    print(result_full.head())

    # Extract logistic predictions (hypertension risk probabilities)
    predictions = result_full.filter(regex=r"^logistic_")
    print(predictions.head())

    # Summary statistics of predictions
    print(predictions.describe())

Next Steps
----------

- For detailed information about the Model Parameters specification, see the
  `Model Parameters Reference Documentation
  <https://big-life-lab.github.io/model-parameters/5-reference.html>`_
- To add new transformation steps, see the
  `Adding a New Transformation Step
  <https://github.com/Big-Life-Lab/model-parameters-pipeline-py/blob/main/CONTRIBUTING.md#adding-a-new-transformation-step>`_
  guide
- To report issues or request features, visit the
  `issue tracker
  <https://github.com/Big-Life-Lab/model-parameters-pipeline-py/issues>`_

Additional Resources
--------------------

- `Big Life Lab GitHub <https://github.com/Big-Life-Lab>`_
- `Model Parameters Specification
  <https://github.com/Big-Life-Lab/model-parameters>`_
- `HTNPoRT Model <https://github.com/Big-Life-Lab/htnport>`_
- `Predictive Algorithms Repository
  <https://github.com/Big-Life-Lab/predictive-algorithms>`_
