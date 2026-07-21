# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

from typing import Any, TYPE_CHECKING

from . import syntax_helpers as _syntax_helpers

__all__ = _syntax_helpers.__all__

_EXPORTS_SH = frozenset(_syntax_helpers.__all__)

if TYPE_CHECKING:
    from .syntax_helpers import *

def __getattr__(name: str) -> Any:
    if name in _EXPORTS_SH:
        value = getattr(_syntax_helpers, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(__all__))
