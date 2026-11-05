"""lenient line parsing that preserves source and comments (RFC 2622).

Every object in this module is a placeholder until the milestone named in ROADMAP.md lands. A
stub raises instead of returning a plausible empty value: a protocol library that silently
answers nothing is worse than one that refuses to answer.
"""

from __future__ import annotations

__all__ = [
    "parse",
]


def parse(text: str, source: str) -> list:
    """Pending behaviour defined by RFC 2622.

    Not implemented yet. See the ``parser.parse()`` row in ROADMAP.md; this stub raises
    on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("parse() is not implemented: RFC 2622")
