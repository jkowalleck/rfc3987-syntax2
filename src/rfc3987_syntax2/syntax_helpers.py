# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

"""
Deprecated alias of package attributes.
"""

import sys
from importlib import import_module

sys.modules[__name__] = import_module(".", package=__package__)
