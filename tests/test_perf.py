# Copyright (c) 2025 Will Riley - original author
# Copyright (c) 2026 Jan Kowalleck - modifications and maintenance
# SPDX-License-Identifier: MIT

from __future__ import annotations

import gc
import json
import os
import platform
import statistics
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Callable

import lark
import pytest
from lark import Lark

import rfc3987_syntax2 as sut
from rfc3987_syntax2.syntax_helpers import (
    RFC3987_SYNTAX_PARSER_TYPE,
    grammar,
)

pytestmark = pytest.mark.perf

PERF_RESULTS_JSON_ENV = "RFC3987_PERF_RESULTS_JSON"
PERF_BASELINE_JSON_ENV = "RFC3987_PERF_BASELINE_JSON"
PERF_MODE_ENV = "RFC3987_PERF_MODE"

PERF_SETTINGS: dict[str, dict[str, Any]] = {
    "smoke": {
        "warmup_rounds": 1,
        "measurement_rounds": 2,
        "build_iterations_per_round": 1,
        "parse_corpus_repetitions_per_round": 1,
        "dataset_names": ("small",),
    },
    "full": {
        "warmup_rounds": 1,
        "measurement_rounds": 3,
        "build_iterations_per_round": 3,
        "parse_corpus_repetitions_per_round": 3,
        "dataset_names": ("small", "medium", "large"),
    },
}

DATASET_REPEAT_FACTORS = {
    "small": 1,
    "medium": 5,
    "large": 25,
}

RULE_SAMPLES: dict[str, tuple[str, ...]] = {
    "absolute_iri": (
        "https://www.example.com/articles/überblick?lang=de",
        "mailto:alice@example.com",
    ),
    "alpha": ("A", "z"),
    "dec_octet": ("200", "42"),
    "digit": ("7", "3"),
    "h16": ("1a2b", "BEEF"),
    "iauthority": ("alice@example.com:443", "example.org"),
    "hexdig": ("f", "9"),
    "ifragment": ("kapitel-1", "section-2"),
    "ihier_part": ("//example.com/articles/überblick", "/articles/überblick"),
    "ihost": ("example.org", "192.168.0.1"),
    "ip_literal": ("[2001:db8::1]", "[vF.example]"),
    "ipath": ("/articles/überblick", "documents/guide"),
    "ipath_abempty": ("/articles/überblick", "/guide/intro"),
    "ipath_absolute": ("/articles/2026/überblick", "/docs/reference"),
    "ipath_empty": ("",),
    "ipath_noscheme": ("documents/guide", "articles/überblick"),
    "ipath_rootless": ("documents/guide", "articles/überblick/teil-1"),
    "ipchar": ("ü", "a"),
    "iprivate": ("\uE000", "\uF8FF"),
    "ipv4address": ("192.168.0.1", "203.0.113.42"),
    "ipv6address": ("2001:db8::1", "2001:db8:85a3::8a2e:370:7334"),
    "ipvfuture": ("vF.example", "v1.alpha"),
    "ireg_name": ("example.org", "xn--bcher-kva.example"),
    "irelative_part": ("//example.com/articles/überblick", "documents/guide"),
    "irelative_ref": ("../docs/guide.html?lang=de#überblick", "//example.com/docs"),
    "iri": (
        "https://www.example.com/articles/überblick?lang=de#kapitel-1",
        "ftp://example.org/files/report.txt",
    ),
    "iri_reference": (
        "docs/guide.html#überblick",
        "../assets/über.png?size=2x",
    ),
    "isegment": ("überblick", "section-2"),
    "isegment_nz": ("überblick", "section-2"),
    "isegment_nz_nc": ("uberblick", "section-2"),
    "iquery": ("lang=de&section=überblick", "page=2&sort=asc"),
    "iunreserved": ("ü", "a"),
    "iuserinfo": ("alice:token", "reader"),
    "ls32": ("192.168.0.1", "1a2b:3c4d"),
    "port": ("443", "8080"),
    "sub_delims": ("!", ";"),
    "ucschar": ("ü", "京"),
    "unreserved": ("a", "~"),
}

GENERIC_RULES = ("absolute_iri", "iri", "iri_reference")

VALIDATOR_APIS: tuple[tuple[str, str, Callable[[str], bool]], ...] = (
    ("is_valid_syntax_absolute_iri", "absolute_iri", sut.is_valid_syntax_absolute_iri),
    ("is_valid_syntax_alpha", "alpha", sut.is_valid_syntax_alpha),
    ("is_valid_syntax_dec_octet", "dec_octet", sut.is_valid_syntax_dec_octet),
    ("is_valid_syntax_digit", "digit", sut.is_valid_syntax_digit),
    ("is_valid_syntax_h16", "h16", sut.is_valid_syntax_h16),
    ("is_valid_syntax_iauthority", "iauthority", sut.is_valid_syntax_iauthority),
    ("is_valid_syntax_hexdig", "hexdig", sut.is_valid_syntax_hexdig),
    ("is_valid_syntax_ifragment", "ifragment", sut.is_valid_syntax_ifragment),
    ("is_valid_syntax_ihier_part", "ihier_part", sut.is_valid_syntax_ihier_part),
    ("is_valid_syntax_ihost", "ihost", sut.is_valid_syntax_ihost),
    ("is_valid_syntax_ip_literal", "ip_literal", sut.is_valid_syntax_ip_literal),
    ("is_valid_syntax_ipath", "ipath", sut.is_valid_syntax_ipath),
    ("is_valid_syntax_ipath_abempty", "ipath_abempty", sut.is_valid_syntax_ipath_abempty),
    ("is_valid_syntax_ipath_absolute", "ipath_absolute", sut.is_valid_syntax_ipath_absolute),
    ("is_valid_syntax_ipath_empty", "ipath_empty", sut.is_valid_syntax_ipath_empty),
    ("is_valid_syntax_ipath_noscheme", "ipath_noscheme", sut.is_valid_syntax_ipath_noscheme),
    ("is_valid_syntax_ipath_rootless", "ipath_rootless", sut.is_valid_syntax_ipath_rootless),
    ("is_valid_syntax_ipchar", "ipchar", sut.is_valid_syntax_ipchar),
    ("is_valid_syntax_iprivate", "iprivate", sut.is_valid_syntax_iprivate),
    ("is_valid_syntax_ipv4address", "ipv4address", sut.is_valid_syntax_ipv4address),
    ("is_valid_syntax_ipv6address", "ipv6address", sut.is_valid_syntax_ipv6address),
    ("is_valid_syntax_ipvfuture", "ipvfuture", sut.is_valid_syntax_ipvfuture),
    ("is_valid_syntax_ireg_name", "ireg_name", sut.is_valid_syntax_ireg_name),
    ("is_valid_syntax_irelative_part", "irelative_part", sut.is_valid_syntax_irelative_part),
    ("is_valid_syntax_irelative_ref", "irelative_ref", sut.is_valid_syntax_irelative_ref),
    ("is_valid_syntax_iri", "iri", sut.is_valid_syntax_iri),
    ("is_valid_syntax_iri_reference", "iri_reference", sut.is_valid_syntax_iri_reference),
    ("is_valid_syntax_isegment", "isegment", sut.is_valid_syntax_isegment),
    ("is_valid_syntax_isegment_nz", "isegment_nz", sut.is_valid_syntax_isegment_nz),
    ("is_valid_syntax_isegment_nz_nc", "isegment_nz_nc", sut.is_valid_syntax_isegment_nz_nc),
    ("is_valid_syntax_iquery", "iquery", sut.is_valid_syntax_iquery),
    ("is_valid_syntax_iunreserved", "iunreserved", sut.is_valid_syntax_iunreserved),
    ("is_valid_syntax_iuserinfo", "iuserinfo", sut.is_valid_syntax_iuserinfo),
    ("is_valid_syntax_ls32", "ls32", sut.is_valid_syntax_ls32),
    ("is_valid_syntax_port", "port", sut.is_valid_syntax_port),
    ("is_valid_syntax_sub_delims", "sub_delims", sut.is_valid_syntax_sub_delims),
    ("is_valid_syntax_ucschar", "ucschar", sut.is_valid_syntax_ucschar),
    ("is_valid_syntax_unreserved", "unreserved", sut.is_valid_syntax_unreserved),
)

PERF_RESULTS: list[dict[str, Any]] = []


def perf_settings() -> dict[str, Any]:
    mode = os.environ.get(PERF_MODE_ENV, "full")
    try:
        return PERF_SETTINGS[mode]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported {PERF_MODE_ENV} value {mode!r}. "
            f"Expected one of {sorted(PERF_SETTINGS)}."
        ) from exc


def dataset_names() -> tuple[str, ...]:
    return tuple(perf_settings()["dataset_names"])


def build_corpus(rule_name: str, dataset_name: str) -> tuple[str, ...]:
    samples = RULE_SAMPLES[rule_name]
    return samples * DATASET_REPEAT_FACTORS[dataset_name]


def assert_build_coverage_is_complete() -> None:
    covered_rules = set(GENERIC_RULES) | {rule_name for _, rule_name, _ in VALIDATOR_APIS}
    assert set(RULE_SAMPLES) == covered_rules


def measure_resource_usage(
    run_once: Callable[[], None],
    *,
    operation_count_per_round: int,
) -> dict[str, Any]:
    settings = perf_settings()
    warmup_rounds = settings["warmup_rounds"]
    measurement_rounds = settings["measurement_rounds"]

    for _ in range(warmup_rounds):
        run_once()

    durations: list[float] = []
    peak_allocations: list[int] = []
    for _ in range(measurement_rounds):
        gc.collect()
        tracemalloc.start()
        started_at = time.perf_counter()
        run_once()
        duration = time.perf_counter() - started_at
        _, peak_allocated = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        durations.append(duration)
        peak_allocations.append(peak_allocated)

    mean_seconds = statistics.fmean(durations)
    stdev_seconds = statistics.pstdev(durations) if len(durations) > 1 else 0.0
    ms_per_operation = (mean_seconds * 1000) / operation_count_per_round
    operations_per_second = operation_count_per_round / mean_seconds

    return {
        "warmup_rounds": warmup_rounds,
        "measurement_rounds": measurement_rounds,
        "operation_count_per_round": operation_count_per_round,
        "mean_seconds_per_round": mean_seconds,
        "stdev_seconds_per_round": stdev_seconds,
        "ms_per_operation": ms_per_operation,
        "operations_per_second": operations_per_second,
        "peak_allocated_bytes": max(peak_allocations),
    }


def record_perf_result(
    *,
    benchmark_kind: str,
    parser_name: str,
    rule_name: str,
    dataset_name: str,
    dataset_size: int,
    metrics: dict[str, Any],
) -> None:
    PERF_RESULTS.append(
        {
            "benchmark_kind": benchmark_kind,
            "parser_name": parser_name,
            "rule_name": rule_name,
            "dataset_name": dataset_name,
            "dataset_size": dataset_size,
            **metrics,
        }
    )


def baseline_results() -> dict[tuple[str, str, str], dict[str, Any]]:
    baseline_path = os.environ.get(PERF_BASELINE_JSON_ENV)
    if not baseline_path:
        return {}

    raw_results = json.loads(Path(baseline_path).read_text(encoding="utf-8"))
    return {
        (result["benchmark_kind"], result["parser_name"], result["dataset_name"]): result
        for result in raw_results.get("results", [])
    }


def render_delta(current_ms_per_operation: float, baseline_entry: dict[str, Any] | None) -> str:
    if not baseline_entry:
        return "n/a"

    baseline_ms = baseline_entry["ms_per_operation"]
    if baseline_ms == 0:
        return "n/a"

    delta = ((current_ms_per_operation - baseline_ms) / baseline_ms) * 100
    return f"{delta:+.2f}%"


def write_perf_results() -> Path | None:
    results_path = os.environ.get(PERF_RESULTS_JSON_ENV)
    if not results_path:
        return None

    path = Path(results_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "system": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "lark_version": lark.__version__,
        },
        "settings": {
            "mode": os.environ.get(PERF_MODE_ENV, "full"),
            **perf_settings(),
        },
        "results": PERF_RESULTS,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def build_benchmark_cases() -> list[tuple[str, str, Callable[[], Any]]]:
    cases = [
        (
            "syntax_parser_init",
            "iri|iri_reference|absolute_iri",
            lambda: Lark(
                grammar,
                start=["iri", "iri_reference", "absolute_iri"],
                parser=RFC3987_SYNTAX_PARSER_TYPE,
            ),
        )
    ]
    cases.extend(
        (
            f"make_syntax_validator[{rule_name}]",
            rule_name,
            lambda rule_name=rule_name: sut.make_syntax_validator(rule_name),
        )
        for _, rule_name, _ in VALIDATOR_APIS
    )
    return cases


def parse_benchmark_cases() -> list[tuple[str, str, str, Callable[[str], Any]]]:
    cases: list[tuple[str, str, str, Callable[[str], Any]]] = []
    for rule_name in GENERIC_RULES:
        cases.append(
            (
                f"parse[{rule_name}]",
                rule_name,
                rule_name,
                lambda value, rule_name=rule_name: sut.parse(term=rule_name, value=value),
            )
        )
        cases.append(
            (
                f"is_valid_syntax[{rule_name}]",
                rule_name,
                rule_name,
                lambda value, rule_name=rule_name: sut.is_valid_syntax(term=rule_name, value=value),
            )
        )

    cases.extend(
        (api_name, rule_name, rule_name, validator)
        for api_name, rule_name, validator in VALIDATOR_APIS
    )
    return cases


def run_parse_corpus(parse_api: Callable[[str], Any], corpus: tuple[str, ...]) -> None:
    repetitions = perf_settings()["parse_corpus_repetitions_per_round"]
    for _ in range(repetitions):
        for value in corpus:
            result = parse_api(value)
            if isinstance(result, bool):
                assert result is True
            else:
                assert result is not None


def format_summary_table() -> list[str]:
    baselines = baseline_results()
    rows = [
        (
            result["benchmark_kind"],
            result["parser_name"],
            result["dataset_name"],
            str(result["dataset_size"]),
            f"{result['ms_per_operation']:.4f}",
            f"{result['operations_per_second']:.2f}",
            f"{result['peak_allocated_bytes'] / 1024:.1f}",
            render_delta(
                result["ms_per_operation"],
                baselines.get(
                    (
                        result["benchmark_kind"],
                        result["parser_name"],
                        result["dataset_name"],
                    )
                ),
            ),
        )
        for result in sorted(
            PERF_RESULTS,
            key=lambda item: (
                item["benchmark_kind"],
                item["parser_name"],
                item["dataset_name"],
            ),
        )
    ]
    headers = (
        "kind",
        "parser",
        "dataset",
        "size",
        "ms/op",
        "ops/s",
        "peak KiB",
        "delta",
    )
    widths = [
        max(len(header), *(len(row[index]) for row in rows)) for index, header in enumerate(headers)
    ]
    formatted = [
        " | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)),
        "-+-".join("-" * width for width in widths),
    ]
    formatted.extend(
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    )
    return formatted


def test_perf_scope_matches_public_parser_helpers() -> None:
    assert_build_coverage_is_complete()
    actual_public_validators = {
        name
        for name in dir(sut)
        if name.startswith("is_valid_syntax_") and callable(getattr(sut, name))
    }
    expected_public_validators = {api_name for api_name, _, _ in VALIDATOR_APIS}
    assert actual_public_validators == expected_public_validators


@pytest.mark.parametrize(
    ("parser_name", "rule_name", "build_api"),
    build_benchmark_cases(),
    ids=lambda value: value if isinstance(value, str) else getattr(value, "__name__", "callable"),
)
def test_perf_parser_build_time(
    parser_name: str,
    rule_name: str,
    build_api: Callable[[], Any],
) -> None:
    settings = perf_settings()

    def build_round() -> None:
        for _ in range(settings["build_iterations_per_round"]):
            built = build_api()
            assert built is not None

    metrics = measure_resource_usage(
        build_round,
        operation_count_per_round=settings["build_iterations_per_round"],
    )
    record_perf_result(
        benchmark_kind="build",
        parser_name=parser_name,
        rule_name=rule_name,
        dataset_name="build",
        dataset_size=settings["build_iterations_per_round"],
        metrics=metrics,
    )


@pytest.mark.parametrize("dataset_name", dataset_names())
@pytest.mark.parametrize(
    ("parser_name", "rule_name", "_sample_rule_name", "parse_api"),
    parse_benchmark_cases(),
    ids=lambda value: value if isinstance(value, str) else getattr(value, "__name__", "callable"),
)
def test_perf_parse_runtime(
    parser_name: str,
    rule_name: str,
    _sample_rule_name: str,
    parse_api: Callable[[str], Any],
    dataset_name: str,
) -> None:
    corpus = build_corpus(rule_name, dataset_name)
    repetitions = perf_settings()["parse_corpus_repetitions_per_round"]

    metrics = measure_resource_usage(
        lambda: run_parse_corpus(parse_api, corpus),
        operation_count_per_round=len(corpus) * repetitions,
    )
    record_perf_result(
        benchmark_kind="parse",
        parser_name=parser_name,
        rule_name=rule_name,
        dataset_name=dataset_name,
        dataset_size=len(corpus),
        metrics=metrics,
    )


def test_perf_summary_output() -> None:
    assert PERF_RESULTS, "No performance results were collected."

    print("")
    print("Performance environment")
    print(f"- Python: {sys.version}")
    print(f"- Platform: {platform.platform()}")
    print(f"- Lark: {lark.__version__}")
    print(f"- Mode: {os.environ.get(PERF_MODE_ENV, 'full')}")
    print("")
    for line in format_summary_table():
        print(line)

    written_path = write_perf_results()
    if written_path is not None:
        print("")
        print(f"Wrote machine-readable perf results to {written_path}")
