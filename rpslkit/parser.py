"""RPSL object text parser that preserves source, comments and the original text (RFC 2622 section 2).

Reading rules, each from RFC 2622 section 2 unless marked as policy:

* an object is a list of attribute-value pairs, one per line, and ends at a blank line;
* the attribute name starts at column 0 and is followed by ``:``;
* a value continues on lines whose first character is a space, a tab or ``+``;
  a ``+`` line may carry no text, so a value can contain blank lines;
* a comment starts at the first ``#`` on a line and ends at the end of the line;
* the order of the attributes is significant and a name may repeat;
* RPSL is case insensitive and ASCII only.

Policy, where the RFC is silent or an implementation must decide:

* a line holding only whitespace ends an object, like an empty line (dumps carry them);
* a column-0 ``#`` line is a comment, kept in :attr:`RpslObject.comments`;
* the class of an object is the name of its first attribute, lower-cased; whether that
  attribute really is the class attribute needs the class table, which is not read here;
* :func:`parse` refuses non-ASCII text and control characters, :func:`parse_lenient`
  keeps the line and reports it.

``raw`` is a slice of the input, never rebuilt from the parsed fields. No regular
expression runs over more than one line.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "MAX_ATTRIBUTES",
    "MAX_LINE_LENGTH",
    "Attribute",
    "ParseIssue",
    "RpslObject",
    "RpslSyntaxError",
    "parse",
    "parse_lenient",
]

MAX_LINE_LENGTH = 65_536
MAX_ATTRIBUTES = 100_000

_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
_CONTINUATION = (" ", "\t", "+")

_KEYS: dict[str, tuple[str, ...]] = {
    "mntner": ("mntner",),
    "person": ("nic-hdl",),
    "role": ("nic-hdl",),
    "route": ("route", "origin"),
    "route6": ("route6", "origin"),
    "as-set": ("as-set",),
    "route-set": ("route-set",),
    "filter-set": ("filter-set",),
    "peering-set": ("peering-set",),
    "rtr-set": ("rtr-set",),
    "aut-num": ("aut-num",),
    "inet-rtr": ("inet-rtr",),
}


@dataclass(frozen=True)
class Attribute:
    """One attribute-value pair.

    ``value`` holds the text after the colon with comments removed; continuation lines are
    joined with a newline and each line is stripped of the continuation character and of
    surrounding white space. ``comment`` joins the comments of all the lines of the pair
    with a newline, or is ``None``. ``line`` is the 1-based line of the name.
    """

    name: str
    value: str
    comment: str | None
    line: int


@dataclass(frozen=True)
class ParseIssue:
    """A problem found by :func:`parse_lenient`, with the offending text."""

    line: int
    reason: str
    text: str


class RpslSyntaxError(ValueError):
    """Raised by :func:`parse` on the first malformed line."""

    def __init__(self, issue: ParseIssue) -> None:
        super().__init__(f"line {issue.line}: {issue.reason}: {issue.text[:80]!r}")
        self.issue = issue


@dataclass(frozen=True)
class RpslObject:
    """One parsed object.

    ``raw`` is the exact input text of the object, from its first line to its last, without
    the blank line that ended it, and ``text[offset : offset + len(raw)] == raw`` holds for the
    text that was parsed. ``comments`` holds the column-0 comment lines as ``(line, text)``.
    """

    cls: str
    attributes: tuple[Attribute, ...]
    source: str
    raw: str
    line: int
    offset: int
    comments: tuple[tuple[int, str], ...] = ()

    def get(self, name: str) -> list[str]:
        """Values of every attribute called ``name``, in order; the name is case insensitive."""
        wanted = name.lower()
        return [a.value for a in self.attributes if a.name.lower() == wanted]

    @property
    def key(self) -> tuple[str, ...] | None:
        """Class key values, lower-cased and in key order, or ``None`` when not known.

        Keys come from the class tables of RFC 2622 sections 3 to 6 and 9, and RFC 4012
        section 3 for route6. A missing or repeated key attribute gives ``None``.
        """
        names = _KEYS.get(self.cls)
        if names is None:
            return None
        values = []
        for name in names:
            found = self.get(name)
            if len(found) != 1:
                return None
            values.append(" ".join(found[0].split()).lower())
        return tuple(values)


class _Collector:
    def __init__(self, strict: bool) -> None:
        self.strict = strict
        self.issues: list[ParseIssue] = []

    def report(self, line: int, reason: str, text: str) -> None:
        """Record an issue; strict mode raises instead."""
        issue = ParseIssue(line, reason, text)
        if self.strict:
            raise RpslSyntaxError(issue)
        self.issues.append(issue)


def _bad_character(text: str) -> str | None:
    for ch in text:
        code = ord(ch)
        if code > 0x7F:
            return "non-ascii character"
        if (code < 0x20 and ch != "\t") or code == 0x7F:
            return "control character"
    return None


def _split_comment(text: str) -> tuple[str, str | None]:
    at = text.find("#")
    if at < 0:
        return text, None
    return text[:at], text[at + 1 :].strip()


class _Builder:
    def __init__(self, line: int, offset: int) -> None:
        self.line = line
        self.offset = offset
        self.end = offset
        self.attributes: list[Attribute] = []
        self.comments: list[tuple[int, str]] = []
        # the attribute being continued
        self.name = ""
        self.name_line = 0
        self.parts: list[str] = []
        self.notes: list[str] = []

    def flush(self) -> None:
        if self.name:
            comment = "\n".join(self.notes) if self.notes else None
            self.attributes.append(
                Attribute(self.name, "\n".join(self.parts), comment, self.name_line)
            )
        self.name = ""
        self.parts = []
        self.notes = []


def _close(current: _Builder | None, objects: list[RpslObject], text: str, source: str) -> None:
    if current is None:
        return
    current.flush()
    if current.attributes:
        objects.append(
            RpslObject(
                cls=current.attributes[0].name.lower(),
                attributes=tuple(current.attributes),
                source=source,
                raw=text[current.offset : current.end],
                line=current.line,
                offset=current.offset,
                comments=tuple(current.comments),
            )
        )


def _scan(text: str, source: str, collector: _Collector) -> list[RpslObject]:
    objects: list[RpslObject] = []
    current: _Builder | None = None
    offset = 0
    for number, line in enumerate(text.split("\n"), start=1):
        start = offset
        offset += len(line) + 1
        logical = line[:-1] if line.endswith("\r") else line

        if not logical.strip(" \t"):
            _close(current, objects, text, source)
            current = None
            continue

        if current is None:
            current = _Builder(number, start)
        current.end = start + len(line)

        if len(logical) > MAX_LINE_LENGTH:
            collector.report(number, f"line longer than {MAX_LINE_LENGTH} characters", logical[:80])
            continue

        why = _bad_character(logical)
        if why is not None:
            collector.report(number, why, logical)

        if logical.startswith("#"):
            current.comments.append((number, logical[1:].strip()))
            continue

        if logical.startswith(_CONTINUATION):
            if not current.name:
                collector.report(number, "continuation line before any attribute", logical)
                continue
            body, note = _split_comment(logical[1:])
            current.parts.append(body.strip())
            if note is not None:
                current.notes.append(note)
            continue

        head, note = _split_comment(logical)
        colon = head.find(":")
        if colon < 0:
            collector.report(number, "line has no colon", logical)
            continue
        name = head[:colon]
        if not _NAME.fullmatch(name):
            collector.report(number, "invalid attribute name", logical)
            continue
        if len(current.attributes) + bool(current.name) >= MAX_ATTRIBUTES:
            collector.report(number, f"more than {MAX_ATTRIBUTES} attributes", logical[:80])
            continue
        current.flush()
        current.name = name
        current.name_line = number
        current.parts = [head[colon + 1 :].strip()]
        if note is not None:
            current.notes.append(note)

    _close(current, objects, text, source)
    return objects


def parse(text: str, source: str) -> list[RpslObject]:
    """Parse RPSL object text, refusing anything malformed (RFC 2622 section 2).

    ``source`` is the name of the registry or file the text came from and is recorded on
    every object. Raises :class:`RpslSyntaxError` at the first malformed line: a line
    without a colon, a bad attribute name, a continuation before any attribute, a control
    character, non-ASCII text, an over-long line or too many attributes. A block that holds
    only comments yields no object.
    """
    return _scan(text, source, _Collector(strict=True))


def parse_lenient(text: str, source: str) -> tuple[list[RpslObject], list[ParseIssue]]:
    """Parse like :func:`parse` but report each problem instead of raising (RFC 2622 section 2).

    Every problem line stays in ``raw`` and is listed in the returned issues. A line that
    could not be read as an attribute or continuation contributes to no attribute; a line
    over ``MAX_LINE_LENGTH`` is skipped the same way. Non-ASCII and control characters are
    reported and the line is still parsed.
    """
    collector = _Collector(strict=False)
    return _scan(text, source, collector), collector.issues
