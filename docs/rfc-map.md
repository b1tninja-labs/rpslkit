# Where every claim in this repository comes from

| Document | Status | Published | Verified against the publisher record on |
|---|---|---|---|
| RFC 4012 | Proposed Standard, current, no errata, updated by RFC 7909 | 2005-03 | 2026-11-13 |
| RFC 7909 | Proposed Standard, current, no errata; `signature:` attribute, parse-and-preserve only until the owner accepts CMS and RPKI validation | 2016-06 | 2026-11-13 |
| IRRd database query interface | operational practice | - | 2026-11-05 |
| RFC 2622 (updated by RFC 4012, RFC 7909; obsoletes RFC 2280) | Proposed Standard, current, 3 verified errata (6588, 7564, 8243) | 1999-06 | 2026-11-13 |
| RFC 2725 (updated by RFC 4012) | Proposed Standard, current, no errata; authorisation model, background for the non-goal on maintainer authentication | 1999-12 | 2026-11-13 |
| RFC 2650 | Informational, current, no errata; RPSL in practice, a tutorial, for ambiguity rules | 1999-08 | 2026-11-13 |
| RFC 4291 | Draft Standard, current; replaces RFC 3513, which RFC 4012 section 2.4 cites for IPv6 text forms (RFC 3513 is obsolete) | 2006-02 | 2026-11-13 |
| RFC 9632 | Proposed Standard, current, no errata; `geofeed:` attribute on `inetnum`, parse-and-preserve | 2024-08 | 2026-11-13 |
| RFC 3912 | Draft Standard, current, no errata; WHOIS transport, also implemented in registrata | 2004-09 | 2026-11-13 |
| RFC 5943 | Proposed Standard, current; `pingable` attribute on route and route6 (found by search, not read) | - | 2026-11-13 |

Citation rules, in the order they most often get broken:

1. Cite the document. A secondary write-up is a lead, not a source.
2. A section number is cited only if that section was read in full.
3. Errata are checked at each milestone freeze, not once at the start.
4. Where a claim came from a body outside the RFC series, that body is named here.

Re-verify with the RFC library rather than memory: `info('RFCnnnn')` for current status, `errata('RFCnnnn')` for corrections, and `read('RFCnnnn', view='normative')` for the MUST and SHOULD statements that become obligation rows.

## Sections read in full

RFC 2622 sections 2, 3.2, 3.3 and 4 (parser and ranges); RFC 4012 sections 2.4, 3 and 4.2. Appendix B (the grammar) and sections 5 to 9 are not yet read; the parser takes no class grammar from them.

Test vectors: RFC 2622 section 2 paragraphs 8 to 16 (prefix forms, operators and the published equivalence table), section 4 Figure 8 (route objects) and section 3.2 Figure 4 (person object).

The IPv6 maximum prefix length of 128 in `ranges` is an inference: RFC 4012 section 2.4 only says the range operator is the one of RFC 2622 section 2.
