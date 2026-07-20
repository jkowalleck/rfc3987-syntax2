# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

import rfc3987_syntax2 as sut
from lark import Lark


def test_grammar_is_accessible() -> None:
    """Regression test: grammar is lazily loaded and accessible as a module attribute."""
    assert isinstance(sut.grammar, str)
    assert len(sut.grammar) > 0


def test_syntax_parser_is_accessible() -> None:
    """Regression test: syntax_parser is lazily loaded and accessible as a module attribute."""
    parser = sut.syntax_parser
    assert isinstance(parser, Lark)
    assert parser.options.parser == sut.RFC3987_SYNTAX_PARSER_TYPE
    assert parser.options.start == ["iri", "iri_reference", "absolute_iri"]


def test_grammar_in_dir() -> None:
    """Regression test: grammar appears in dir(rfc3987_syntax2)."""
    assert "grammar" in dir(sut)


def test_syntax_parser_in_dir() -> None:
    """Regression test: syntax_parser appears in dir(rfc3987_syntax2)."""
    assert "syntax_parser" in dir(sut)
