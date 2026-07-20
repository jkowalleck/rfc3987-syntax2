# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

from typing import Callable, Optional, TYPE_CHECKING

from lark import Lark, ParseTree, exceptions

from pathlib import Path

from .utils import load_grammar

__all__ = [
    "RFC3987_SYNTAX_PARSER_TYPE",
    "RFC3987_SYNTAX_GRAMMAR_PATH",
    "RFC3987_SYNTAX_TERMS",
    "grammar",
    "syntax_parser",
    "parse",
    "is_valid_syntax",
    "make_syntax_validator",
    "is_valid_syntax_iri",
    "is_valid_syntax_iri_reference",
    "is_valid_syntax_absolute_iri",
    "is_valid_syntax_irelative_ref",
    "is_valid_syntax_irelative_part",
    "is_valid_syntax_ihier_part",
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
    "is_valid_syntax_unreserved",
    "is_valid_syntax_alpha",
    "is_valid_syntax_digit",
    "is_valid_syntax_hexdig",
    "is_valid_syntax_port",
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
    "non_zero",
    "unreserved",
    "alpha",
    "hexdig",
    "port",
    "pct_encoded",
]

def parse(term: str, value: str) -> ParseTree:
    return get_syntax_parser().parse(value, start=term)


def is_valid_syntax(term: str, value: str) -> bool:
    try:
        parse(term=term, value=value)
        return True
    except exceptions.LarkError:
        return False

T_SYNTAX_VALIDATOR = Callable[[str], bool]

def make_syntax_validator(rule_name: str) -> T_SYNTAX_VALIDATOR:
    parser = Lark(get_grammar(),
                  start=rule_name,
                  parser=RFC3987_SYNTAX_PARSER_TYPE)

    def syntax_validator(text: str) -> bool:
        try:
            parser.parse(text)
            return True
        except exceptions.LarkError:
            return False

    return syntax_validator


_grammar: Optional[str] = None


def get_grammar() -> str:
    """this is private API"""
    global _grammar
    if _grammar is None:
        _grammar = load_grammar(RFC3987_SYNTAX_GRAMMAR_PATH)
    return _grammar


_syntax_parser: Optional[Lark] = None


def get_syntax_parser() -> Lark:
    """this is private API"""
    global _syntax_parser
    if _syntax_parser is None:
        _syntax_parser = Lark(get_grammar(),
                              start=["iri", "iri_reference", "absolute_iri"],
                              parser=RFC3987_SYNTAX_PARSER_TYPE)
    return _syntax_parser


_CACHE_SYNTAX_VALIDATOR: dict[str, T_SYNTAX_VALIDATOR] = {}


def get_syntax_validator(rule_name) -> T_SYNTAX_VALIDATOR:
    """this is private API"""
    validator = _CACHE_SYNTAX_VALIDATOR.get(rule_name)
    if validator is None:
        validator = _CACHE_SYNTAX_VALIDATOR[rule_name] = make_syntax_validator(rule_name)
    return validator


if TYPE_CHECKING:
    # define types for all those lazy-loaded symbols
    grammar: str
    syntax_parser: Lark
    is_valid_syntax_iri: T_SYNTAX_VALIDATOR
    is_valid_syntax_iri_reference: T_SYNTAX_VALIDATOR
    is_valid_syntax_absolute_iri: T_SYNTAX_VALIDATOR
    is_valid_syntax_irelative_ref: T_SYNTAX_VALIDATOR
    is_valid_syntax_irelative_part: T_SYNTAX_VALIDATOR
    is_valid_syntax_ihier_part: T_SYNTAX_VALIDATOR
    is_valid_syntax_iauthority: T_SYNTAX_VALIDATOR
    is_valid_syntax_iuserinfo: T_SYNTAX_VALIDATOR
    is_valid_syntax_ihost: T_SYNTAX_VALIDATOR
    is_valid_syntax_ireg_name: T_SYNTAX_VALIDATOR
    is_valid_syntax_ipath: T_SYNTAX_VALIDATOR
    is_valid_syntax_ipath_abempty: T_SYNTAX_VALIDATOR
    is_valid_syntax_ipath_absolute: T_SYNTAX_VALIDATOR
    is_valid_syntax_ipath_noscheme: T_SYNTAX_VALIDATOR
    is_valid_syntax_ipath_rootless: T_SYNTAX_VALIDATOR
    is_valid_syntax_ipath_empty: T_SYNTAX_VALIDATOR
    is_valid_syntax_isegment: T_SYNTAX_VALIDATOR
    is_valid_syntax_isegment_nz: T_SYNTAX_VALIDATOR
    is_valid_syntax_isegment_nz_nc: T_SYNTAX_VALIDATOR
    is_valid_syntax_ipchar: T_SYNTAX_VALIDATOR
    is_valid_syntax_iquery: T_SYNTAX_VALIDATOR
    is_valid_syntax_ifragment: T_SYNTAX_VALIDATOR
    is_valid_syntax_iunreserved: T_SYNTAX_VALIDATOR
    is_valid_syntax_ucschar: T_SYNTAX_VALIDATOR
    is_valid_syntax_iprivate: T_SYNTAX_VALIDATOR
    is_valid_syntax_sub_delims: T_SYNTAX_VALIDATOR
    is_valid_syntax_ip_literal: T_SYNTAX_VALIDATOR
    is_valid_syntax_ipvfuture: T_SYNTAX_VALIDATOR
    is_valid_syntax_ipv6address: T_SYNTAX_VALIDATOR
    is_valid_syntax_h16: T_SYNTAX_VALIDATOR
    is_valid_syntax_ls32: T_SYNTAX_VALIDATOR
    is_valid_syntax_ipv4address: T_SYNTAX_VALIDATOR
    is_valid_syntax_dec_octet: T_SYNTAX_VALIDATOR
    is_valid_syntax_unreserved: T_SYNTAX_VALIDATOR
    is_valid_syntax_alpha: T_SYNTAX_VALIDATOR
    is_valid_syntax_digit: T_SYNTAX_VALIDATOR
    is_valid_syntax_hexdig: T_SYNTAX_VALIDATOR
    is_valid_syntax_port: T_SYNTAX_VALIDATOR


def __getattr__(name: str):
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    if name == 'grammar':
        return get_grammar()
    if name == 'syntax_parser':
        return get_syntax_parser()
    if name.startswith('is_valid_syntax_'):
        return get_syntax_validator(name[16:])  # the prefix is 16 chars long
    raise NotImplementedError(f"module {__name__!r} failed to implement attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + __all__)
