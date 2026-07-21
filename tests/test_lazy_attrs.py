# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

import subprocess
import sys

from lark import Lark

import rfc3987_syntax2 as sut


def test_grammar_not_eager() -> None:
    """Regression test: grammar is not populated in rfc3987_syntax2.__dict__ immediately after import."""
    result = subprocess.run(
        [sys.executable, '-c',
            'import rfc3987_syntax2; assert "grammar" not in vars(rfc3987_syntax2), "grammar was eagerly loaded on import"'],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_syntax_parser_not_eager() -> None:
    """Regression test: syntax_parser is not populated in rfc3987_syntax2.__dict__ immediately after import."""
    result = subprocess.run(
        [sys.executable, '-c',
            'import rfc3987_syntax2; assert "syntax_parser" not in vars(rfc3987_syntax2), "syntax_parser was eagerly loaded on import"'],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_grammar_is_accessible() -> None:
    """Regression test: grammar is lazily loaded and accessible as a module attribute."""
    assert isinstance(sut.grammar, str)
    assert len(sut.grammar) > 0


def test_syntax_parser_is_accessible() -> None:
    """Regression test: syntax_parser is lazily loaded and accessible as a module attribute."""
    assert isinstance(sut.syntax_parser, Lark)


def test_grammar_in_dir() -> None:
    """Regression test: grammar appears in dir(rfc3987_syntax2)."""
    assert "grammar" in dir(sut)


def test_syntax_parser_in_dir() -> None:
    """Regression test: syntax_parser appears in dir(rfc3987_syntax2)."""
    assert "syntax_parser" in dir(sut)
