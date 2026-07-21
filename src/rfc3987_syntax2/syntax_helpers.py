# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

from pathlib import Path
from threading import Lock
from typing import Any, Callable, Optional, TYPE_CHECKING, Literal
from warnings import warn

from lark import Lark, ParseTree, exceptions

from .utils import load_grammar


RFC3987_SYNTAX_PARSER_TYPE: str = "earley"
RFC3987_SYNTAX_GRAMMAR_PATH: Path = Path(__file__).parent / "syntax_rfc3987.lark"
RFC3987_SYNTAX_TERMS: list[str] = [
    "iri",
    "iri_reference",
    "absolute_iri",
    "scheme",
    "ihier_part",
    "irelative_ref",
    "irelative_part",
    "iauthority",
    "iuserinfo",
    "ihost",
    "ireg_name",
    "ipath",
    "ipath_abempty",
    "ipath_absolute",
    "ipath_noscheme",
    "ipath_rootless",
    "ipath_empty",
    "isegment",
    "isegment_nz",
    "isegment_nz_nc",
    "ipchar",
    "iquery",
    "ifragment",
    "iunreserved",
    "ucschar",
    "iprivate",
    "sub_delims",
    "ip_literal",
    "ipvfuture",
    "ipv6address",
    "h16",
    "ls32",
    "ipv4address",
    "dec_octet",
    "digit",
    "non_zero",
    "unreserved",
    "alpha",
    "hexdig",
    "port",
    "pct_encoded",
]
"""All supported RFC 3987 grammar rule names exposed by this module.

These term names can be used to select validators from
:data:`RFC3987_SYNTAX_TERM_VALIDATORS` and correspond to rules
defined in the RFC 3987 Lark grammar.
"""

T_SYNTAX_PARSER_TERM = Literal["iri", "iri_reference", "absolute_iri"]
SYNTAX_PARSER_STARTS: list[T_SYNTAX_PARSER_TERM] = ["iri", "iri_reference", "absolute_iri"]

def parse(term: T_SYNTAX_PARSER_TERM, value: str) -> ParseTree:
    """Parse text as one of the top-level RFC 3987 syntax terms.

    Args:
        term: Start rule used for parsing. Must be one of
            ``"iri"``, ``"iri_reference"``, or ``"absolute_iri"``.
        value: Input text to parse.

    Returns:
        The Lark parse tree for ``value`` under the selected start rule.

    Raises:
        lark.exceptions.LarkError: If parser initialization fails or parsing
            cannot be completed.
    """

    return _get_syntax_parser().parse(value, start=term)


def is_valid_syntax(term: T_SYNTAX_PARSER_TERM, value: str) -> bool:
    """Check whether text is valid for a top-level RFC 3987 syntax term.

    This is a boolean convenience wrapper around :func:`parse`.

    Args:
        term: Start rule used for validation. Must be one of
            ``"iri"``, ``"iri_reference"``, or ``"absolute_iri"``.
        value: Input text to validate.

    Returns:
        ``True`` if parsing succeeds; otherwise ``False``.

    Warns:
        RuntimeWarning: Emitted when a non-``UnexpectedInput``
            ``lark.exceptions.LarkError`` occurs.
    """

    try:
        parse(term=term, value=value)
    except exceptions.UnexpectedInput:
        # from Lark.parse()
        return False
    except exceptions.LarkError as err:
        # from Lark internals / initialization (non-UnexpectedInput)
        warn("Unexpected LarkError (non-UnexpectedInput) "
             f"for term={term!r}: {type(err).__name__}: {err}",
            RuntimeWarning,
            stacklevel=2)
        return False
    return True

T_SYNTAX_VALIDATOR = Callable[[str], bool]
"""Callable validator for one RFC 3987 grammar rule.

Args:
    text: Input text to validate.

Returns:
    ``True`` if ``text`` matches the target rule, otherwise ``False``.
"""


def make_syntax_validator(rule_name: str) -> T_SYNTAX_VALIDATOR:
    """Create a validator function for a specific RFC 3987 grammar rule.

    The returned callable lazily initializes and caches a dedicated
    :class:`lark.Lark` parser configured with ``start=rule_name`` and
    ``parser=RFC3987_SYNTAX_PARSER_TYPE``.

    Args:
        rule_name: Grammar rule name to validate against. Must be a value from
            :data:`RFC3987_SYNTAX_TERMS`.

    Returns:
        A callable ``(text: str) -> bool`` that returns ``True`` when parsing
        succeeds and ``False`` if a ``lark.exceptions.LarkError`` is raised.
    """

    parser: Optional[Lark] = None
    parser_lock = Lock()

    def syntax_validator(text: str) -> bool:
        nonlocal parser
        with parser_lock:
            if parser is None:
                parser = Lark(_get_grammar(),
                              start=rule_name,
                              parser=RFC3987_SYNTAX_PARSER_TYPE)
        try:
            parser.parse(text)
        except exceptions.LarkError:
            return False
        else:
            return True

    return syntax_validator


_grammar: Optional[str] = None
_grammar_lock = Lock()

def _get_grammar() -> str:
    """this is private API"""

    global _grammar
    with _grammar_lock:
        if _grammar is None:
            _grammar = load_grammar(RFC3987_SYNTAX_GRAMMAR_PATH)
        return _grammar


_syntax_parser: Optional[Lark] = None
_syntax_parser_lock = Lock()

def _get_syntax_parser() -> Lark:
    """this is private API"""

    global _syntax_parser
    if _syntax_parser is not None:
        return _syntax_parser
    grammar = _get_grammar()
    with _syntax_parser_lock:
        if _syntax_parser is None:
            _syntax_parser = Lark(grammar,
                                  start=SYNTAX_PARSER_STARTS,
                                  parser=RFC3987_SYNTAX_PARSER_TYPE)
        return _syntax_parser


is_valid_syntax_iri: T_SYNTAX_VALIDATOR = make_syntax_validator("iri")
"""Validate that input text conforms to the RFC 3987 ``IRI`` rule."""

is_valid_syntax_iri_reference: T_SYNTAX_VALIDATOR = make_syntax_validator("iri_reference")
"""Validate that input text conforms to the RFC 3987 ``IRI-reference`` rule."""

is_valid_syntax_absolute_iri: T_SYNTAX_VALIDATOR = make_syntax_validator("absolute_iri")
"""Validate that input text conforms to the RFC 3987 ``absolute-IRI`` rule."""

is_valid_syntax_scheme: T_SYNTAX_VALIDATOR = make_syntax_validator("scheme")
"""Validate that input text conforms to the RFC 3987 ``scheme`` rule."""

is_valid_syntax_ihier_part: T_SYNTAX_VALIDATOR = make_syntax_validator("ihier_part")
"""Validate that input text conforms to the RFC 3987 ``ihier-part`` rule."""

is_valid_syntax_irelative_ref: T_SYNTAX_VALIDATOR = make_syntax_validator("irelative_ref")
"""Validate that input text conforms to the RFC 3987 ``irelative-ref`` rule."""

is_valid_syntax_irelative_part: T_SYNTAX_VALIDATOR = make_syntax_validator("irelative_part")
"""Validate that input text conforms to the RFC 3987 ``irelative-part`` rule."""

is_valid_syntax_iauthority: T_SYNTAX_VALIDATOR = make_syntax_validator("iauthority")
"""Validate that input text conforms to the RFC 3987 ``iauthority`` rule."""

is_valid_syntax_iuserinfo: T_SYNTAX_VALIDATOR = make_syntax_validator("iuserinfo")
"""Validate that input text conforms to the RFC 3987 ``iuserinfo`` rule."""

is_valid_syntax_ihost: T_SYNTAX_VALIDATOR = make_syntax_validator("ihost")
"""Validate that input text conforms to the RFC 3987 ``ihost`` rule."""

is_valid_syntax_ireg_name: T_SYNTAX_VALIDATOR = make_syntax_validator("ireg_name")
"""Validate that input text conforms to the RFC 3987 ``ireg-name`` rule."""

is_valid_syntax_ipath: T_SYNTAX_VALIDATOR = make_syntax_validator("ipath")
"""Validate that input text conforms to the RFC 3987 ``ipath`` rule."""

is_valid_syntax_ipath_abempty: T_SYNTAX_VALIDATOR = make_syntax_validator("ipath_abempty")
"""Validate that input text conforms to the RFC 3987 ``ipath-abempty`` rule."""

is_valid_syntax_ipath_absolute: T_SYNTAX_VALIDATOR = make_syntax_validator("ipath_absolute")
"""Validate that input text conforms to the RFC 3987 ``ipath-absolute`` rule."""

is_valid_syntax_ipath_noscheme: T_SYNTAX_VALIDATOR = make_syntax_validator("ipath_noscheme")
"""Validate that input text conforms to the RFC 3987 ``ipath-noscheme`` rule."""

is_valid_syntax_ipath_rootless: T_SYNTAX_VALIDATOR = make_syntax_validator("ipath_rootless")
"""Validate that input text conforms to the RFC 3987 ``ipath-rootless`` rule."""

is_valid_syntax_ipath_empty: T_SYNTAX_VALIDATOR = make_syntax_validator("ipath_empty")
"""Validate that input text conforms to the RFC 3987 ``ipath-empty`` rule."""

is_valid_syntax_isegment: T_SYNTAX_VALIDATOR = make_syntax_validator("isegment")
"""Validate that input text conforms to the RFC 3987 ``isegment`` rule."""

is_valid_syntax_isegment_nz: T_SYNTAX_VALIDATOR = make_syntax_validator("isegment_nz")
"""Validate that input text conforms to the RFC 3987 ``isegment-nz`` rule."""

is_valid_syntax_isegment_nz_nc: T_SYNTAX_VALIDATOR = make_syntax_validator("isegment_nz_nc")
"""Validate that input text conforms to the RFC 3987 ``isegment-nz-nc`` rule."""

is_valid_syntax_ipchar: T_SYNTAX_VALIDATOR = make_syntax_validator("ipchar")
"""Validate that input text conforms to the RFC 3987 ``ipchar`` rule."""

is_valid_syntax_iquery: T_SYNTAX_VALIDATOR = make_syntax_validator("iquery")
"""Validate that input text conforms to the RFC 3987 ``iquery`` rule."""

is_valid_syntax_ifragment: T_SYNTAX_VALIDATOR = make_syntax_validator("ifragment")
"""Validate that input text conforms to the RFC 3987 ``ifragment`` rule."""

is_valid_syntax_iunreserved: T_SYNTAX_VALIDATOR = make_syntax_validator("iunreserved")
"""Validate that input text conforms to the RFC 3987 ``iunreserved`` rule."""

is_valid_syntax_ucschar: T_SYNTAX_VALIDATOR = make_syntax_validator("ucschar")
"""Validate that input text conforms to the RFC 3987 ``ucschar`` rule."""

is_valid_syntax_iprivate: T_SYNTAX_VALIDATOR = make_syntax_validator("iprivate")
"""Validate that input text conforms to the RFC 3987 ``iprivate`` rule."""

is_valid_syntax_sub_delims: T_SYNTAX_VALIDATOR = make_syntax_validator("sub_delims")
"""Validate that input text conforms to the RFC 3987 ``sub-delims`` rule."""

is_valid_syntax_ip_literal: T_SYNTAX_VALIDATOR = make_syntax_validator("ip_literal")
"""Validate that input text conforms to the RFC 3987 ``IP-literal`` rule."""

is_valid_syntax_ipvfuture: T_SYNTAX_VALIDATOR = make_syntax_validator("ipvfuture")
"""Validate that input text conforms to the RFC 3987 ``IPvFuture`` rule."""

is_valid_syntax_ipv6address: T_SYNTAX_VALIDATOR = make_syntax_validator("ipv6address")
"""Validate that input text conforms to the RFC 3987 ``IPv6address`` rule."""

is_valid_syntax_h16: T_SYNTAX_VALIDATOR = make_syntax_validator("h16")
"""Validate that input text conforms to the RFC 3987 ``h16`` rule."""

is_valid_syntax_ls32: T_SYNTAX_VALIDATOR = make_syntax_validator("ls32")
"""Validate that input text conforms to the RFC 3987 ``ls32`` rule."""

is_valid_syntax_ipv4address: T_SYNTAX_VALIDATOR = make_syntax_validator("ipv4address")
"""Validate that input text conforms to the RFC 3987 ``IPv4address`` rule."""

is_valid_syntax_dec_octet: T_SYNTAX_VALIDATOR = make_syntax_validator("dec_octet")
"""Validate that input text conforms to the RFC 3987 ``dec-octet`` rule."""

is_valid_syntax_digit: T_SYNTAX_VALIDATOR = make_syntax_validator("digit")
"""Validate that input text conforms to the RFC 3987 ``DIGIT`` rule."""

is_valid_syntax_non_zero: T_SYNTAX_VALIDATOR = make_syntax_validator("non_zero")
"""deprecated - not a known entry point according to RFC 3987"""

is_valid_syntax_unreserved: T_SYNTAX_VALIDATOR = make_syntax_validator("unreserved")
"""Validate that input text conforms to the RFC 3987 ``unreserved`` rule."""

is_valid_syntax_alpha: T_SYNTAX_VALIDATOR = make_syntax_validator("alpha")
"""Validate that input text conforms to the RFC 3987 ``ALPHA`` rule."""

is_valid_syntax_hexdig: T_SYNTAX_VALIDATOR = make_syntax_validator("hexdig")
"""Validate that input text conforms to the RFC 3987 ``HEXDIG`` rule."""

is_valid_syntax_port: T_SYNTAX_VALIDATOR = make_syntax_validator("port")
"""Validate that input text conforms to the RFC 3987 ``port`` rule."""

if TYPE_CHECKING:
    def is_valid_syntax_pct_encoded(text: str) -> bool:
        """typed """
else:
    is_valid_syntax_pct_encoded: T_SYNTAX_VALIDATOR = make_syntax_validator("pct_encoded")
    """Validate that input text conforms to the RFC 3987 ``pct-encoded`` rule."""


RFC3987_SYNTAX_TERM_VALIDATORS: dict[str, T_SYNTAX_VALIDATOR] = {  # frozendict
    "iri": make_syntax_validator("iri"),
    "iri_reference": is_valid_syntax_iri_reference,
    "absolute_iri": is_valid_syntax_absolute_iri,
    "scheme": is_valid_syntax_scheme,
    "ihier_part": is_valid_syntax_ihier_part,
    "irelative_ref": is_valid_syntax_irelative_ref,
    "irelative_part": is_valid_syntax_irelative_part,
    "iauthority": is_valid_syntax_iauthority,
    "iuserinfo": is_valid_syntax_iuserinfo,
    "ihost": is_valid_syntax_ihost,
    "ireg_name": is_valid_syntax_ireg_name,
    "ipath": is_valid_syntax_ipath,
    "ipath_abempty": is_valid_syntax_ipath_abempty,
    "ipath_absolute": is_valid_syntax_ipath_absolute,
    "ipath_noscheme": is_valid_syntax_ipath_noscheme,
    "ipath_rootless": is_valid_syntax_ipath_rootless,
    "ipath_empty": is_valid_syntax_ipath_empty,
    "isegment": is_valid_syntax_isegment,
    "isegment_nz": is_valid_syntax_isegment_nz,
    "isegment_nz_nc": is_valid_syntax_isegment_nz_nc,
    "ipchar": is_valid_syntax_ipchar,
    "iquery": is_valid_syntax_iquery,
    "ifragment": is_valid_syntax_ifragment,
    "iunreserved": is_valid_syntax_iunreserved,
    "ucschar": is_valid_syntax_ucschar,
    "iprivate": is_valid_syntax_iprivate,
    "sub_delims": is_valid_syntax_sub_delims,
    "ip_literal": is_valid_syntax_ip_literal,
    "ipvfuture": is_valid_syntax_ipvfuture,
    "ipv6address": is_valid_syntax_ipv6address,
    "h16": is_valid_syntax_h16,
    "ls32": is_valid_syntax_ls32,
    "ipv4address": is_valid_syntax_ipv4address,
    "dec_octet": is_valid_syntax_dec_octet,
    "digit": is_valid_syntax_digit,
    "non_zero": is_valid_syntax_non_zero,
    "unreserved": is_valid_syntax_unreserved,
    "alpha": is_valid_syntax_alpha,
    "hexdig": is_valid_syntax_hexdig,
    "port": is_valid_syntax_port,
    "pct_encoded": is_valid_syntax_pct_encoded,
}
"""Mapping from syntax term to validator.

Allowed keys are the RFC3987 term literals (see :data:`RFC3987_SYNTAX_TERMS`).
"""

# region lazy loaded attrs

if TYPE_CHECKING:  # types for lazy-loaded symbols
    grammar: str
    """Lark grammar text for RFC 3987.

    This is the grammar source loaded from :data:`RFC3987_SYNTAX_GRAMMAR_PATH`
    via :func:`_get_grammar`.
    """

    syntax_parser: Lark
    """Lazily initialized parser for RFC 3987 syntax.

    Built from :data:`grammar` using :class:`lark.Lark` with
    ``parser=RFC3987_SYNTAX_PARSER_TYPE`` and
    ``start=_SYNTAX_PARSER_STARTS``.
    """


def __getattr__(name: str) -> Any:
    if name == 'grammar':
        return _get_grammar()
    if name == 'syntax_parser':
        return _get_syntax_parser()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | {'grammar', 'syntax_parser'})

# endregion lazy loaded attrs
