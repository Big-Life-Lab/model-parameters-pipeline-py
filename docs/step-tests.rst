Model Parameters Step Tests
===========================

This section documents the unit tests for Model Parameters transformation
steps. Each subdirectory under ``tests/testdata/step-tests/`` represents a test
case for a specific transformation step.

Directory Structure
-------------------

::

    tests/testdata/step-tests/
    ├── test-data.csv             # Shared test data used by all step tests
    ├── test-variables.csv        # Shared variables definition file
    └── test-{stepname}/          # Test directory for a specific step
        ├── test-model-export.csv # Model export file defining files for transformation
        ├── test-model-steps.csv  # Model steps file defining transformation steps
        ├── test-{stepname}.csv   # Step-specific parameters file
        └── test-expected.csv     # Expected output (auto-generated)

Adding a New Unit Test
----------------------

To add a unit test for a Model Parameters transformation step:

1. Create Test Directory
^^^^^^^^^^^^^^^^^^^^^^^^

Create a new subdirectory named ``test-{stepname}`` where ``{stepname}`` is the
name of the transformation step you want to test.

2. Create Required Files
^^^^^^^^^^^^^^^^^^^^^^^^

Each test directory must contain the following files:

``test-model-export.csv``
"""""""""""""""""""""""""

This file defines the files used for the transformation. It generally has the
same structure for each unit test:

.. code-block:: text

    fileType,filePath
    variables,../test-variables.csv
    model-steps,./test-model-steps.csv

The file references:

- ``test-variables.csv`` -- The shared variables definition file (located in the
  parent directory)
- ``test-model-steps.csv`` -- The model steps file (located in the test
  directory)

``test-model-steps.csv``
"""""""""""""""""""""""""

This file defines the transformation steps to execute. The structure is:

.. code-block:: text

    step,fileType,filePath,notes
    {stepname},N/A,./test-{stepname}.csv,

Replace ``{stepname}`` with your step name. If the step doesn't require a
separate file, use ``N/A`` for ``fileType`` and ``filePath``.

``test-{stepname}.csv``
"""""""""""""""""""""""

This file contains step-specific parameters. The structure depends on the
transformation step being tested. For example, a logistic regression step would
have the coefficients for each variable and the intercept. Refer to the `Model
Parameters documentation
<https://big-life-lab.github.io/model-parameters/5-reference.html>`_ for
details on each step's required parameters.

3. Generate Expected Output
^^^^^^^^^^^^^^^^^^^^^^^^^^^

After creating your test files, generate the expected output by running:

.. code-block:: bash

    # From the project root directory

    # Generate expected output for all tests
    python -m tests.generate_step_tests_expected

    # Or generate for only your new test
    python -m tests.generate_step_tests_expected stepname

The ``generate_step_tests_expected`` function in
``tests/generate_step_tests_expected.py`` will:

1. Read the shared test data from ``test-data.csv``
2. Iterate through each subdirectory in the step-tests folder (or only
   specified steps)
3. Run the model pipeline using each ``test-model-export.csv`` file
4. Save the pipeline output as ``test-expected.csv`` in each subdirectory

The generated ``test-expected.csv`` file will be used by the unit tests to
verify correct transformation behavior.

You can also call the function directly from Python:

.. code-block:: python

    from tests.generate_step_tests_expected import generate_step_tests_expected

    # Generate expected output for all tests
    generate_step_tests_expected()

    # Or generate for only your new test
    generate_step_tests_expected(steps=["stepname"])

4. Run Tests Automatically
^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you've created your test directory and generated the expected output, your
new unit test will be **automatically discovered and run** when the test suite
executes. No additional registration or configuration is needed.

The test automation is implemented in ``tests/test_pipeline.py``, which:

1. Scans all subdirectories in the ``step-tests/`` folder
2. Automatically runs each test it finds
3. Compares the pipeline output against the ``test-expected.csv`` file

To run all tests, execute:

.. code-block:: bash

    pytest

Your new step test will be included automatically alongside all existing step
tests.

Model Parameters Steps Reference
---------------------------------

For detailed information about available transformation steps and their
parameters, see the `Model Parameters Reference Documentation
<https://big-life-lab.github.io/model-parameters/5-reference.html>`_.

Regenerating Expected Output
-----------------------------

If you need to update the expected output after fixing a bug or updating
transformation logic, follow the same process as described in section "3.
Generate Expected Output" above. The ``generate_step_tests_expected()`` function
can regenerate output for all tests or specific tests using the ``steps``
parameter.

After regenerating, review the changes to ensure the new output is correct, then
commit the updated ``test-expected.csv`` files.
