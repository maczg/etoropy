# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import importlib.metadata

# -- Project information -----------------------------------------------------

project = "etoropy"
copyright = "2025, Massimo Gollo"
author = "Massimo Gollo"
release = importlib.metadata.version("etoropy")
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinxcontrib.autodoc_pydantic",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_title = "etoropy"
html_static_path = []

# -- autodoc -----------------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "undoc-members": False,
}
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# -- sphinx-autodoc-typehints ------------------------------------------------

always_document_param_types = True
typehints_defaults = "braces"

# -- autodoc-pydantic --------------------------------------------------------

autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_field_summary = True
autodoc_pydantic_model_show_validator_summary = True
autodoc_pydantic_field_list_validators = True
autodoc_pydantic_settings_show_json = False
autodoc_pydantic_settings_show_config_summary = False
autodoc_pydantic_settings_show_field_summary = True

# -- intersphinx -------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

suppress_warnings = ["sphinx_autodoc_typehints.forward_reference"]

# -- copybutton --------------------------------------------------------------

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
