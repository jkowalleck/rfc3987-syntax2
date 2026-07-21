# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

import json
from pathlib import Path
from typing import TypedDict

from typing_extensions import NotRequired, Required

TESTS_ROOT_DIR = Path(__file__).parent
TESTS_DATA_DIR = TESTS_ROOT_DIR / '_data'

TESTS_DATA_FILES = {
    'invalid_syntax': TESTS_DATA_DIR / 'invalid_syntax.json',
    'valid_syntax': TESTS_DATA_DIR / 'valid_syntax.json',
}


class SyntaxCase(TypedDict):
    value: Required[str]
    reason: Required[str]
    expect_lark: NotRequired[bool]
    expect_regex: NotRequired[bool]
    conforms_with_rfc3987_semantics: NotRequired[bool]
    semantics_notes: NotRequired[str]


T_syntax_file = dict[str, list[SyntaxCase]]


def valid_syntax_data() -> T_syntax_file:
    with open(TESTS_DATA_FILES['valid_syntax'], "r", encoding="utf-8") as f:
        return json.load(f)  # type:ignore[no-any-return]


def invalid_syntax_data() -> T_syntax_file:
    with open(TESTS_DATA_FILES['invalid_syntax'], "r", encoding="utf-8") as f:
        return json.load(f)  # type:ignore[no-any-return]
