# rpslkit

<!-- PyPI badges go live with the first release. Until then a version badge renders
     "no version" on the landing page, which reads as a defect rather than a date, so
     the badges stay commented out until the tag exists.
-->

**Pre-alpha shell.** The package surface, the obligation matrix and the CI gates exist.
No protocol behaviour is implemented: every public function raises `NotImplementedError`,
and the test suite records that rather than hiding it. Read
[ROADMAP.md](ROADMAP.md) before depending on any of it.

rpslkit -- RPSL parsing and IRR queries without a decade old dependency

IRR is still the origin authority most operators filter on, and Python's only serious tool, irrtree, last shipped 1.4.0 on 2021-06-24. Worse, the obvious package names are gone: rpsl is a Raspberry Pi sensor library and irr is a numpy joke. RFC 2622 defines the language, carries 3 verified errata and is updated by RFC 4012 and RFC 7909, and the databases disagree with each other in ways a library should surface rather than hide. rpslkit parses RPSL, queries the IRRs concurrently, resolves route sets, and reports conflicts between IRR, RPKI and observed routing as first class output.

## The gap, with a date

PyPI was queried on 2026-11-05 for this name and for every neighbouring project. Landscape
claims rot quickly: two projects in this portfolio shipped within five days of the survey,
which is why the table below carries dates instead of adjectives.

| Project | Version | Last release | Why it is not this project |
|---|---|---|---|
| irrtree | 1.4.0 | 2021-06-24 | the working solution, four years without a release, no asyncio |
| rpsl | 0.1.dev1 | 2019-11-30 | a Raspberry Pi sensor library squatting the acronym |
| irr | 0.2 | 2021-09-28 | a numpy joke |

What this project intends to add:

- a RPSL parser that keeps source, references and comments so provenance survives
- concurrent queries to RIPE, RADB, NTTC, AltDB and the regional archives with per source policy
- route set and as set expansion with cycle detection and explicit ambiguity reporting
- conflict output comparing IRR assertions against RPKI assertions and observed routing
- prefix match semantics that say which object matched and why

## Specification spine

Status and publication dates below were read from the RFC Editor record on 2026-11-05. A
section number is cited only where that section was read in full; everything else cites the
document, which is the honest grain size for a plan. See [docs/rfc-map.md](docs/rfc-map.md).

| Document | Status | Published | What it gives this project |
|---|---|---|---|
| RFC 2622 | Proposed Standard | 1999-06 | RPSL: object definitions, the set expression grammar and the delete syntax |
| RFC 4012 | Proposed Standard | 2005-02 | digest objects for secure route origin registration |
| IRRd database query interface | operational practice | - | whois style queries, the newer HTTP and REST interfaces, and per database syntax quirks |

### Errata watch

- RFC 2622 carries 3 verified errata and is updated by RFC 4012 and RFC 7909; RFC 7909 adds the as-set import semantics that most parsers get wrong. Verify both before M2.
- The four large IRRs differ in practice on comments, mangling and mirroring latency. Treat divergence as data and record which database answered.

## Module layout

| Module | Responsibility |
|---|---|
| `objects` | RPSL object classes, attributes and the reserved word set (RFC 2622) |
| `parser` | lenient line parsing that preserves source and comments (RFC 2622) |
| `sets` | route set and as set expansion with cycles and imports (RFC 2622, RFC 7909) |
| `client` | whois and HTTP queries with timeouts and per source budgets |
| `resolve` | origin resolution for a prefix with ambiguity preserved |
| `compare` | IRR against RPKI and against observed routing |
| `sources` | registry of IRR databases, endpoints and quirks |

## What it does not do

- generating router configuration from RPSL
- being an IRR server or handling maintainer authentication and object updates
- validating route authorisation policy, which is rpkit and pkix


## Install

```bash
git clone https://github.com/b1tninja/rpslkit.cd rpslkit
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
```

Not published to PyPI yet. The name is reserved for this repository's trusted publisher at
the moment of the first release.

## Development

All four gates must pass, on Linux and Windows alike:

```bash
ruff check . && ruff format --check .
mypy rpslkit
pytest -q --cov
python -O -m pytest -q
```

The last line is the one that matters most in a protocol library. `-O` strips `assert`, and a
parser whose bounds checks were asserts stops being a parser under production flags. Wire
paths raise named exceptions; asserts belong in tests and nowhere else.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
