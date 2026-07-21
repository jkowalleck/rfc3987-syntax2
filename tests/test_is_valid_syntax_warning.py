# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

from unittest.mock import patch

import pytest
from lark import exceptions

import rfc3987_syntax2.syntax_helpers as sut


def _raise_lark_error(*args: object, **kwargs: object) -> None:
    raise exceptions.LarkError("unexpected test error")


def test_is_valid_syntax_warns_on_unexpected_lark_error() -> None:
    with patch.object(sut, "parse", side_effect=_raise_lark_error):
        with pytest.warns(RuntimeWarning, match=r"Unexpected LarkError"):
            result = sut.is_valid_syntax(
                term='unsupported-term',  # type: ignore[arg-type] # on purpose
                value="any-value")
    assert result is False
