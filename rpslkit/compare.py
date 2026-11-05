"""IRR against RPKI and against observed routing.

Every object in this module is a placeholder until the milestone named in ROADMAP.md lands. A
stub raises instead of returning a plausible empty value: a protocol library that silently
answers nothing is worse than one that refuses to answer.
"""

from __future__ import annotations

__all__ = [
    "conflicts",
]


def conflicts(irr: list, roas: list, observed: list) -> list:
    """Pending behaviour defined by design.

    Not implemented yet. See the ``compare.conflicts()`` row in ROADMAP.md; this stub
    raises on purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("conflicts() is not implemented: design")
