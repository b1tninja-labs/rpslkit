# Specification completeness -- and the roadmap it implies

This is the project's north star: every protocol obligation rpslkit could plausibly take on,
with an honest status against the code at `HEAD`. It is blunt about gaps on purpose. A
roadmap that overstates its coverage is not a plan, it is marketing.

**The honesty rule:** a row may read `[ok]` only when a named test would fail if the
behaviour regressed. Reading the code and agreeing with it is not enough. That is how
"decoded but never sent" quietly becomes "implemented".

Legend: `[ok]` implemented and pinned by a named test -- `[part]` partial, with what is
missing stated -- `[ ]` not implemented -- `[no]` deliberate non-goal.

A Where cell marked `(to be written)` names the test that will pin the row once it exists; no
such test has been written yet, and the row cannot leave `[ ]` until it has. The Milestone
column places the row on the ladder in section 2, and `-` means it is not placed yet.

Update the affected row in the same commit that changes the behaviour. A row and its test
drift apart within one release, and the document becomes useless exactly when it is needed.

## 1. Obligations

| Obligation | Spec | Status | Where | Milestone |
|---|---|---|---|---|
| `parser.parse()` | RFC 2622 section 2 | `[ok]` | `tests/test_parser.py::test_parse_route_objects_from_rfc_section_4_figure_8`, `tests/test_parser.py::test_continuation_space_tab_plus`, `tests/test_parser.py::test_raw_is_the_exact_input_slice_and_not_rebuilt` | M1 |
| `parser.parse_lenient()` | RFC 2622 section 2 | `[ok]` | `tests/test_parser.py::test_no_colon_line_is_syntax_error_strict_and_issue_lenient`, `tests/test_parser.py::test_non_ascii_in_value_strict_refuses_lenient_keeps_with_issue` | M1 |
| `ranges.parse_prefix_range()` | RFC 2622 section 2; RFC 4012 section 2.4 | `[ok]` | `tests/test_ranges.py::test_published_member_examples`, `tests/test_ranges.py::test_operator_on_operator_is_error` | M4 |
| `ranges.apply_operator()` | RFC 2622 section 2 | `[ok]` | `tests/test_ranges.py::test_published_set_equivalence`, `tests/test_ranges.py::test_published_equivalence_with_empty_result` | M4 |
| `ranges.contains()` | RFC 2622 section 2 | `[ok]` | `tests/test_ranges.py::test_member_must_lie_inside_the_network`, `tests/test_ranges.py::test_ipv4_range_applied_to_ipv6_prefix_never_matches` | M4 |
| `parser.parse-bytes` | RFC 2622 section 2 (ASCII only) | `[ ]` | `tests/test_parser.py::test_parse_bytes` (to be written) | M1 |
| `parser.class-first` | RFC 2622 section 2 ("should be specified first") | `[ ]` | `tests/test_parser.py::test_class_attribute_first` (to be written) | M1 |
| `names.validate` | RFC 2622 section 2 | `[ ]` | `tests/test_names.py::test_validate` (to be written) | M3 |
| `objects.matches_prefix()` | RFC 2622 | `[ ]` | `tests/test_obligations.py::test_matches_prefix` (to be written) | M4 |
| `sets.expand()` | RFC 2622 section 5 | `[ ]` | `tests/test_obligations.py::test_expand` (to be written) | M3 |
| `client.query()` | design | `[ ]` | `tests/test_obligations.py::test_query` (to be written) | M2 |
| `resolve.origins()` | RFC 2622 | `[ ]` | `tests/test_obligations.py::test_origins` (to be written) | M4 |
| `compare.conflicts()` | design | `[ ]` | `tests/test_obligations.py::test_conflicts` (to be written) | M5 |
| `objects.route-view` | RFC 2622 section 4; RFC 4012 section 3 | `[ ]` | `tests/test_objects.py::test_route_view` (to be written) | M4 |
| `objects.set-views` | RFC 2622 section 5; RFC 4012 section 4 (`mp-members`) | `[ ]` | `tests/test_objects.py::test_set_views` (to be written) | M3 |
| `sets.expand-flat` | RFC 2622 section 5.1 | `[ ]` | `tests/test_sets.py::test_expand_flat` (to be written) | M3 |
| `sets.expand-route-set` | RFC 2622 sections 5.2, 5.3 and errata 8243 | `[ ]` | `tests/test_sets.py::test_expand_route_set` (to be written) | M3 |
| `sets.report` | design | `[ ]` | `tests/test_sets.py::test_report` (to be written) | M3 |
| `client.whois-query` | RFC 3912; IRRd query interface | `[ ]` | `tests/test_client.py::test_whois_query` (to be written) | M2 |
| `client.rate-policy` | design | `[ ]` | `tests/test_client.py::test_rate_policy` (to be written) | M2 |
| `parser.signature-preserved` | RFC 7909 | `[ ]` | `tests/test_parser.py::test_signature_attribute_preserved` (to be written) | M1 |
| `parser.geofeed-preserved` | RFC 9632 section 3 | `[ ]` | `tests/test_parser.py::test_geofeed_attribute_preserved` (to be written) | M1 |
| `corpus.fixtures` | design | `[ ]` | `tests/test_corpus.py::test_fixture_provenance` (to be written) | M1 |

## 2. Milestones

- M1 RPSL parser with round trip preserving comments and source
- M2 whois and HTTP clients for the four major databases (do after M3 and M4: most of the evidence is offline; `parser` and `ranges` need no network)
- M3 set expansion with cycle detection and ambiguity output
- M4 prefix origin resolution with provenance per answer
- M5 the IRR against RPKI against observed comparison
- M6 publication: 0.1.0

Every milestone is accepted by its rows above flipping to `[ok]` with a named test, not by
the code existing. Coverage in `pyproject.toml` ratchets in the same commit.

## 3. Errata watch

- RFC 2622 carries 3 verified errata and is updated by RFC 4012 and RFC 7909; RFC 4012 adds the IPv6 and multicast policy extensions and RFC 7909 adds a signature attribute validated against the RPKI (rfclib, 2026-11-07). Verify both before M2.
- RFC 2622 verified errata, read 2026-11-13: 6588 (typo "authenticaiton", editorial); 7564 (technical, section 5.6: the peering-set example has `AS3 at 9.9.9.1` where the text printed `AS1 at 9.9.9.1`; matters only to a test built on that example, none exists yet); 8243 (editorial, the section 5.3 heading is misplaced inside 5.2 and the `rs-any` sentences belong to 5.3). Section 2, which the parser and ranges implement, has none.
- RFC 4012 and RFC 2725 and RFC 7909 have no errata (rfclib, 2026-11-13). RFC 4012 section 2.4 cites RFC 3513 for IPv6 text forms; RFC 3513 is obsolete, replaced by RFC 4291.
- The four large IRRs differ in practice on comments, mangling and mirroring latency. Treat divergence as data and record which database answered.

## 4. Deliberate non-goals

| Non-goal | Status | Revisit when |
|---|---|---|
| generating router configuration from RPSL | `[no]` | a named document requires it |
| being an IRR server or handling maintainer authentication and object updates | `[no]` | a named document requires it |
| validating route authorisation policy, which is rpkit | `[no]` | a named document requires it |

## 5. Open questions

- **IPv6 range maximum.** RFC 4012 section 2.4 says the IPv6 range operator is that of RFC 2622 section 2 and does not state the maximum length; `ranges` uses 128. Owner or IRRd documentation to confirm.
- **Whitespace-only line.** RFC 2622 section 2 says a blank line ends an object and a space starts a continuation; a line of only spaces is both. The parser treats it as blank (dumps carry such lines). Compare with IRRd and RIPE behaviour on a real dump before M2.
- **Non-ASCII text.** The RFC allows ASCII only; IRR dumps carry Latin-1 and UTF-8 in free text. `parse` refuses, `parse_lenient` keeps and reports. Whether `parse_bytes` decodes Latin-1 is undecided.
- **Prefix ranges that select nothing** (`^8-12` on a /16, `^-` on a /32) are refused by `ranges.parse_prefix_range`; the RFC does not call them errors. Refused so far because a silent empty range hides a typo; reconsider against real dumps.
- **Plan statement.** `docs/plan.md` says "Depends on: None". True for M1 to M4; M5 (IRR against RPKI against observed) consumes rpkit and routevalid data shapes, and M2 `client.whois_query` overlaps the RFC 3912 client already in registrata. The plan is generated; the correction belongs in PORTFOLIO.md.
- **One budget implementation or two?** `client.rate_policy` and bgpfeed's per-source budget are the same design; decide the owner.
- **RFC 7909 `signature:`** is parse-and-preserve only in 0.1 unless the owner accepts a CMS and RPKI validation dependency on signeddata and rpkit.

## 6. Publication checklist

- [ ] every `[ ]` row above either `[ok]` or moved to a named later milestone
- [ ] `docs/research.md` claims re-verified and the dated ones either promoted or deleted
- [ ] interoperability evidence recorded in `docs/` against a non-Python implementation
- [ ] `tools/check_dist.py` proves the wheel ships the fixtures the README promises
- [ ] version 0.1.0 tagged, trusted publisher configured, README badges uncommented
