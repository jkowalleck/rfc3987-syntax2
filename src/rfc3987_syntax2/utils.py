# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck (modifications and maintenance)
# SPDX-License-Identifier: MIT

from pathlib import Path


def load_grammar(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()
