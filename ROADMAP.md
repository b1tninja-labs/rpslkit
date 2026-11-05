# Specification completeness -- and the roadmap it implies

This is the project's north star: every protocol obligation rpslkit could plausibly take on,
with an honest status against the code at `HEAD`. It is blunt about gaps on purpose. A
roadmap that overstates its coverage is not a plan, it is marketing.

**The honesty rule:** a row may read `[ok]` only when a named test would fail if the
behaviour regressed. Reading the code and agreeing with it is not enough. That is how
"decoded but never sent" quietly becomes "implemented".

Legend: `[ok]` implemented and pinned by a named test -- `[part]` partial, with what is
missing stated -- `[ ]` not implemented -- `[no]` deliberate non-goal.

Update the affected row in the same commit that changes the behaviour. A row and its test
drift apart within one release, and the document becomes useless exactly when it is needed.

## 1. Obligations

| Obligation | Spec | Status | Where |
|---|---|---|---|
| `parser.parse()` | RFC 2622 | `[ ]` | `tests/test_obligations.py::parse` |
| `objects.matches_prefix()` | RFC 2622 | `[ ]` | `tests/test_obligations.py::matches_prefix` |
| `sets.expand()` | RFC 7909 | `[ ]` | `tests/test_obligations.py::expand` |
| `client.query()` | design | `[ ]` | `tests/test_obligations.py::query` |
| `resolve.origins()` | RFC 2622 | `[ ]` | `tests/test_obligations.py::origins` |
| `compare.conflicts()` | design | `[ ]` | `tests/test_obligations.py::conflicts` |

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

- RFC 2622 carries 3 verified errata and is updated by RFC 4012 and RFC 7909; RFC 7909 adds the as-set import semantics that most parsers get wrong. Verify both before M2.
- The four large IRRs differ in practice on comments, mangling and mirroring latency. Treat divergence as data and record which database answered.

## 4. Deliberate non-goals

| Non-goal | Status | Revisit when |
|---|---|---|
| generating router configuration from RPSL | `[no]` | a named document requires it |
| being an IRR server or handling maintainer authentication and object updates | `[no]` | a named document requires it |
| validating route authorisation policy, which is rpkit and pkix | `[no]` | a named document requires it |

## 5. Open questions

- none recorded yet

## 6. Publication checklist

- [ ] every `[ ]` row above either `[ok]` or moved to a named later milestone
- [ ] `docs/research.md` claims re-verified and the dated ones either promoted or deleted
- [ ] interoperability evidence recorded in `docs/` against a non-Python implementation
- [ ] `tools/check_dist.py` proves the wheel ships the fixtures the README promises
- [ ] version 0.1.0 tagged, trusted publisher configured, README badges uncommented
