"""The RPSL object parser against RFC 2622 section 2.

Vectors: the route objects are RFC 2622 section 4 Figure 8 and the person object is section 3.2
Figure 4, both copied from rfclib on 2026-11-13. The continuation, comment and blank-line
cases are built from the rules of section 2 paragraphs 25 and 26; the RFC has no byte-exact
example for them.
"""

from __future__ import annotations

import time

import pytest

from rpslkit.parser import (
    MAX_LINE_LENGTH,
    RpslSyntaxError,
    parse,
    parse_lenient,
)

ROUTES = """\
route: 128.9.0.0/16
origin: AS226

route: 128.99.0.0/16
origin: AS226

route: 128.8.0.0/16
origin: AS1

route: 128.8.0.0/16
origin: AS2
"""

PERSON = """\
person:      Daniel Karrenberg
address:     RIPE Network Coordination Centre (NCC)
address:     Singel 258
address:     NL-1016 AB  Amsterdam
address:     Netherlands
phone:       +31 20 535 4444
fax-no:      +31 20 535 4445
e-mail:      Daniel.Karrenberg@ripe.net
nic-hdl:     DK58
changed:     Daniel.Karrenberg@ripe.net 19970616
source:      RIPE
"""


def test_parse_route_objects_from_rfc_section_4_figure_8():
    objects = parse(ROUTES, "RFC2622")
    assert [o.cls for o in objects] == ["route"] * 4
    assert [o.key for o in objects] == [
        ("128.9.0.0/16", "as226"),
        ("128.99.0.0/16", "as226"),
        ("128.8.0.0/16", "as1"),
        ("128.8.0.0/16", "as2"),
    ]
    # section 4: same prefix, different origin, different objects
    assert objects[2].key != objects[3].key


def test_parse_person_object_from_rfc_section_3_2_figure_4():
    (obj,) = parse(PERSON, "RIPE")
    assert obj.cls == "person"
    assert obj.get("address") == [
        "RIPE Network Coordination Centre (NCC)",
        "Singel 258",
        "NL-1016 AB  Amsterdam",
        "Netherlands",
    ]
    assert obj.key == ("dk58",)
    assert obj.attributes[0].line == 1


def test_continuation_space_tab_plus():
    text = "as-set: AS-FOO\nmembers: AS1,\n    AS2,\n\tAS3,\n+   AS4\n"
    (obj,) = parse(text, "T")
    assert obj.get("members") == ["AS1,\nAS2,\nAS3,\nAS4"]
    assert len(obj.attributes) == 2


def test_plus_continuation_allows_blank_value_line():
    text = "remarks: first\n+\n+ third\nsource: T\n"
    (obj,) = parse(text, "T")
    assert obj.get("remarks") == ["first\n\nthird"]
    assert obj.get("source") == ["T"]


def test_empty_line_not_a_plus_line_ends_the_object():
    # the line after the blank has no attribute before it: that is a new block, and invalid.
    with pytest.raises(RpslSyntaxError, match="before any attribute"):
        parse("remarks: first\n\n second\n", "T")
    objects, issues = parse_lenient("remarks: first\n\n second\n", "T")
    assert len(objects) == 1
    assert issues[0].reason == "continuation line before any attribute"


def test_comments_inline_continuation_and_full_line():
    text = "# leading note\nroute: 10.0.0.0/8 # inline\norigin: AS1 # one\n  # two\n"
    (obj,) = parse(text, "T")
    assert obj.cls == "route"
    assert obj.attributes[0].comment == "inline"
    assert obj.attributes[0].value == "10.0.0.0/8"
    assert obj.attributes[1].value == "AS1\n"
    assert obj.attributes[1].comment == "one\ntwo"
    assert obj.comments == ((1, "leading note"),)
    assert obj.raw == text.rstrip("\n")


def test_hash_is_a_comment_start_even_before_a_colon():
    with pytest.raises(RpslSyntaxError, match="no colon"):
        parse("route # not: an attribute\n", "T")


def test_blank_lines_separate_objects_and_extra_blank_lines_are_fine():
    objects = parse(
        "\n\nroute: 1.0.0.0/8\norigin: AS1\n\n\n\n \t \nroute: 2.0.0.0/8\norigin: AS2\n\n\n", "T"
    )
    assert [o.get("route") for o in objects] == [["1.0.0.0/8"], ["2.0.0.0/8"]]


def test_comment_only_block_yields_no_object():
    assert (
        parse("# just a note\n# and another\n\nroute: 1.0.0.0/8\norigin: AS1\n", "T")[0].cls
        == "route"
    )
    assert parse("# only a note\n", "T") == []


def test_attribute_order_preserved_and_duplicates_kept():
    (obj,) = parse("mntner: M\nremarks: b\nremarks: a\nremarks: b\nsource: S\n", "T")
    assert [a.name for a in obj.attributes] == ["mntner", "remarks", "remarks", "remarks", "source"]
    assert obj.get("remarks") == ["b", "a", "b"]


def test_attribute_names_case_insensitive_lookup_but_original_case_kept():
    (obj,) = parse("Route: 1.0.0.0/8\nORIGIN: AS1\n", "T")
    assert obj.cls == "route"
    assert [a.name for a in obj.attributes] == ["Route", "ORIGIN"]
    assert obj.get("origin") == ["AS1"]
    assert obj.get("OrIgIn") == ["AS1"]
    assert obj.key == ("1.0.0.0/8", "as1")


def test_key_is_none_for_unknown_class_missing_or_repeated_key():
    assert parse("widget: x\n", "T")[0].key is None
    assert parse("route: 1.0.0.0/8\n", "T")[0].key is None
    assert parse("route: 1.0.0.0/8\norigin: AS1\norigin: AS2\n", "T")[0].key is None


def test_source_recorded_on_every_object():
    assert {o.source for o in parse(ROUTES, "RADB")} == {"RADB"}


def test_raw_is_the_exact_input_slice_and_not_rebuilt():
    text = "# c\nroute:    10.0.0.0/8   # odd   spacing\n  \norigin:AS1\r\n\r\nroute: 11.0.0.0/8\n"
    objects = parse(text, "T")
    assert len(objects) == 3
    for obj in objects:
        assert text[obj.offset : obj.offset + len(obj.raw)] == obj.raw
    assert objects[0].raw == "# c\nroute:    10.0.0.0/8   # odd   spacing"
    assert objects[1].raw == "origin:AS1\r"
    assert objects[0].line == 1


def test_crlf_input_is_normalised_in_values_but_preserved_in_raw():
    text = "route: 10.0.0.0/8\r\norigin: AS1\r\n\r\nroute: 11.0.0.0/8\r\norigin: AS2\r\n"
    objects = parse(text, "T")
    assert [o.get("origin") for o in objects] == [["AS1"], ["AS2"]]
    assert objects[0].raw == "route: 10.0.0.0/8\r\norigin: AS1\r"
    assert text[objects[1].offset : objects[1].offset + len(objects[1].raw)] == objects[1].raw


def test_no_colon_line_is_syntax_error_strict_and_issue_lenient():
    text = "route: 10.0.0.0/8\ngarbage\norigin: AS1\n"
    with pytest.raises(RpslSyntaxError, match="no colon") as caught:
        parse(text, "T")
    assert caught.value.issue.line == 2
    objects, issues = parse_lenient(text, "T")
    assert [(i.line, i.reason, i.text) for i in issues] == [(2, "line has no colon", "garbage")]
    assert [a.name for a in objects[0].attributes] == ["route", "origin"]
    assert objects[0].raw == text.rstrip("\n")


def test_invalid_attribute_name_is_reported():
    with pytest.raises(RpslSyntaxError, match="invalid attribute name"):
        parse("rou te: x\n", "T")
    with pytest.raises(RpslSyntaxError, match="invalid attribute name"):
        parse(": x\n", "T")
    with pytest.raises(RpslSyntaxError, match="invalid attribute name"):
        parse("1route: x\n", "T")


def test_continuation_line_before_any_attribute():
    with pytest.raises(RpslSyntaxError, match="before any attribute"):
        parse("  orphan\n", "T")
    with pytest.raises(RpslSyntaxError, match="before any attribute"):
        parse("+orphan\n", "T")
    objects, issues = parse_lenient("+orphan\nroute: 1.0.0.0/8\n", "T")
    assert [i.line for i in issues] == [1]
    assert objects[0].get("route") == ["1.0.0.0/8"]


@pytest.mark.parametrize("bad", ["\x00", "\x07", "\x1b", "\x7f", "\r"])
def test_nul_and_control_characters_rejected(bad):
    text = f"remarks: a{bad}b\n"
    with pytest.raises(RpslSyntaxError, match="control character"):
        parse(text, "T")
    objects, issues = parse_lenient(text, "T")
    assert issues[0].reason == "control character"
    assert objects[0].get("remarks") == [f"a{bad}b".strip(" \t")]


def test_non_ascii_in_value_strict_refuses_lenient_keeps_with_issue():
    text = "remarks: café\n"
    with pytest.raises(RpslSyntaxError, match="non-ascii"):
        parse(text, "T")
    objects, issues = parse_lenient(text, "T")
    assert issues[0].reason == "non-ascii character"
    assert objects[0].get("remarks") == ["café"]


def test_very_long_line_is_bounded():
    long = "remarks: " + "x" * (MAX_LINE_LENGTH + 1)
    with pytest.raises(RpslSyntaxError, match="longer than"):
        parse(long + "\n", "T")
    objects, issues = parse_lenient("route: 1.0.0.0/8\n" + long + "\norigin: AS1\n", "T")
    assert len(issues) == 1
    assert [a.name for a in objects[0].attributes] == ["route", "origin"]
    assert len(issues[0].text) <= 80


def test_many_attributes_and_continuations_are_linear_time():
    many = "route: 1.0.0.0/8\n" + "remarks: x\n" * 99_000
    start = time.perf_counter()
    (obj,) = parse(many, "T")
    assert len(obj.attributes) == 99_001
    cont = "as-set: AS-X\nmembers: AS1\n" + "  , AS2 # c\n" * 200_000
    (big,) = parse(cont, "T")
    assert big.get("members")[0].count("\n") == 200_000
    assert time.perf_counter() - start < 10.0


def test_attribute_count_cap():
    text = "a: 1\n" + "b: 2\n" * 100_000
    with pytest.raises(RpslSyntaxError, match="attributes"):
        parse(text, "T")


def test_hostile_continuations_do_not_backtrack():
    text = "remarks: x\n" + (" " * 50_000 + "#" + "\n") * 2 + "+" * 60_000 + "\n"
    start = time.perf_counter()
    (obj,) = parse(text, "T")
    assert obj.cls == "remarks"
    assert time.perf_counter() - start < 2.0


@pytest.mark.parametrize("text", ["", "\n", "\n\n\n", "  \n\t\n", "\r\n\r\n"])
def test_empty_and_whitespace_only_input_returns_empty_list(text):
    assert parse(text, "T") == []
    assert parse_lenient(text, "T") == ([], [])


def test_unterminated_last_object_without_trailing_newline():
    (obj,) = parse("route: 1.0.0.0/8\norigin: AS1", "T")
    assert obj.get("origin") == ["AS1"]
    assert obj.raw == "route: 1.0.0.0/8\norigin: AS1"
