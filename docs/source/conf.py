# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import tomllib
import datetime

sys.path.insert(0, os.path.abspath("../../"))  # adjust based on where your code is

project = "Crypto Pandas"
copyright = f"{datetime.datetime.now().year}, Sigma Quantiphi"
author = "Sigma Quantiphi"
with open("../../pyproject.toml", "rb") as toml_file:
    pyproject_data = tomllib.load(toml_file)
    release = pyproject_data["project"]["version"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",  # Google/NumPy docstrings
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_sitemap",
    "sphinxext.opengraph",
    # "sphinxcontrib.googleanalytics",
    "sphinxcontrib.redirects",
    # "sphinx.ext.intersphinx",
]
autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": False,
    "inherited-members": False,
}
templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_baseurl = "https://crypto-pandas.readthedocs.io/en/latest/"
html_theme = "furo"
html_static_path = ["_static"]
html_logo = "_static/sigma-quantiphi-logo.svg"
html_favicon = "_static/favicon.ico"
html_theme_options = {
    # "light_logo": "sigma-quantiphi-logo.svg",
    # "dark_logo":  "sigma-quantiphi-logo.svg",
    "favicon": {
        "light": "favicon-light.png",
        "dark": "favicon-dark.png",
    },
    # shows a GitHub icon in the header **and**
    # an “Edit this page” button in the right sidebar
    "source_repository": "https://github.com/sigma-quantiphi/crypto-pandas/",
    "source_branch": "main",  # or "master"
    "source_directory": "docs/",  # path inside the repo
}
ogp_site_url = html_baseurl  # reuse the value above
ogp_site_name = "Crypto-Pandas Docs"
ogp_description_length = 180
