# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional
from warnings import warn

from lark import Lark, ParseTree, exceptions

__all__ = [
    "RFC3987_SYNTAX_PARSER_TYPE",
    "RFC3987_SYNTAX_GRAMMAR_PATH",
    "RFC3987_SYNTAX_TERMS",
    "grammar",
    "T_SYNTAX_PARSER_TERM",
    "parse",
    "syntax_parser",
    "T_SYNTAX_VALIDATOR",
    "is_valid_syntax",
    "make_syntax_validator",
]

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
    # non_zero - a local helper token used in `dec_octet`
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
"""Top-level RFC 3987 parser start terms accepted by :func:`parse` and :func:`check`.

Allowed values are ``"iri"``, ``"iri_reference"``, and ``"absolute_iri"``.
"""
_SYNTAX_PARSER_STARTS: list[T_SYNTAX_PARSER_TERM] = ["iri", "iri_reference", "absolute_iri"]


def parse(term: T_SYNTAX_PARSER_TERM, value: str) -> ParseTree:
    """Parse text as one of the top-level RFC 3987 syntax terms.

    :param term: Start rule used for parsing.
                 Must be one of ``"iri"``, ``"iri_reference"``, or ``"absolute_iri"``.
    :param value: Input text to parse.
    :return: The Lark parse tree for ``value`` under the selected start rule.
    :raises lark.exceptions.LarkError: If parser initialization fails or parsing cannot be completed.
    """

    return _get_syntax_parser().parse(value, start=term)


def is_valid_syntax(term: T_SYNTAX_PARSER_TERM, value: str) -> bool:
    """Check whether text is valid for a top-level RFC 3987 syntax term.

    This is a boolean convenience wrapper around :func:`parse`.

    .. warning:: Emits a ``RuntimeWarning`` (via :func:`warnings.warn`) when a non-``UnexpectedInput``
                ``lark.exceptions.LarkError`` occurs.

    :param term: Start rule used for validation.
                 Must be one of ``"iri"``, ``"iri_reference"``, or ``"absolute_iri"``.
    :param value: Input text to validate.
    :return: ``True`` if parsing succeeds; otherwise ``False``.
    """

    try:
        parse(term=term, value=value)
    except exceptions.UnexpectedInput:
        # from Lark.parse()
        return False
    except exceptions.LarkError as err:
        # from Lark internals / initialization (non-UnexpectedInput)
        # TODO: make this thor transparent - dont catch it
        warn("Unexpected LarkError (non-UnexpectedInput) "
             f"for term={term!r}: {type(err).__name__}: {err}",
             RuntimeWarning,
             stacklevel=2)
        return False
    return True


T_SYNTAX_VALIDATOR = Callable[[str], bool]
"""Callable validator for one RFC 3987 grammar rule.

:param text: Input text to validate.
:return: ``True`` if ``text`` matches the target rule, otherwise ``False``.
"""


def make_syntax_validator(rule_name: str) -> T_SYNTAX_VALIDATOR:
    """Create a validator function for a specific RFC 3987 grammar rule.

    The returned callable lazily initializes and caches a dedicated
    :class:`lark.Lark` parser configured with ``start=rule_name`` and
    ``parser=RFC3987_SYNTAX_PARSER_TYPE``.

    :param rule_name: Grammar rule name to validate against. Must be a value from
        :data:`RFC3987_SYNTAX_TERMS`.
    :return: A callable ``(text: str) -> bool`` that returns ``True`` when parsing
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
            _grammar = RFC3987_SYNTAX_GRAMMAR_PATH.read_text(encoding="utf-8")
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
                                  start=_SYNTAX_PARSER_STARTS,
                                  parser=RFC3987_SYNTAX_PARSER_TYPE)
        return _syntax_parser


# region lazy loaded attrs

if TYPE_CHECKING:  # types for lazy-loaded symbols
    grammar: str
    """Lark grammar text for RFC 3987."""

if TYPE_CHECKING:  # types for lazy-loaded symbols
    syntax_parser: Lark
    """Lazily initialized parser for RFC 3987 syntax."""


def __getattr__(name: str) -> Any:
    if name == "grammar":
        global grammar
        grammar = _get_grammar()
        return grammar
    if name == "syntax_parser":
        global syntax_parser
        syntax_parser = _get_syntax_parser()
        return syntax_parser
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(__all__))

# endregion lazy loaded attrs
