# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

<!-- unreleased things below this line -->

* Fixed
  * Fix `RFC3987_SYNTAX_TERMS` correctly containing "ipath" (via [#41])
  * Fix `RFC3987_SYNTAX_TERMS` correctly containing "ipath_absolute" (via [#41])
  * Fix `RFC3987_SYNTAX_TERMS` correctly containing "ipath_noscheme" (via [#41])
  * Fix `RFC3987_SYNTAX_TERMS` correctly containing "ipath_rootless" (via [#41])
  * Fix `RFC3987_SYNTAX_TERMS` correctly containing "ipath_empty" (via [#41])
  * Fix `ucschar` range (via [#45])
  * Typehint of `parse()`'s arg `term` (via [#50], [#52])  
    Narrowed down to valid values: "iri", "iri_reference", "absolute_iri"
  * Typehint of `is_valid_syntax`'s arg `term` (via [#50], [#52])  
    Narrowed down to valid values: "iri", "iri_reference", "absolute_iri"
* Added
  * Function `is_valid_syntax_scheme` (via [#48])
  * Function `is_valid_syntax_non_zero` (via [#48])
  * Function `is_valid_syntax_pct_encoded` (via [#48])
  * Dict `RFC3987_SYNTAX_TERM_VALIDATORS` mapping `RFC3987_SYNTAX_TERMS` to validator function (via [#49])
* Performance
  * Public symbols use lazy loading (via [#43])
* Tests
  * Add grammar regression tests (via [#48])

[#41]: https://github.com/jkowalleck/rfc3987-syntax2/pull/41
[#43]: https://github.com/jkowalleck/rfc3987-syntax2/pull/43
[#45]: https://github.com/jkowalleck/rfc3987-syntax2/pull/45
[#48]: https://github.com/jkowalleck/rfc3987-syntax2/pull/48
[#49]: https://github.com/jkowalleck/rfc3987-syntax2/pull/49
[#50]: https://github.com/jkowalleck/rfc3987-syntax2/pull/50
[#52]: https://github.com/jkowalleck/rfc3987-syntax2/pull/52

## v1.2.0 - 2026-07-16

* Fixed
  * Align RFC 3987 grammar handling with the specification (via [#10])
  * Fix RFC 3986-delegated IRI parsing edge cases (via [#10])
  * Fix `RFC3987_SYNTAX_TERMS` correctly containing "irelative_part" `(via [#19])
  * Fix `RFC3987_SYNTAX_TERMS` correctly containing "ihier_part" `(via [#19])
* Changed
  * Update grammar rules used by `is_valid_syntax(...)` and term-specific validators (via [#10])
* Added
  * Validate IPv6 compression (via [#10])
  * Assert static typing (via [#16])
* Tests
  * Add grammar regression tests (via [#10])

[#10]: https://github.com/jkowalleck/rfc3987-syntax2/pull/10
[#16]: https://github.com/jkowalleck/rfc3987-syntax2/pull/16
[#19]: https://github.com/jkowalleck/rfc3987-syntax2/pull/19

## v1.1.1 - 2026-07-14

### Fork release `rfc3987-syntax2`
* Forked from [`willynilly/rfc3987-syntax`](https://github.com/willynilly/rfc3987-syntax).
* Published this project as an independently maintained package under the new distribution name `rfc3987-syntax2`.
* Preserved upstream functionality as the baseline for this initial fork release.

### Notes for `rfc3987-syntax2`
* This is the first release of the fork.
* No intentional behavioral changes from upstream are introduced in this release unless explicitly listed above.

## v1.1.0 - 2025-07-18

Original release: <https://github.com/willynilly/rfc3987-syntax/releases/tag/v1.1.0>

* Features
  * Added add support for IRI-reference and absolute-IRI
* Bugs
  * Fixed single quote sub-delimiter

## v1.0.0 - 2025-05-18

Original release: <https://github.com/willynilly/rfc3987-syntax/releases/tag/v1.0.0>
