"""route set and as set expansion with cycles and imports (RFC 2622).

Every object in this module is a placeholder until the milestone named in ROADMAP.md lands. A
stub raises instead of returning a plausible empty value: a protocol library that silently
answers nothing is worse than one that refuses to answer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    Expansion = Any  # placeholder: give it a real type in the milestone that needs it
    Store = Any  # placeholder: give it a real type in the milestone that needs it

__all__ = [
    "expand",
]


def expand(name: str, store: Store, depth: int) -> Expansion:
    """Pending behaviour defined by RFC 2622 section 5.

    Not implemented yet. See the ``sets.expand()`` row in ROADMAP.md; this stub raises on
    purpose so nothing downstream mistakes it for working code.
    """
    raise NotImplementedError("expand() is not implemented: RFC 2622 section 5")
