import rfc3987_syntax as h

from . import invalid_syntax_data, valid_syntax_data
import cProfile

def test_is_valid_syntax(valid_syntax_data):
    pr = cProfile.Profile()
    for _ in range(10):
        for term, valid_examples in valid_syntax_data.items():
            for valid_example in valid_examples:
                pr.enable()
                h.is_valid_syntax(term=term, value=valid_example["value"])
                pr.disable()
    pr.print_stats(sort='time')
    # ~ 7sec for 10 runs - mostly earley.py:78(predict_and_complete)
    # not much change after optimizing imports and try/catch
    # not much change after optimizing terminators in grammar


def test_not_is_valid_syntax(invalid_syntax_data):
    pr = cProfile.Profile()
    for _ in range(10):
        for term, invalid_examples in invalid_syntax_data.items():
            for invalid_example in invalid_examples:
                pr.enable()
                h.is_valid_syntax(term=term, value=invalid_example["value"])
                pr.disable()
    pr.print_stats(sort='time')
