# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

import pytest

import rfc3987_syntax2 as sut


@pytest.mark.parametrize("term", sut.RFC3987_SYNTAX_TERMS)
def test_term_validator_as_expected(term: str) -> None:
    expected = getattr(sut, f'is_valid_syntax_{term}')
    actual = sut.RFC3987_SYNTAX_TERM_VALIDATORS[term]
    assert (actual is expected), f"unexpected func for {term}"
