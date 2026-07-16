# rfc3987-syntax2

[![shield_pypi-version]][link_pypi]
[![shield_gh-workflow-test]][link_gh-workflow-test]
[![shield_license]][license_file]

----

Helper functions to parse and validate the **syntax** of terms defined in **[RFC 3987](https://www.rfc-editor.org/info/rfc3987)** — the IETF standard for Internationalized Resource Identifiers (IRIs).

> [!NOTE]  
> This is a maintained fork of <https://github.com/willynilly/rfc3987-syntax>.

## 🎯 Purpose

The goal of `rfc3987-syntax2` is to provide a **lightweight, permissively licensed Python module** for validating that strings conform to the **ABNF grammar defined in RFC 3987** (with delegated productions from RFC 3986 where RFC 3987 explicitly reuses them).

These helpers are:

- ✅ Strictly aligned with the **syntax rules of RFC 3987**
- ✅ Built using a **permissive MIT license**
- ✅ Designed for both **open source and proprietary use**
- ✅ Powered by [Lark](https://github.com/lark-parser/lark), a fast, EBNF-based parser

> 🧠 **Note:** This project focuses on **syntax validation only**.  
> RFC 3987 also defines semantic and processing requirements (for example Unicode normalization expectations, BiDi constraints, and IRI↔URI mapping behavior) that are intentionally out of scope for this package.

## 📄 License, Attribution, and Citation

**`rfc3987-syntax2`** is licensed under the [MIT License][license_file], which allows reuse in both open source and commercial software.

This project:

- ❌ Does **not** depend on the `rfc3987` Python package (GPL-licensed)
- ✅ Uses [`lark`](https://github.com/lark-parser/lark), licensed under MIT
- ✅ Implements grammar derived from **[RFC 3987](https://datatracker.ietf.org/doc/html/rfc3987)** and its normative dependencies on **[RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986)**

> ⚠️ This project is **not affiliated with or endorsed by** the authors of RFC 3987 or the `rfc3987` Python package.

## ⚠️ Limitations

The grammar/parser enforce **ABNF-level syntax only**. They do **not** enforce all semantic/procedural requirements from RFC 3987 and related specs.

Examples of intentionally out-of-scope validation include:

- ❌ Unicode **Normalization Form C (NFC)** enforcement
- ❌ Bidirectional text (**BiDi**) rule enforcement (RFC 3987 §4.1)
- ❌ Context-aware IRI↔URI mapping policy checks
- ❌ Port range policy checks beyond syntax (e.g., numeric bounds such as 0–65535)
- ❌ Higher-level host/network canonicalization or resolution semantics

ChatGPT-4o was used during parts of original development. Errors may exist. Additional review, testing, and bug fixes by human experts are welcome.

## 📦 Installation

```sh
pip install rfc3987-syntax2
```

## 🛠 Usage

### List all supported terms

```python
from rfc3987_syntax2 import RFC3987_SYNTAX_TERMS

print("Supported terms:")
for term in RFC3987_SYNTAX_TERMS:
    print(term)
```

### Validate syntax with the generic validator

```python
from rfc3987_syntax2 import is_valid_syntax

if is_valid_syntax(term='iri', value='http://github.com'):
    print("✓ Valid IRI syntax")

if not is_valid_syntax(term='iri', value='bob'):
    print("✗ Invalid IRI syntax")

if is_valid_syntax(term='iri_reference', value='bob'):
    print("✓ Valid IRI-reference syntax")
```

### Or use term-specific helpers

```python
from rfc3987_syntax2 import is_valid_syntax_iri
from rfc3987_syntax2 import is_valid_syntax_iri_reference

if is_valid_syntax_iri('http://github.com'):
    print("✓ Valid IRI syntax")

if not is_valid_syntax_iri('bob'):
    print("✗ Invalid IRI syntax")

if is_valid_syntax_iri_reference('bob'):
    print("✓ Valid IRI-reference syntax")
```

### Get a Lark parse tree

```python
from lark import Tree as ParseTree
from rfc3987_syntax2 import parse

ptree: ParseTree = parse(term="iri", value="http://github.com")
print(ptree)
```

## 📚 Sources

This grammar is based on:

- **RFC 3987 – Internationalized Resource Identifiers (IRIs)**  
  → Primary source for `IRI`, `IRI-reference`, and `i*` grammar productions  
  → https://datatracker.ietf.org/doc/html/rfc3987

- **RFC 3986 – Uniform Resource Identifier (URI): Generic Syntax**  
  → Source for foundational URI productions reused by RFC 3987 (e.g., `scheme`, `port`, `ipv4address`, `ipv6address`, `pct-encoded`, character classes)  
  → https://datatracker.ietf.org/doc/html/rfc3986

> 📝 Attribution policy used in this project:
> - Productions named with `i...` are treated as RFC 3987 productions.
> - Non-`i` foundational productions reused by RFC 3987 are attributed to RFC 3986.

### Rule-to-Source Mapping (aligned to current grammar)

| Rule/Component | Source | Notes |
|---|---|---|
| `iri` | RFC 3987 | Top-level IRI rule |
| `iri_reference` | RFC 3987 | Top-level IRI-reference rule |
| `absolute_iri` | RFC 3987 | Absolute IRI rule |
| `ihier_part` | RFC 3987 | IRI hierarchy |
| `irelative_ref` | RFC 3987 | Relative IRI-reference |
| `irelative_part` | RFC 3987 | Relative IRI hierarchy |
| `iauthority` | RFC 3987 | IRI authority production |
| `ihost` | RFC 3987 | IRI host production |
| `ireg_name` | RFC 3987 | IRI reg-name (Unicode-capable via `iunreserved`) |
| `iuserinfo` | RFC 3987 | IRI userinfo |
| `ipath` | RFC 3987 | IRI path union |
| `ipath_abempty` | RFC 3987 | IRI path variant |
| `ipath_absolute` | RFC 3987 | IRI path variant |
| `ipath_noscheme` | RFC 3987 | IRI path variant |
| `ipath_rootless` | RFC 3987 | IRI path variant |
| `ipath_empty` | RFC 3987 | Empty IRI path |
| `isegment` | RFC 3987 | IRI segment |
| `isegment_nz` | RFC 3987 | Non-empty IRI segment |
| `isegment_nz_nc` | RFC 3987 | Non-empty, no-colon first segment form |
| `ipchar` | RFC 3987 | IRI path character |
| `iquery` | RFC 3987 | IRI query |
| `ifragment` | RFC 3987 | IRI fragment |
| `iunreserved` | RFC 3987 | Includes `ucschar` |
| `ucschar` | RFC 3987 | Unicode range class |
| `iprivate` | RFC 3987 | Private-use Unicode range class |
| `scheme` | RFC 3986 | Reused foundational URI production |
| `sub_delims` | RFC 3986 | Reused delimiters |
| `ip_literal` | RFC 3986 | Bracketed literal host |
| `ipvfuture` | RFC 3986 | IPvFuture form |
| `ipv6address` | RFC 3986 | IPv6 ABNF syntax only |
| `ls32` | RFC 3986 | IPv6 helper production |
| `h16` | RFC 3986 | IPv6 helper production |
| `ipv4address` | RFC 3986 | Dotted-decimal IPv4 syntax |
| `dec_octet` | RFC 3986 | IPv4 octet syntax |
| `port` | RFC 3986 | `*DIGIT` syntax only |
| `pct_encoded` | RFC 3986 | Percent-encoded triplet |
| `alpha` | RFC 3986 | Character class |
| `digit` | RFC 3986 | Character class |
| `hexdig` | RFC 3986 | Character class |
| `non_zero` | Project helper | Convenience token used to express `dec_octet` |
| `unreserved` | RFC 3986 | Used by `ipvfuture` branch |

## ✅ Scope statement (quick reference)

`rfc3987-syntax2` answers:  
**“Does this string match the RFC ABNF syntax for the requested term?”**

It does **not** answer:  
**“Is this identifier semantically valid in all RFC processing contexts?”**

[shield_gh-workflow-test]: https://img.shields.io/github/actions/workflow/status/jkowalleck/rfc3987-syntax2/python-tests.yml?branch=main&logo=GitHub&logoColor=white "tests"
[shield_pypi-version]: https://img.shields.io/pypi/v/rfc3987-syntax2?logo=Python&logoColor=white&label=PyPI "PyPI"
[shield_license]: https://img.shields.io/github/license/jkowalleck/rfc3987-syntax2?logo=open%20source%20initiative&logoColor=white "license"

[link_pypi]: https://pypi.org/project/rfc3987-syntax2/
[link_gh-workflow-test]: https://github.com/jkowalleck/rfc3987-syntax2/actions/workflows/python-tests.yml?query=branch%3Amain
[license_file]: https://github.com/jkowalleck/rfc3987-syntax2/blob/main/LICENSE
