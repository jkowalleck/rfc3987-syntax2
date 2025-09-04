from lark import Lark, ParseTree, exceptions

from pathlib import Path

from rfc3987_syntax.utils import load_grammar

RFC3987_SYNTAX_PARSER_TYPE: str = "earley"
RFC3987_SYNTAX_GRAMMAR_PATH: Path = Path(__file__).parent / "syntax_rfc3987.lark"
RFC3987_SYNTAX_TERMS: list[str] = [
    "iri",
    "iri_reference",
    "absolute_iri",
    "scheme",
    "irelative_ref",
    "irelative_part"
    "ihier_part",
    "iauthority",
    "iuserinfo",
    "ihost",
    "ireg_name",
    "ipath_abempty",
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

syntax_parser = Lark(grammar, start=["iri", "iri_reference", "absolute_iri"], parser=RFC3987_SYNTAX_PARSER_TYPE)


def parse(term: str, value: str) -> ParseTree:
    return syntax_parser.parse(value, start=term)


def is_valid_syntax(term: str, value: str):
    try:
        parse(term=term, value=value)
        return True
    except exceptions.LarkError:
        return False


def make_syntax_validator(rule_name):
    parser = Lark(grammar, start=rule_name, parser=RFC3987_SYNTAX_PARSER_TYPE)

    def syntax_validator(text):
        try:
            parser.parse(text)
            return True
        except exceptions.LarkError:
            return False

    return syntax_validator


# Cache for lazily created validators
_validator_cache = {}


SYNTAX_VALIDATOR_PREFIX = "is_valid_syntax_"


def get_syntax_validator(attr_name: str):
    if not attr_name.startswith(SYNTAX_VALIDATOR_PREFIX):
        return None

    term_name = attr_name[len(SYNTAX_VALIDATOR_PREFIX) :]

    if term_name not in RFC3987_SYNTAX_TERMS:
        return None

    return make_syntax_validator(term_name)


def __getattr__(name):
    """
    Lazily create syntax validators when accessed.

    When an attribute like 'is_valid_syntax_iri' is accessed, this function
    will create and cache the corresponding validator function.
    """
    try:
        return _validator_cache[name]
    except KeyError:
        if validator := get_syntax_validator(name):
            _validator_cache[name] = validator
            return validator

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
