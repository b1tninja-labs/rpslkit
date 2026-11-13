"""rpslkit -- RPSL parsing and IRR queries without a decade old dependency.

IRR is still the origin authority most operators filter on, and Python's only serious tool,
irrtree, last shipped 1.4.0 on 2021-06-24.
"""

from __future__ import annotations

from . import apps, cli, client, compare, objects, parser, ranges, resolve, sets, sources
from .client import query
from .compare import conflicts
from .objects import matches_prefix
from .parser import parse
from .resolve import origins
from .sets import expand

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "apps",
    "cli",
    "client",
    "compare",
    "conflicts",
    "expand",
    "matches_prefix",
    "objects",
    "origins",
    "parse",
    "parser",
    "query",
    "ranges",
    "resolve",
    "sets",
    "sources",
]
