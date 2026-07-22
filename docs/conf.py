# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from __future__ import annotations

import skbuild

# -- Project information -----------------------------------------------------

project = 'scikit-build'
copyright = '2016, the scikit-build team'
author = 'The scikit-build team'

version = skbuild.__version__
release = skbuild.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'sphinx_issues',
    'sphinxcontrib.moderncmakedomain',
]

issues_github_path = 'scikit-build/scikit-build'

# README.md/CHANGES.md fragments are spliced into index.rst, so they start at H2.
suppress_warnings = ['myst.header']

templates_path = ['_templates']

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

exclude_patterns = ['_build']

intersphinx_mapping = {
    'cmake': ('https://cmake.org/cmake/help/latest/', None),
    'python': ('https://docs.python.org/3', None),
    'setuptools': ('https://setuptools.readthedocs.io/en/latest', None),
}

# -- Options for HTML output -------------------------------------------------

html_theme = 'furo'

html_theme_options = {
    'source_repository': 'https://github.com/scikit-build/scikit-build',
    'source_branch': 'main',
    'source_directory': 'docs/',
    'footer_icons': [
        {
            'name': 'GitHub',
            'url': 'https://github.com/scikit-build/scikit-build',
            'html': """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            'class': '',
        },
    ],
}

# The full logo's gray wordmark was drawn for a dark sidebar; the mark alone
# works on both furo backgrounds.
html_logo = 'logo/scikit_build_mark.svg'
html_copy_source = False
html_show_sourcelink = False

htmlhelp_basename = 'scikit-build-doc'

# -- Extension configuration -------------------------------------------------

myst_enable_extensions = [
    'colon_fence',
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'scikit-build',
     'scikit-build Documentation',
     ['scikit-build team'], 1)
]
