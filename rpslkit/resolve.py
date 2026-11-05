"""origin resolution for a prefix with ambiguity preserved.

Every object in this module is a placeholder until the milestone named in ROADMAP.md lands. A
stub raises instead of returning a plausible empty value: a protocol library that silently
answers nothing is worse than one that refuses to answer.
"""

from __future__ import annotations

__all__ = [
    "origins",
]


async def origins(prefix: str, sources: list) -> list:
    """Pending behaviour defined by RFC 2622.

    Not implemented yet. See the ``resolve.origins()`` row in ROADMAP.md; this stub
    raises on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("origins() is not implemented: RFC 2622")
