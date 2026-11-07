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
| `parser.parse()` | RFC 2622 | `[ ]` | `tests/test_obligations.py::test_parse` (to be written) | M1 |
| `objects.matches_prefix()` | RFC 2622 | `[ ]` | `tests/test_obligations.py::test_matches_prefix` (to be written) | M4 |
| `sets.expand()` | RFC 2622 section 5 | `[ ]` | `tests/test_obligations.py::test_expand` (to be written) | M3 |
| `client.query()` | design | `[ ]` | `tests/test_obligations.py::test_query` (to be written) | M2 |
| `resolve.origins()` | RFC 2622 | `[ ]` | `tests/test_obligations.py::test_origins` (to be written) | M4 |
| `compare.conflicts()` | design | `[ ]` | `tests/test_obligations.py::test_conflicts` (to be written) | M5 |

## 2. Milestones

- M1 RPSL parser with round trip preserving comments and source
- M2 whois and HTTP clients for the four major databases
- M3 set expansion with cycle detection and ambiguity output
- M4 prefix origin resolution with provenance per answer
- M5 the IRR against RPKI against observed comparison
- M6 publication: 0.1.0

Every milestone is accepted by its rows above flipping to `[ok]` with a named test, not by
the code existing. Coverage in `pyproject.toml` ratchets in the same commit.

## 3. Errata watch

- RFC 2622 carries 3 verified errata and is updated by RFC 4012 and RFC 7909; RFC 4012 adds the IPv6 and multicast policy extensions and RFC 7909 adds a signature attribute validated against the RPKI (rfclib, 2026-11-07). Verify both before M2.
- The four large IRRs differ in practice on comments, mangling and mirroring latency. Treat divergence as data and record which database answered.

## 4. Deliberate non-goals

| Non-goal | Status | Revisit when |
|---|---|---|
| generating router configuration from RPSL | `[no]` | a named document requires it |
| being an IRR server or handling maintainer authentication and object updates | `[no]` | a named document requires it |
| validating route authorisation policy, which is rpkit | `[no]` | a named document requires it |

## 5. Open questions

- none recorded yet

## 6. Publication checklist

- [ ] every `[ ]` row above either `[ok]` or moved to a named later milestone
- [ ] `docs/research.md` claims re-verified and the dated ones either promoted or deleted
- [ ] interoperability evidence recorded in `docs/` against a non-Python implementation
- [ ] `tools/check_dist.py` proves the wheel ships the fixtures the README promises
- [ ] version 0.1.0 tagged, trusted publisher configured, README badges uncommented
