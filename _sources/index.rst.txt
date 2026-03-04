Model Parameters Pipeline
=========================

A Python package for applying sequential data transformations according to the
`Model Parameters specification <https://github.com/Big-Life-Lab/model-parameters>`_
developed by Big Life Lab.

Supported Transformations
-------------------------

- **Center** -- Subtract a specified value from a variable
- **Dummy** -- Create binary indicator variables for categorical values
- **Interaction** -- Multiply variables together to create interaction terms
- **Restricted Cubic Splines (RCS)** -- Create spline basis functions with
  specified knots
- **Logistic Regression** -- Apply logistic regression coefficients and the
  sigmoid function

.. toctree::
   :maxdepth: 2
   :caption: Contents

   introduction
   adding-a-step
   step-tests
   api
