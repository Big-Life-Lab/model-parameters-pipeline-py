"""Sphinx configuration for Model Parameters Pipeline."""

project = "Model Parameters Pipeline"
copyright = "2026, Martin Wellman"
author = "Martin Wellman"
version = "0.2.0"
release = "0.2.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# Autodoc settings
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Theme
html_theme = "sphinx_rtd_theme"

# Exclude build output
exclude_patterns = ["_build"]
