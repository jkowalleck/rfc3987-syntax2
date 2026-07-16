from pathlib import Path


def load_grammar(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()
