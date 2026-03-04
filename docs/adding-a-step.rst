Adding a New Transformation Step
================================

This guide explains how to add support for a new transformation step to the
Model Parameters Pipeline, as defined by the `Model Parameters repository
<https://big-life-lab.github.io/model-parameters/>`_.

Overview
--------

Adding a new transformation step requires three main tasks:

1. **Register the step** in the ``_STEP_DISPATCH`` dictionary in
   ``pipeline.py``
2. **Create a new step module** -- Implement ``run_step_{stepname}`` in
   ``src/model_parameters_pipeline/steps/{stepname}.py``
3. **Add unit tests** -- Create test files to verify correct behavior

Step 1: Register the Step in ``_STEP_DISPATCH``
------------------------------------------------

The ``pipeline.py`` module contains a ``_STEP_DISPATCH`` dictionary that maps
step names to their implementation functions. The ``run`` method uses this
dictionary to dispatch each step.

Location
^^^^^^^^

Find the ``_STEP_DISPATCH`` dictionary near the top of ``pipeline.py``:

.. code-block:: python

    _STEP_DISPATCH: dict[str, Callable[[ModelPipeline, str | Path], list[str]]] = {
        "center": run_step_center,
        "dummy": run_step_dummy,
        "interaction": run_step_interaction,
        "logistic-regression": run_step_logistic_regression,
        "rcs": run_step_rcs,
    }

Add Your Step
^^^^^^^^^^^^^

1. Import your new step function at the top of the file:

   .. code-block:: python

       from model_parameters_pipeline.steps.your_step_name import run_step_your_step_name

2. Add a new entry to ``_STEP_DISPATCH``:

   .. code-block:: python

       _STEP_DISPATCH: dict[str, Callable[[ModelPipeline, str | Path], list[str]]] = {
           "center": run_step_center,
           "dummy": run_step_dummy,
           "interaction": run_step_interaction,
           "logistic-regression": run_step_logistic_regression,
           "rcs": run_step_rcs,
           "your-step-name": run_step_your_step_name,
       }

.. important::

   - The dictionary key (``"your-step-name"``) must match the exact step name
     as it appears in the Model Parameters specification and in users'
     ``model-steps.csv`` files.
   - The function name (``run_step_your_step_name``) uses underscores instead
     of hyphens.

Step 2: Create the Step Function
---------------------------------

Create a new module ``src/model_parameters_pipeline/steps/{stepname}.py``
containing a function named ``run_step_{stepname}`` that implements the
transformation logic.

Create the Module
^^^^^^^^^^^^^^^^^

Create a new file at ``src/model_parameters_pipeline/steps/{stepname}.py``
(replace ``{stepname}`` with your step name, using underscores).

Function Template
^^^^^^^^^^^^^^^^^

Use this template as a starting point:

.. code-block:: python

    """{Step Name} transformation step.

    {Brief description of what this step does and its purpose}.
    """

    from __future__ import annotations

    from pathlib import Path
    from typing import TYPE_CHECKING

    from model_parameters_pipeline._utils import verify_columns

    if TYPE_CHECKING:
        from model_parameters_pipeline.pipeline import ModelPipeline


    def run_step_{stepname}(mod: ModelPipeline, file: str | Path) -> list[str]:
        """Run {step name} transformation step.

        Args:
            mod: ModelPipeline instance (mutated in place).
            file: Path to {step name} step specification CSV.

        Returns:
            List of output column names created by this step.
        """
        mod._add_file(file)
        step_data = mod._get_file(file)

        verify_columns(
            step_data,
            ["column1", "column2", "column3"],
            "{stepname} step file",
            file,
        )

        output_columns: list[str] = []

        for _, row in step_data.iterrows():
            # Extract parameters from the specification
            param1 = row["column1"]
            param2 = row["column2"]
            param3 = row["column3"]

            # Implement your transformation logic here
            # Example: mod.data[new_column] = mod.data[existing_column] * param
            output_columns.append(new_column)

        return output_columns

Key Components Explained
^^^^^^^^^^^^^^^^^^^^^^^^

1. **File Location**: Create your step function in
   ``src/model_parameters_pipeline/steps/{stepname}.py``.

2. **Function Signature**:

   - Always takes ``mod`` (``ModelPipeline`` instance) and ``file`` (path to
     specification file)
   - Input data is accessed and modified via ``mod.data`` (a pandas DataFrame)
   - Always returns a ``list[str]`` of output column names
   - The ``ModelPipeline`` import is under ``TYPE_CHECKING`` to avoid circular
     imports

3. **Load Specification File**:

   .. code-block:: python

       mod._add_file(file)
       step_data = mod._get_file(file)

   Always use these ``ModelPipeline`` methods to load files -- never read files
   directly (e.g. with ``pd.read_csv``). ``_add_file`` and ``_get_file`` ensure
   that any file path is validated against the sandbox path, if one was
   specified when constructing the ``ModelPipeline``. This prevents steps from
   reading files outside the permitted directory.

4. **Verify Columns**:

   .. code-block:: python

       verify_columns(
           step_data,
           ["column1", "column2", "column3"],
           "{stepname} step file",
           file,
       )

   Validates that the specification file contains all required columns. Update
   the column list to match your step's requirements from the Model Parameters
   documentation. Import ``verify_columns`` from
   ``model_parameters_pipeline._utils``.

5. **Process Each Row**: The ``for _, row in step_data.iterrows()`` loop
   processes each row in the specification file. Each row typically defines one
   transformation to apply.

6. **Access and Write Data**:

   - Read a column: ``mod.data[column_name]`` (returns a pandas Series)
   - Write a column: ``mod.data[new_column] = transformed_values``

7. **Track Output Columns**: Append each new column name to
   ``output_columns`` so the pipeline knows which columns this step produced.

Example: Center Step
^^^^^^^^^^^^^^^^^^^^

Here's a real example from the existing codebase (``steps/center.py``):

.. code-block:: python

    def run_step_center(mod: ModelPipeline, file: str | Path) -> list[str]:
        """Run center transformation step.

        Args:
            mod: ModelPipeline instance (mutated in place).
            file: Path to center step specification CSV.

        Returns:
            List of output column names created by this step.
        """
        mod._add_file(file)
        step_data = mod._get_file(file)

        verify_columns(
            step_data,
            ["origVariable", "centerValue", "centeredVariable"],
            "center step file",
            file,
        )

        output_columns: list[str] = []

        for _, row in step_data.iterrows():
            orig_variable = row["origVariable"]
            center_value = row["centerValue"]
            centered_variable = row["centeredVariable"]

            mod.data[centered_variable] = mod.data[orig_variable] - center_value
            output_columns.append(centered_variable)

        return output_columns

This function:

- Is defined in its own module ``steps/center.py``
- Accepts ``mod`` (a ``ModelPipeline`` instance) and ``file``; data is accessed
  via ``mod.data``
- Loads the center specification file using ``mod._add_file`` /
  ``mod._get_file``
- Verifies it has the required columns (``origVariable``, ``centerValue``,
  ``centeredVariable``)
- For each row, creates a new centered variable by subtracting ``centerValue``
  from the original variable in ``mod.data``
- Returns a list of the new column names

Step 3: Add Unit Tests
-----------------------

Unit tests ensure your transformation step works correctly. The testing
framework automatically discovers and runs tests based on directory structure.

See :doc:`step-tests` for complete instructions.

Reference Documentation
-----------------------

For detailed information about Model Parameters transformation steps and their
required file formats, see:

- `Model Parameters Reference Documentation
  <https://big-life-lab.github.io/model-parameters/5-reference.html>`_
- :doc:`step-tests`

Checklist
---------

Use this checklist when adding a new transformation step:

- Create new module: ``src/model_parameters_pipeline/steps/{stepname}.py``
- Implement ``run_step_{stepname}`` function with type hints and docstring
- Import and add entry to ``_STEP_DISPATCH`` in ``pipeline.py``
- Verify column names match the Model Parameters specification
- Create test directory: ``tests/testdata/step-tests/test-{stepname}/``
- Create ``test-model-export.csv`` in test directory
- Create ``test-model-steps.csv`` in test directory
- Create ``test-{stepname}.csv`` with test parameters in test directory
- Generate expected output using ``generate_step_tests_expected()``
- Run ``pytest`` to verify tests pass
- Review and commit all changes including ``test-expected.csv``

Common Patterns
---------------

Parsing Delimited Strings
^^^^^^^^^^^^^^^^^^^^^^^^^^

Some steps use delimited strings (e.g., "var1;var2;var3") in their parameters
file. Use the helper function:

.. code-block:: python

    from model_parameters_pipeline._utils import get_string_parts

    parts = get_string_parts(row["columnName"])

Working with Numeric Values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert string values to numeric when needed:

.. code-block:: python

    from model_parameters_pipeline._utils import get_string_parts

    numeric_values = [float(v) for v in get_string_parts(row["knots"])]

Creating New Columns Safely
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To avoid column name conflicts:

.. code-block:: python

    from model_parameters_pipeline._utils import get_unused_column

    new_col = get_unused_column(mod.data, "prefix_")

Adding Multiple Columns
^^^^^^^^^^^^^^^^^^^^^^^^

You can add multiple columns at once using numpy array assignment:

.. code-block:: python

    import numpy as np

    # vals is a 2D numpy array with one column per variable
    vals = some_computation(mod.data[variable])
    for col_idx, var_name in enumerate(variable_names):
        mod.data[var_name] = vals[:, col_idx]

Getting Help
------------

- For Model Parameters specification questions, refer to the `Model Parameters
  documentation <https://big-life-lab.github.io/model-parameters/>`_
- For existing step implementation examples, see modules like
  ``steps/center.py``, ``steps/dummy.py``, etc.
- For testing questions, see ``tests/testdata/step-tests/README.md``
