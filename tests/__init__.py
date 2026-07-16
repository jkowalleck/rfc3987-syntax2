from pathlib import Path

TESTS_ROOT_DIR = Path(__file__).parent
TESTS_DATA_DIR = TESTS_ROOT_DIR / '_data'

TESTS_DATA_FILES = {
    'invalid_syntax': TESTS_DATA_DIR / 'invalid_syntax.json',
    'valid_syntax': TESTS_DATA_DIR / 'valid_syntax.json',
}