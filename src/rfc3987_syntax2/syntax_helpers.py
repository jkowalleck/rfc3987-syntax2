# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Any, Callable, Final, Literal, Mapping, Optional, Sequence, TypeAlias
from warnings import warn

from lark import Lark, ParseTree, exceptions

from .utils import load_grammar

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
    "is_valid_syntax_unreserved",
    "is_valid_syntax_alpha",
    "is_valid_syntax_hexdig",
    "is_valid_syntax_port",
    "is_valid_syntax_pct_encoded",
]

RFC3987_SYNTAX_PARSER_TYPE: Final[str] = "earley"
RFC3987_SYNTAX_GRAMMAR_PATH: Final[Path] = Path(__file__).parent / "syntax_rfc3987.lark"
RFC3987_SYNTAX_TERMS: Final[Sequence[str]] = [
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

T_SYNTAX_PARSER_TERM: TypeAlias = Literal["iri", "iri_reference", "absolute_iri"]
"""Top-level RFC 3987 parser start terms accepted by :func:`parse` and :func:`check`.

Allowed values are ``"iri"``, ``"iri_reference"``, and ``"absolute_iri"``.
"""

_SYNTAX_PARSER_STARTS: Final[Sequence[T_SYNTAX_PARSER_TERM]] = ["iri", "iri_reference", "absolute_iri"]


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
        warn("Unexpected LarkError (non-UnexpectedInput) "
             f"for term={term!r}: {type(err).__name__}: {err}",
             RuntimeWarning,
             stacklevel=2)
        return False
    return True


T_SYNTAX_VALIDATOR: TypeAlias = Callable[[str], bool]
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
                                  start=_SYNTAX_PARSER_STARTS,
                                  parser=RFC3987_SYNTAX_PARSER_TYPE)
        return _syntax_parser


if TYPE_CHECKING:
    def is_valid_syntax_iri(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``IRI`` rule."""
        ...
else:
    is_valid_syntax_iri = make_syntax_validator("iri")


if TYPE_CHECKING:
    def is_valid_syntax_iri_reference(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``IRI-reference`` rule."""
        ...
else:
    is_valid_syntax_iri_reference = make_syntax_validator("iri_reference")

if TYPE_CHECKING:
    def is_valid_syntax_absolute_iri(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``absolute-IRI`` rule."""
        ...
else:
    is_valid_syntax_absolute_iri = make_syntax_validator("absolute_iri")

if TYPE_CHECKING:
    def is_valid_syntax_scheme(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``scheme`` rule."""
        ...
else:
    is_valid_syntax_scheme = make_syntax_validator("scheme")

if TYPE_CHECKING:
    def is_valid_syntax_ihier_part(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ihier-part`` rule."""
        ...
else:
    is_valid_syntax_ihier_part = make_syntax_validator("ihier_part")

if TYPE_CHECKING:
    def is_valid_syntax_irelative_ref(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``irelative-ref`` rule."""
        ...
else:
    is_valid_syntax_irelative_ref = make_syntax_validator("irelative_ref")

if TYPE_CHECKING:
    def is_valid_syntax_irelative_part(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``irelative-part`` rule."""
        ...
else:
    is_valid_syntax_irelative_part = make_syntax_validator("irelative_part")

if TYPE_CHECKING:
    def is_valid_syntax_iauthority(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``iauthority`` rule."""
        ...
else:
    is_valid_syntax_iauthority = make_syntax_validator("iauthority")

if TYPE_CHECKING:
    def is_valid_syntax_iuserinfo(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``iuserinfo`` rule."""
        ...
else:
    is_valid_syntax_iuserinfo = make_syntax_validator("iuserinfo")

if TYPE_CHECKING:
    def is_valid_syntax_ihost(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ihost`` rule."""
        ...
else:
    is_valid_syntax_ihost = make_syntax_validator("ihost")

if TYPE_CHECKING:
    def is_valid_syntax_ireg_name(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ireg-name`` rule."""
        ...
else:
    is_valid_syntax_ireg_name = make_syntax_validator("ireg_name")

if TYPE_CHECKING:
    def is_valid_syntax_ipath(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ipath`` rule."""
        ...
else:
    is_valid_syntax_ipath = make_syntax_validator("ipath")

if TYPE_CHECKING:
    def is_valid_syntax_ipath_abempty(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ipath-abempty`` rule."""
        ...
else:
    is_valid_syntax_ipath_abempty = make_syntax_validator("ipath_abempty")

if TYPE_CHECKING:
    def is_valid_syntax_ipath_absolute(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ipath-absolute`` rule."""
        ...
else:
    is_valid_syntax_ipath_absolute = make_syntax_validator("ipath_absolute")

if TYPE_CHECKING:
    def is_valid_syntax_ipath_noscheme(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ipath-noscheme`` rule."""
        ...
else:
    is_valid_syntax_ipath_noscheme = make_syntax_validator("ipath_noscheme")

if TYPE_CHECKING:
    def is_valid_syntax_ipath_rootless(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ipath-rootless`` rule."""
        ...
else:
    is_valid_syntax_ipath_rootless = make_syntax_validator("ipath_rootless")

if TYPE_CHECKING:
    def is_valid_syntax_ipath_empty(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ipath-empty`` rule."""
        ...
else:
    is_valid_syntax_ipath_empty = make_syntax_validator("ipath_empty")


if TYPE_CHECKING:
    def is_valid_syntax_isegment(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``isegment`` rule."""
        ...
else:
    is_valid_syntax_isegment = make_syntax_validator("isegment")

if TYPE_CHECKING:
    def is_valid_syntax_isegment_nz(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``isegment-nz`` rule."""
        ...
else:
    is_valid_syntax_isegment_nz = make_syntax_validator("isegment_nz")

if TYPE_CHECKING:
    def is_valid_syntax_isegment_nz_nc(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``isegment-nz-nc`` rule."""
        ...
else:
    is_valid_syntax_isegment_nz_nc = make_syntax_validator("isegment_nz_nc")

if TYPE_CHECKING:
    def is_valid_syntax_ipchar(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ipchar`` rule."""
        ...
else:
    is_valid_syntax_ipchar = make_syntax_validator("ipchar")

if TYPE_CHECKING:
    def is_valid_syntax_iquery(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``iquery`` rule."""
        ...
else:
    is_valid_syntax_iquery = make_syntax_validator("iquery")

if TYPE_CHECKING:
    def is_valid_syntax_ifragment(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ifragment`` rule."""
        ...
else:
    is_valid_syntax_ifragment = make_syntax_validator("ifragment")

if TYPE_CHECKING:
    def is_valid_syntax_iunreserved(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``iunreserved`` rule."""
        ...
else:
    is_valid_syntax_iunreserved = make_syntax_validator("iunreserved")

if TYPE_CHECKING:
    def is_valid_syntax_ucschar(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ucschar`` rule."""
        ...
else:
    is_valid_syntax_ucschar = make_syntax_validator("ucschar")

if TYPE_CHECKING:
    def is_valid_syntax_iprivate(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``iprivate`` rule."""
        ...
else:
    is_valid_syntax_iprivate = make_syntax_validator("iprivate")

if TYPE_CHECKING:
    def is_valid_syntax_sub_delims(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``sub-delims`` rule."""
        ...
else:
    is_valid_syntax_sub_delims = make_syntax_validator("sub_delims")

if TYPE_CHECKING:
    def is_valid_syntax_ip_literal(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``IP-literal`` rule."""
        ...
else:
    is_valid_syntax_ip_literal = make_syntax_validator("ip_literal")

if TYPE_CHECKING:
    def is_valid_syntax_ipvfuture(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``IPvFuture`` rule."""
        ...
else:
    is_valid_syntax_ipvfuture = make_syntax_validator("ipvfuture")

if TYPE_CHECKING:
    def is_valid_syntax_ipv6address(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``IPv6address`` rule."""
        ...
else:
    is_valid_syntax_ipv6address = make_syntax_validator("ipv6address")

if TYPE_CHECKING:
    def is_valid_syntax_h16(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``h16`` rule."""
        ...
else:
    is_valid_syntax_h16 = make_syntax_validator("h16")

if TYPE_CHECKING:
    def is_valid_syntax_ls32(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ls32`` rule."""
        ...
else:
    is_valid_syntax_ls32 = make_syntax_validator("ls32")

if TYPE_CHECKING:
    def is_valid_syntax_ipv4address(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``IPv4address`` rule."""
        ...
else:
    is_valid_syntax_ipv4address = make_syntax_validator("ipv4address")

if TYPE_CHECKING:
    def is_valid_syntax_dec_octet(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``dec-octet`` rule."""
        ...
else:
    is_valid_syntax_dec_octet = make_syntax_validator("dec_octet")

if TYPE_CHECKING:
    def is_valid_syntax_digit(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``DIGIT`` rule."""
        ...
else:
    is_valid_syntax_digit = make_syntax_validator("digit")

if TYPE_CHECKING:
    def is_valid_syntax_unreserved(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``unreserved`` rule."""
        ...
else:
    is_valid_syntax_unreserved = make_syntax_validator("unreserved")

if TYPE_CHECKING:
    def is_valid_syntax_alpha(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``ALPHA`` rule."""
        ...
else:
    is_valid_syntax_alpha = make_syntax_validator("alpha")

if TYPE_CHECKING:
    def is_valid_syntax_hexdig(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``HEXDIG`` rule."""
        ...
else:
    is_valid_syntax_hexdig = make_syntax_validator("hexdig")

if TYPE_CHECKING:
    def is_valid_syntax_port(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``port`` rule."""
        ...
else:
    is_valid_syntax_port = make_syntax_validator("port")

if TYPE_CHECKING:
    def is_valid_syntax_pct_encoded(text: str) -> bool:
        """Validate that input text conforms to the RFC 3987 ``pct-encoded`` rule."""
        ...
else:
    is_valid_syntax_pct_encoded = make_syntax_validator("pct_encoded")


RFC3987_SYNTAX_TERM_VALIDATORS: Final[Mapping[str, T_SYNTAX_VALIDATOR]] = {  # frozendict
    "iri": is_valid_syntax_iri,
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
    # non_zero - a local helper token used in `dec_octet`
    "non_zero": make_syntax_validator("non_zero"),
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
    grammar: Final[str]  # type:ignore[misc]  # lazy loading is Final downstream
    """Lark grammar text for RFC 3987."""

if TYPE_CHECKING:  # types for lazy-loaded symbols
    syntax_parser: Final[Lark]  # type:ignore[misc]  # lazy loading is Final downstream
    """Lazily initialized parser for RFC 3987 syntax."""


def __getattr__(name: str) -> Any:
    if name == "grammar":
        global grammar
        grammar = _get_grammar()  # type:ignore[misc]  # lazy loading is Final downstream
        return grammar
    if name == "syntax_parser":
        global syntax_parser
        syntax_parser = _get_syntax_parser()  # type:ignore[misc]  # lazy loading is Final downstream
        return syntax_parser
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(__all__))

# endregion lazy loaded attrs
