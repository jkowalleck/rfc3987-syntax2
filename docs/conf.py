project = "TODO"
copyright = "TODO"
author = "TODO"

release = "TODO"

extensions = [
    "sphinx.ext.autodoc",
    # "sphinx.ext.viewcode",
    "autoapi.extension",
    "sphinx_rtd_theme",
    "m2r2"
]

source_suffix = ['.rst', '.md']

autoapi_type = 'python'
autoapi_dirs = ['../src/rfc3987_syntax2']
# see https://sphinx-autoapi.readthedocs.io/en/latest/reference/config.html#confval-autoapi_options
autoapi_options = [
    'show-module-summary',
    'members',
    'undoc-members',
    'inherited-members',
    'show-inheritance',
    'imported-members'
]


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
# see https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-exclude_patterns
exclude_patterns = [
    '_dev',  # internal docs
    '_build',  # build target
    '.*', '**/.*',  # dotfiles and folders
    'Thumbs.db', '**/Thumbs.db',
]

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

