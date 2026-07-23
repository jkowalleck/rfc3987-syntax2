# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

from typing import Any, Callable

import pytest

import rfc3987_syntax2.is_valid_syntax_term as sut
from rfc3987_syntax2 import RFC3987_SYNTAX_TERMS

from . import SyntaxCase, T_syntax_file, invalid_syntax_data, valid_syntax_data


def syntax_data_as_params(src_cb: Callable[[], T_syntax_file]) -> Any:
    for term, examples in src_cb().items():
        for example in examples:
            yield pytest.param(term, example, id=f"{term}-{example['value']}")


@pytest.mark.parametrize("term,valid_example", syntax_data_as_params(valid_syntax_data))
def test_is_valid_syntax(term: str, valid_example: SyntaxCase) -> None:
    actual = sut.RFC3987_SYNTAX_TERM_VALIDATORS[term](valid_example["value"])
    print("")
    print(
        f"Testing {term} with {valid_example['value']} : {valid_example['reason']}"
    )
    assert (
        actual is True
    ), f"Failed term: {term} for '{valid_example['value']}' : {valid_example['reason']}"


@pytest.mark.parametrize("term,invalid_example", syntax_data_as_params(invalid_syntax_data))
def test_not_is_valid_syntax(term: str, invalid_example: SyntaxCase) -> None:
    actual = sut.RFC3987_SYNTAX_TERM_VALIDATORS[term](invalid_example["value"])
    print("")
    print(
        f"Testing {term} with {invalid_example['value']} : {invalid_example['reason']}"
    )
    assert (
        actual is False
    ), f"Failed term: {term} for '{invalid_example['value']}' : {invalid_example['reason']}"



@pytest.mark.parametrize("term", RFC3987_SYNTAX_TERMS)
def test_term_validator_exists(term: str) -> None:
    actual = sut.RFC3987_SYNTAX_TERM_VALIDATORS.get(term)
    assert (actual is not None), f"missing func for {term}"


@pytest.mark.parametrize("term", (t for t in RFC3987_SYNTAX_TERMS if t not in [
    # non_zero - a local helper token used in `dec_octet`
    'non_zero',
]))
def test_term_validator_as_expected(term: str) -> None:
    expected = getattr(sut, f'is_valid_syntax_{term}')
    actual = sut.RFC3987_SYNTAX_TERM_VALIDATORS[term]
    assert (actual is expected), f"unexpected func for {term}"
