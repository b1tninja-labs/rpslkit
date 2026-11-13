"""Address prefix ranges and the range operators (RFC 2622 section 2, RFC 4012 section 2.4).

A range is a prefix plus a length interval: ``p/l^n-m`` stands for every more specific of
``p/l`` whose length lies in ``n..m``. Nothing here enumerates addresses; membership is two
comparisons and a subnet test.

The operators, from RFC 2622 section 2 (read in full):

* ``^-`` the more specifics without the prefix itself, ``prefix/l^(l+1)-max``;
* ``^+`` the more specifics with the prefix, ``prefix/l^l-max``;
* ``^n`` all more specifics of length ``n``, equal to ``^n-n``;
* ``^n-m`` the more specifics of length ``n`` to ``m``.

An operator may not follow another operator on one prefix (``30.0.0.0/8^24-28^+`` is an
error), but it may be applied to a set of ranges; :func:`apply_operator` does that and
follows the RFC's rule: the outer ``^n-m`` over an inner ``^k-l`` becomes ``^max(n,k)-m``,
or the member is deleted when ``m < max(n,k)``; the outer ``^+`` keeps the inner lower bound
and raises the upper bound to the maximum, and the outer ``^-`` raises the lower bound by one.

RFC 4012 section 2.4 says the IPv6 range operator is the one of RFC 2622 section 2 and does
not state the maximum length. This module takes the maximum as 128 for IPv6, the only value
that makes ``^+`` and ``^-`` mean the same thing as they do for IPv4 (an inference, recorded
in ROADMAP.md).

Policy beyond the RFC: a prefix with host bits set, leading zeros, white space, non-ASCII
digits or an IPv6 zone is refused, and so is a range that selects nothing (``n`` below the
prefix length, ``n > m``, ``^-`` on a host route).
"""

from __future__ import annotations

import ipaddress
from collections.abc import Iterable
from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network

__all__ = [
    "Operator",
    "PrefixRange",
    "apply_operator",
    "contains",
    "parse_operator",
    "parse_prefix",
    "parse_prefix_range",
]

_DIGITS = frozenset("0123456789")


@dataclass(frozen=True)
class PrefixRange:
    """Every more specific of ``network`` whose length is in ``low..high`` (inclusive)."""

    network: IPv4Network | IPv6Network
    low: int
    high: int

    @property
    def max_length(self) -> int:
        return self.network.max_prefixlen


@dataclass(frozen=True)
class Operator:
    """A range operator. ``kind`` is ``"-"``, ``"+"`` or ``"range"``; ``n`` and ``m`` are used by ``"range"``."""

    kind: str
    n: int = 0
    m: int = 0


def _number(text: str, what: str) -> int:
    if not text or not set(text) <= _DIGITS or (len(text) > 1 and text[0] == "0"):
        raise ValueError(f"{what} is not a plain ASCII decimal number: {text!r}")
    return int(text)


def parse_prefix(text: str) -> IPv4Network | IPv6Network:
    """Parse one address prefix, IPv4 (RFC 2622 section 2) or IPv6 (RFC 4012 section 2.4).

    Raises ``ValueError`` for ``0/0``, ``128.9/16``, host bits set, a length out of range,
    leading zeros, white space, non-ASCII digits and IPv6 zones.
    """
    address, slash, length_text = text.partition("/")
    if not slash or not address:
        raise ValueError(f"not an address prefix: {text!r}")
    if not text.isascii() or "%" in text or any(c.isspace() for c in text):
        raise ValueError(f"not an address prefix: {text!r}")
    length = _number(length_text, "prefix length") if length_text != "0" else 0
    if ":" in address:
        network: IPv4Network | IPv6Network
        try:
            network = IPv6Network(f"{ipaddress.IPv6Address(address)}/{length}", strict=True)
        except ValueError as error:
            raise ValueError(f"not an IPv6 prefix: {text!r}") from error
        return network
    parts = address.split(".")
    if len(parts) != 4:
        raise ValueError(f"an IPv4 address is four integers separated by dots: {text!r}")
    octets = [_number(part, "octet") if part != "0" else 0 for part in parts]
    if any(octet > 255 for octet in octets):
        raise ValueError(f"octet above 255: {text!r}")
    try:
        return IPv4Network(f"{'.'.join(map(str, octets))}/{length}", strict=True)
    except ValueError as error:
        raise ValueError(f"not an IPv4 prefix: {text!r}") from error


def parse_operator(text: str) -> Operator:
    """Parse ``^-``, ``^+``, ``^n`` or ``^n-m``. Another ``^`` inside is an error (RFC 2622 section 2)."""
    if not text.startswith("^"):
        raise ValueError(f"a range operator starts with '^': {text!r}")
    body = text[1:]
    if "^" in body:
        raise ValueError(f"a range operator cannot follow another operator: {text!r}")
    if body == "-":
        return Operator("-")
    if body == "+":
        return Operator("+")
    low, dash, high = body.partition("-")
    n = _number(low, "range bound")
    m = _number(high, "range bound") if dash else n
    return Operator("range", n, m)


def parse_prefix_range(text: str) -> PrefixRange:
    """Parse ``prefix``, ``prefix^-``, ``prefix^+``, ``prefix^n`` or ``prefix^n-m`` (RFC 2622 section 2).

    A bare prefix is the range of that length alone. Raises ``ValueError`` for a second
    operator, an invalid prefix, ``n > m``, a bound above the maximum length, and any range
    that selects nothing.
    """
    prefix_text, caret, rest = text.partition("^")
    network = parse_prefix(prefix_text)
    length = network.prefixlen
    base = PrefixRange(network, length, length)
    if not caret:
        return base
    operator = parse_operator("^" + rest)
    if operator.kind == "range":
        if operator.n > operator.m:
            raise ValueError(f"range lower bound above upper bound: {text!r}")
        if operator.m > network.max_prefixlen:
            raise ValueError(f"range bound above {network.max_prefixlen}: {text!r}")
        if operator.n < length:
            raise ValueError(f"range starts below the prefix length {length}: {text!r}")
    applied = _apply(base, operator)
    if applied is None:
        raise ValueError(f"range selects nothing: {text!r}")
    return applied


def _apply(item: PrefixRange, operator: Operator) -> PrefixRange | None:
    ceiling = item.max_length
    if operator.kind == "+":
        low, high = item.low, ceiling
    elif operator.kind == "-":
        low, high = item.low + 1, ceiling
    else:
        low, high = max(operator.n, item.low), operator.m
    if low > high or high > ceiling:
        return None
    return PrefixRange(item.network, low, high)


def apply_operator(ranges: Iterable[PrefixRange], operator: str) -> list[PrefixRange]:
    """Apply an outer range operator to a set of ranges, member by member (RFC 2622 section 2).

    Members the operator deletes are left out, so the result can be empty: the RFC's
    ``{128.9.0.0/16^20-24}^18-19 == {}``. Order is kept. A bad operator raises ``ValueError``
    before any member is processed.
    """
    parsed = parse_operator(operator)
    result = []
    for item in ranges:
        applied = _apply(item, parsed)
        if applied is not None:
            result.append(applied)
    return result


def contains(item: PrefixRange, prefix: IPv4Network | IPv6Network | str) -> bool:
    """True when ``prefix`` is a member of the range. A prefix of the other family never is."""
    network = parse_prefix(prefix) if isinstance(prefix, str) else prefix
    if network.version != item.network.version:
        return False
    if not item.low <= network.prefixlen <= item.high:
        return False
    return network.subnet_of(item.network)  # type: ignore[arg-type]
