# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

"""
Deprecated re-export of package attributes.
"""

from importlib import import_module
from typing import Any, TYPE_CHECKING

__all__ = [
    "RFC3987_SYNTAX_PARSER_TYPE",
    "RFC3987_SYNTAX_GRAMMAR_PATH",
    "RFC3987_SYNTAX_TERMS",
    "grammar",
    "syntax_parser",
    "parse",
    "is_valid_syntax",
    "make_syntax_validator",
    "RFC3987_SYNTAX_TERM_VALIDATORS",
    "is_valid_syntax_iri",
    "is_valid_syntax_iri_reference",
    "is_valid_syntax_absolute_iri",
    "is_valid_syntax_scheme",
    "is_valid_syntax_ihier_part",
    "is_valid_syntax_irelative_ref",
    "is_valid_syntax_irelative_part",
    "is_valid_syntax_iauthority",
    "is_valid_syntax_iuserinfo",
    "is_valid_syntax_ihost",
    "is_valid_syntax_ireg_name",
    "is_valid_syntax_ipath",
    "is_valid_syntax_ipath_abempty",
    "is_valid_syntax_ipath_absolute",
    "is_valid_syntax_ipath_noscheme",
    "is_valid_syntax_ipath_rootless",
    "is_valid_syntax_ipath_empty",
    "is_valid_syntax_isegment",
    "is_valid_syntax_isegment_nz",
    "is_valid_syntax_isegment_nz_nc",
    "is_valid_syntax_ipchar",
    "is_valid_syntax_iquery",
    "is_valid_syntax_ifragment",
    "is_valid_syntax_iunreserved",
    "is_valid_syntax_ucschar",
    "is_valid_syntax_iprivate",
    "is_valid_syntax_sub_delims",
    "is_valid_syntax_ip_literal",
    "is_valid_syntax_ipvfuture",
    "is_valid_syntax_ipv6address",
    "is_valid_syntax_h16",
    "is_valid_syntax_ls32",
    "is_valid_syntax_ipv4address",
    "is_valid_syntax_dec_octet",
    "is_valid_syntax_digit",
    "is_valid_syntax_non_zero",
    "is_valid_syntax_unreserved",
    "is_valid_syntax_alpha",
    "is_valid_syntax_hexdig",
    "is_valid_syntax_port",
    "is_valid_syntax_pct_encoded",
]

if TYPE_CHECKING:
    from . import *
# cannot simply import everything, since we need to be aware of lazy-loading

_pkg = import_module(".", package=__package__)

def __getattr__(name: str) -> Any:
    if name in __all__:
        value = getattr(_pkg, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(__all__))
