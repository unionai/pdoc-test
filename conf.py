# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import Path

sys.path.append(str(Path("extensions").resolve()))

project = "pdoc-test"
copyright = "2025, Shalom & Peeter"
author = "Shalom & Peeter"
release = "1"
autosectionlabel_prefix_document = True


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinxext.remoteliteralinclude",
    "pdoc_sphinx",
    "sphinx_design",
    "myst_parser",
]

# Configure the pdoc extension
pdoc_modules = ['union', 'flytekit']  # List of modules to document
pdoc_output_dir = 'rst'  # Output directory for generated docs

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": True,
    "show-inheritance": True
}
autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
