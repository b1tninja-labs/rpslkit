# Changelog

The format follows Keep a Changelog, and this project adheres to Semantic Versioning.

## Unreleased

### Added

- `parser.parse` and `parser.parse_lenient`: RFC 2622 section 2 object text with continuation lines,
  comments, attribute order, the exact source text of each object and a source name.
- `ranges`: address prefix ranges and the range operators of RFC 2622 section 2 with the published
  equivalence table as tests; IPv6 under RFC 4012 section 2.4.

The rest of the package is a shell: the public surface exists as typed stubs that raise
`NotImplementedError`, and [ROADMAP.md](ROADMAP.md) lists what has to happen first.

## 0.0.0 - 2026-11-05

### Added

- Package skeleton, obligation matrix and CI gates for rpslkit.
- `rpslkit.apps` namespace reserved for composition that is not protocol behaviour.
