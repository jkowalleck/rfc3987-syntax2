from pathlib import Path
import json
import pytest


@pytest.fixture
def valid_syntax_data():
    with open(Path("tests", "valid_syntax.json"), "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def invalid_syntax_data():
    with open(Path("tests", "invalid_syntax.json"), "r", encoding="utf-8") as f:
        return json.load(f)
