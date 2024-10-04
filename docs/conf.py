"""Sphinx configuration."""

project = "SPIDB"
author = "Daniel Kadyrov"
copyright = "2024, Daniel Kadyrov"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
    "sphinx.ext.intersphinx",
]
autodoc_typehints = "description"
html_theme = "furo"
master_doc = "index"