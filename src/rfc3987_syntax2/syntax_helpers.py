# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

from typing import Callable

import sys

from lark import Lark, ParseTree, exceptions

from pathlib import Path

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

grammar: str = load_grammar(RFC3987_SYNTAX_GRAMMAR_PATH)


def parse(term: str, value: str) -> ParseTree:
    return sys.modules[__name__].syntax_parser.parse(value, start=term)


def is_valid_syntax(term: str, value: str) -> bool:
    try:
        parse(term=term, value=value)
        return True
    except exceptions.LarkError:
        return False


def make_syntax_validator(rule_name: str) -> Callable[[str], bool]:
    parser = Lark(grammar, start=rule_name, parser=RFC3987_SYNTAX_PARSER_TYPE)

    def syntax_validator(text: str) -> bool:
        try:
            parser.parse(text)
            return True
        except exceptions.LarkError:
            return False

    return syntax_validator


# Cache for lazily created validators
_attr_cache = {}


SYNTAX_VALIDATOR_PREFIX = "is_valid_syntax_"


def get_syntax_validator(attr_name: str):
    if not attr_name.startswith(SYNTAX_VALIDATOR_PREFIX):
        return None

    term_name = attr_name[len(SYNTAX_VALIDATOR_PREFIX) :]

    if term_name not in RFC3987_SYNTAX_TERMS:
        return None

    return make_syntax_validator(term_name)


def get_syntax_parser():
    return Lark(grammar, start=["iri", "iri_reference", "absolute_iri"], parser=RFC3987_SYNTAX_PARSER_TYPE)

def __getattr__(name):
    """
    Lazily create attributes, in particular syntax validators, when accessed.

    When an attribute like 'is_valid_syntax_iri' is accessed, this function
    will create and cache the corresponding validator function.

    We also create the syntax parser lazily.
    """
    try:
        return _attr_cache[name]
    except KeyError:
        if name == 'syntax_parser':
            syntax_parser = get_syntax_parser()
            _attr_cache[name] = syntax_parser
            return syntax_parser
        if validator := get_syntax_validator(name):
            _attr_cache[name] = validator
            return validator

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
