# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING

import re
from typing import Any, Callable

import pytest

import rfc3987_syntax2 as sut

from . import (
    TESTS_DATA_FILES,
    valid_syntax_data,
    invalid_syntax_data,
    SyntaxCase,
    T_syntax_file,
)


def syntax_data_as_params(src_cb: Callable[[], T_syntax_file]) -> Any:
    for term, examples in src_cb().items():
        for example in examples:
            yield pytest.param(term, example, id=f"{term}-{example['value']}")


def test_fixture_json_files_are_ascii_only() -> None:
    for path in TESTS_DATA_FILES.values():
        text = path.read_text(encoding="ascii")
        assert not re.search(r"\\u[0-9a-f]*[a-f][0-9a-f]*", text)


@pytest.mark.parametrize("term,valid_example", syntax_data_as_params(valid_syntax_data))
def test_is_valid_syntax(term: str, valid_example: SyntaxCase) -> None:
    actual = sut.is_valid_syntax(term=term, value=valid_example["value"])
    print("")
    print(
        f"Testing {term} with {valid_example['value']} : {valid_example['reason']}"
    )
    assert (
        actual is True
    ), f"Failed term: {term} for '{valid_example['value']}' : {valid_example['reason']}"


@pytest.mark.parametrize("term,invalid_example", syntax_data_as_params(invalid_syntax_data))
def test_not_is_valid_syntax(term: str, invalid_example: SyntaxCase) -> None:
    actual = sut.is_valid_syntax(term=term, value=invalid_example["value"])
    print("")
    print(
        f"Testing {term} with {invalid_example['value']} : {invalid_example['reason']}"
    )
    assert (
        actual is False
    ), f"Failed term: {term} for '{invalid_example['value']}' : {invalid_example['reason']}"
