# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

import json
import os
import platform
import sys
import time
import tracemalloc
from importlib import reload
from pathlib import Path
from typing import Callable, TypedDict

from lark import exceptions
import pytest

import rfc3987_syntax2 as sut
import rfc3987_syntax2.syntax_helpers as syntax_helpers

from . import invalid_syntax_data, valid_syntax_data, SyntaxCase


pytestmark = pytest.mark.perf

PERF_LOOPS = int(os.getenv("RFC3987_PERF_LOOPS", "1"))
PERF_WARMUP_LOOPS = int(os.getenv("RFC3987_PERF_WARMUP_LOOPS", "1"))
PERF_OUTPUT_JSON = Path(
    os.getenv("RFC3987_PERF_OUTPUT_JSON", ".pytest_perf/perf-results.json")
)

_PARSER_TERMS = ("iri", "iri_reference", "absolute_iri")
_BENCHMARKED_PUBLIC_PARSER_APIS = (
    "parse",
    "is_valid_syntax",
    "make_syntax_validator",
    "RFC3987_SYNTAX_TERM_VALIDATORS[term]",
)


class _RuntimeMeasurement(TypedDict):
    elapsed_seconds: float
    parse_calls: int
    memory_peak_bytes: int


def _measure_runtime(run_cb: Callable[[], int]) -> _RuntimeMeasurement:
    for _ in range(PERF_WARMUP_LOOPS):
        run_cb()

    tracemalloc.start()
    start = time.perf_counter()
    parse_calls = run_cb()
    elapsed = time.perf_counter() - start
    _, memory_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "elapsed_seconds": elapsed,
        "parse_calls": parse_calls,
        "memory_peak_bytes": memory_peak,
    }


def _run_parser_api(term: str, valid_cases: list[SyntaxCase], invalid_cases: list[SyntaxCase]) -> int:
    parse_calls = 0
    for _ in range(PERF_LOOPS):
        for case in valid_cases:
            parse_calls += 1
            sut.parse(term=term, value=case["value"])
        for case in invalid_cases:
            parse_calls += 1
            with pytest.raises(exceptions.LarkError):
                sut.parse(term=term, value=case["value"])
    return parse_calls


def _run_is_valid_api(
    validator: Callable[[str], bool], valid_cases: list[SyntaxCase], invalid_cases: list[SyntaxCase]
) -> int:
    parse_calls = 0
    for _ in range(PERF_LOOPS):
        for case in valid_cases:
            parse_calls += 1
            assert validator(case["value"]) is True
        for case in invalid_cases:
            parse_calls += 1
            assert validator(case["value"]) is False
    return parse_calls


def _measure_parse_build_init(valid_sample: str) -> float:
    fresh = reload(syntax_helpers)
    start = time.perf_counter()
    fresh.parse(term="iri", value=valid_sample)
    return time.perf_counter() - start


def _measure_is_valid_syntax_build_init(valid_sample: str) -> float:
    fresh = reload(syntax_helpers)
    start = time.perf_counter()
    assert fresh.is_valid_syntax(term="iri", value=valid_sample) is True
    return time.perf_counter() - start


def _measure_make_validator_build_init(term: str, valid_sample: str) -> float:
    start = time.perf_counter()
    validator = sut.make_syntax_validator(term)
    assert validator(valid_sample) is True
    return time.perf_counter() - start


def _write_results(payload: dict[str, object]) -> None:
    PERF_OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with PERF_OUTPUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def test_parser_performance_baseline() -> None:
    assert PERF_LOOPS > 0
    assert PERF_WARMUP_LOOPS >= 0

    valid_data = valid_syntax_data()
    invalid_data = invalid_syntax_data()
    benchmark_terms = tuple(
        term
        for term in sut.RFC3987_SYNTAX_TERMS
        if term in valid_data and term in invalid_data
    )
    assert benchmark_terms
    for parser_term in _PARSER_TERMS:
        assert parser_term in benchmark_terms
    benchmarked_term_validator_apis = tuple(
        f"is_valid_syntax_{term}" for term in benchmark_terms
    )
    valid_sample = valid_data["iri"][0]["value"]

    metrics: list[dict[str, object]] = []

    metrics.append(
        {
            "kind": "build_init",
            "api": "parse",
            "term": "iri",
            "elapsed_seconds": _measure_parse_build_init(valid_sample),
        }
    )
    metrics.append(
        {
            "kind": "build_init",
            "api": "is_valid_syntax",
            "term": "iri",
            "elapsed_seconds": _measure_is_valid_syntax_build_init(valid_sample),
        }
    )

    for term in benchmark_terms:
        metrics.append(
            {
                "kind": "build_init",
                "api": "make_syntax_validator",
                "term": term,
                "elapsed_seconds": _measure_make_validator_build_init(
                    term, valid_data[term][0]["value"]
                ),
            }
        )

    for term in _PARSER_TERMS:
        valid_cases = valid_data[term]
        invalid_cases = invalid_data[term]

        parse_runtime = _measure_runtime(
            lambda term=term, valid_cases=valid_cases, invalid_cases=invalid_cases: _run_parser_api(
                term=term, valid_cases=valid_cases, invalid_cases=invalid_cases
            )
        )
        metrics.append(
            {
                "kind": "runtime",
                "api": "parse",
                "term": term,
                "cases": len(valid_cases) + len(invalid_cases),
                "loops": PERF_LOOPS,
                **parse_runtime,
            }
        )

        is_valid_runtime = _measure_runtime(
            lambda term=term, valid_cases=valid_cases, invalid_cases=invalid_cases: _run_is_valid_api(
                validator=lambda value, term=term: sut.is_valid_syntax(term=term, value=value),
                valid_cases=valid_cases,
                invalid_cases=invalid_cases,
            )
        )
        metrics.append(
            {
                "kind": "runtime",
                "api": "is_valid_syntax",
                "term": term,
                "cases": len(valid_cases) + len(invalid_cases),
                "loops": PERF_LOOPS,
                **is_valid_runtime,
            }
        )

    for term in benchmark_terms:
        valid_cases = valid_data[term]
        invalid_cases = invalid_data[term]

        factory_validator = sut.make_syntax_validator(term)
        assert factory_validator(valid_cases[0]["value"]) is True
        factory_runtime = _measure_runtime(
            lambda factory_validator=factory_validator, valid_cases=valid_cases, invalid_cases=invalid_cases: _run_is_valid_api(
                validator=factory_validator,
                valid_cases=valid_cases,
                invalid_cases=invalid_cases,
            )
        )
        metrics.append(
            {
                "kind": "runtime",
                "api": "make_syntax_validator",
                "term": term,
                "cases": len(valid_cases) + len(invalid_cases),
                "loops": PERF_LOOPS,
                **factory_runtime,
            }
        )

        validator_from_mapping = sut.RFC3987_SYNTAX_TERM_VALIDATORS[term]
        mapping_runtime = _measure_runtime(
            lambda validator_from_mapping=validator_from_mapping, valid_cases=valid_cases, invalid_cases=invalid_cases: _run_is_valid_api(
                validator=validator_from_mapping,
                valid_cases=valid_cases,
                invalid_cases=invalid_cases,
            )
        )
        metrics.append(
            {
                "kind": "runtime",
                "api": "RFC3987_SYNTAX_TERM_VALIDATORS[term]",
                "term": term,
                "cases": len(valid_cases) + len(invalid_cases),
                "loops": PERF_LOOPS,
                **mapping_runtime,
            }
        )

        public_api_name = f"is_valid_syntax_{term}"
        public_validator = getattr(sut, public_api_name)
        public_runtime = _measure_runtime(
            lambda public_validator=public_validator, valid_cases=valid_cases, invalid_cases=invalid_cases: _run_is_valid_api(
                validator=public_validator,
                valid_cases=valid_cases,
                invalid_cases=invalid_cases,
            )
        )
        metrics.append(
            {
                "kind": "runtime",
                "api": public_api_name,
                "term": term,
                "cases": len(valid_cases) + len(invalid_cases),
                "loops": PERF_LOOPS,
                **public_runtime,
            }
        )

    payload = {
        "benchmarked_public_parser_apis": [
            *_BENCHMARKED_PUBLIC_PARSER_APIS,
            *benchmarked_term_validator_apis,
        ],
        "metadata": {
            "loops": PERF_LOOPS,
            "warmup_loops": PERF_WARMUP_LOOPS,
            "python_version": sys.version,
            "platform": platform.platform(),
        },
        "metrics": metrics,
    }
    _write_results(payload)

    assert PERF_OUTPUT_JSON.exists()
