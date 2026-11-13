"""Prefix ranges and operators against the table RFC 2622 section 2 publishes.

Vectors: every equivalence and example below is quoted from RFC 2622 section 2 (paragraphs 8 to
16, read through rfclib on 2026-11-13). Equality is checked twice, on the canonical
(network, low, high) triple and by sampling membership at every prefix length.
"""

from __future__ import annotations

import ipaddress
import time

import pytest

from rpslkit.ranges import (
    PrefixRange,
    apply_operator,
    contains,
    parse_operator,
    parse_prefix,
    parse_prefix_range,
)

BAD = "not an|octet|plain ASCII|four integers|starts with"


def members(item: PrefixRange) -> set[tuple[int, int]]:
    """Membership probe: at every length, the truncations of a few addresses."""
    found = set()
    for probe in ("128.9.7.9", "128.10.0.0", "128.9.0.0"):
        for length in range(33):
            net = ipaddress.IPv4Network(f"{probe}/{length}", strict=False)
            if contains(item, net):
                found.add((int(net.network_address), length))
    return found


def same(left: list[PrefixRange], right: list[PrefixRange]) -> None:
    if left != right:
        pytest.fail(f"{left} != {right}")
    assert [members(x) for x in left] == [members(x) for x in right]


def pr(text: str) -> PrefixRange:
    return parse_prefix_range(text)


# RFC 2622 section 2 paragraph 16, one case per published line.
EQUIVALENCES = [
    ("128.9.0.0/16^+", "^-", "128.9.0.0/16^-"),
    ("128.9.0.0/16^-", "^+", "128.9.0.0/16^-"),
    ("128.9.0.0/16^17", "^24", "128.9.0.0/16^24"),
    ("128.9.0.0/16^20-24", "^26-28", "128.9.0.0/16^26-28"),
    ("128.9.0.0/16^20-24", "^22-28", "128.9.0.0/16^22-28"),
    ("128.9.0.0/16^20-24", "^18-28", "128.9.0.0/16^20-28"),
    ("128.9.0.0/16^20-24", "^18-22", "128.9.0.0/16^20-22"),
]


@pytest.mark.parametrize(("inner", "outer", "expected"), EQUIVALENCES)
def test_published_set_equivalence(inner, outer, expected):
    same(apply_operator([pr(inner)], outer), [pr(expected)])


def test_published_equivalence_with_empty_result():
    # {128.9.0.0/16^20-24}^18-19 == {}
    assert apply_operator([pr("128.9.0.0/16^20-24")], "^18-19") == []


def test_outer_operator_empty_result_drops_prefix():
    survivor = pr("10.0.0.0/8^8-30")
    kept = apply_operator([pr("128.9.0.0/16^20-24"), survivor], "^18-19")
    assert kept == [PrefixRange(survivor.network, 18, 19)]


def test_n_equals_n_dash_n():
    assert pr("30.0.0.0/8^16") == pr("30.0.0.0/8^16-16")


def test_plus_is_l_to_max_and_minus_is_l_plus_one_to_max():
    net = ipaddress.IPv4Network("10.0.0.0/8")
    assert pr("10.0.0.0/8^+") == PrefixRange(net, 8, 32)
    assert pr("10.0.0.0/8^-") == PrefixRange(net, 9, 32)


def test_set_plus_and_minus_equivalences():
    # {prefix/l^n-m}^+ == {prefix/l^n-32}; {prefix/l^n-m}^- == {prefix/l^(n+1)-32}
    inner = pr("128.9.0.0/16^20-24")
    assert apply_operator([inner], "^+") == [PrefixRange(inner.network, 20, 32)]
    assert apply_operator([inner], "^-") == [PrefixRange(inner.network, 21, 32)]


def test_published_member_examples():
    assert contains(pr("128.9.0.0/16^-"), "128.9.1.0/24")
    assert not contains(pr("128.9.0.0/16^-"), "128.9.0.0/16")
    assert contains(pr("5.0.0.0/8^+"), "5.0.0.0/8")
    assert contains(pr("5.0.0.0/8^+"), "5.1.2.0/24")
    assert contains(pr("30.0.0.0/8^16"), "30.9.0.0/16")
    assert not contains(pr("30.0.0.0/8^16"), "30.9.0.0/17")
    assert contains(pr("30.0.0.0/8^24-32"), "30.9.9.96/28")
    assert not contains(pr("30.0.0.0/8^24-32"), "30.9.0.0/16")


def test_member_must_lie_inside_the_network():
    assert not contains(pr("128.9.0.0/16^+"), "128.10.0.0/16")
    assert not contains(pr("128.9.0.0/16^+"), "128.0.0.0/8")


def test_operator_on_operator_is_error():
    with pytest.raises(ValueError, match="another operator"):
        pr("30.0.0.0/8^24-28^+")
    with pytest.raises(ValueError, match="another operator"):
        parse_operator("^24^+")


@pytest.mark.parametrize(
    "text",
    [
        "0/0",
        "128.9/16",
        "128.9.0.0/33",
        "128.9.0.1/16",
        "128.9.0.0/016",
        "128.009.0.0/16",
        "256.9.0.0/16",
        " 128.9.0.0/16",
        "128.9.0.0/16 ",
        "128.9.0.0",
        "128.9.0.0/",
        "/16",
        "128.9.0.0/-1",
        "2001:db8::/129",
        "2001:db8::1/32",
        "fe80::/10%eth0",
    ],
)
def test_invalid_prefix_forms_rejected(text):
    with pytest.raises(ValueError, match=BAD):
        parse_prefix(text)


def test_valid_prefixes_from_the_rfc():
    # RFC 2622 section 2 paragraph 8: 128.9.128.5/32, 128.9.0.0/16, 0.0.0.0/0
    assert str(parse_prefix("128.9.128.5/32")) == "128.9.128.5/32"
    assert str(parse_prefix("128.9.0.0/16")) == "128.9.0.0/16"
    assert str(parse_prefix("0.0.0.0/0")) == "0.0.0.0/0"


def test_n_greater_than_m_rejected():
    with pytest.raises(ValueError, match="above upper"):
        pr("128.9.0.0/16^24-20")


def test_range_below_prefix_length_rejected():
    with pytest.raises(ValueError, match="below the prefix length"):
        pr("128.9.0.0/16^8-12")


def test_range_above_maximum_length_rejected():
    with pytest.raises(ValueError, match="above 32"):
        pr("128.9.0.0/16^20-33")


def test_minus_on_host_route_selects_nothing_and_is_rejected():
    with pytest.raises(ValueError, match="selects nothing"):
        pr("128.9.0.1/32^-")


def test_huge_range_membership_is_constant_time():
    wide = pr("0.0.0.0/0^+")
    start = time.perf_counter()
    for _ in range(2000):
        assert contains(wide, "203.0.113.0/24")
    assert time.perf_counter() - start < 2.0
    assert contains(pr("::/0^+"), "2001:db8::/32")


@pytest.mark.parametrize("digit", [chr(0x663), chr(0xFF11), chr(0x661)])
def test_non_ascii_digits_rejected(digit):
    with pytest.raises(ValueError, match=BAD):
        parse_prefix(f"128.9.0.0/{digit}6")
    with pytest.raises(ValueError, match=BAD):
        parse_prefix(f"{digit}28.9.0.0/16")
    with pytest.raises(ValueError, match=BAD):
        parse_operator(f"^2{digit}")


def test_ipv4_range_applied_to_ipv6_prefix_never_matches():
    assert not contains(pr("0.0.0.0/0^+"), "::/0")
    assert not contains(pr("::/0^+"), "0.0.0.0/0")


def test_ipv6_ranges_follow_the_same_operators_with_maximum_128():
    # Maximum 128 is an inference from RFC 4012 section 2.4 (see the ranges module docstring).
    net = ipaddress.IPv6Network("2001:db8::/32")
    assert pr("2001:db8::/32^+") == PrefixRange(net, 32, 128)
    assert pr("2001:db8::/32^-") == PrefixRange(net, 33, 128)
    assert pr("2001:db8::/32^48") == PrefixRange(net, 48, 48)
    assert contains(pr("2001:db8::/32^48-64"), "2001:db8:1::/48")
    assert not contains(pr("2001:db8::/32^48-64"), "2001:db8:2::/47")
    with pytest.raises(ValueError, match="above 128"):
        pr("2001:db8::/32^48-129")


def test_bad_operator_raises_before_any_member_is_processed():
    with pytest.raises(ValueError, match=BAD):
        apply_operator([pr("10.0.0.0/8")], "24")
