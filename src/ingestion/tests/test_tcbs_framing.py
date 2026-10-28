"""TCBS wire protocol — pure functions, fully testable without any network."""

from ingestion.feeds.tcbs import framing as F


def test_splits_multiple_frames_in_one_message():
    # A production audit found 1 frame per message, but that is an observation,
    # not a guarantee -> the splitter must stay correct if TCBS changes its mind.
    assert F.split_frames('s|1|{"a":1}s|6|{"b":2}') == ['s|1|{"a":1}', 's|6|{"b":2}']


def test_pretty_printed_json_does_not_break_framing():
    raw = 's|6|{\n  "symbol": "TCB"\n}'
    assert F.split_frames(raw) == [raw]


def test_parse_thesis_frame():
    f = F.parse_thesis_frame('s|42|{"symbol":"41I1G8000","top":1}')
    assert f.wire_code == "42"
    assert '"top":1' in f.json_body


def test_ouranos_takes_symbol_from_envelope_not_payload():
    f = F.parse_ouranos_frame('C002S60|VIC|{"symbol":"VIC"}')
    assert (f.code, f.symbol) == ("C002S60", "VIC")


def test_ouranos_ignores_control_frames():
    assert F.parse_ouranos_frame("d|pi") is None
    assert F.parse_ouranos_frame("d|33|30") is None


def test_key_prefers_symbol():
    assert F.extract_key('{"symbol":"TCB","indexId":"X"}') == "TCB"


def test_index_key_falls_back_to_index_number():
    # s|8 only carries indexNumber as a NUMBER. examples/ lacked this branch so
    # the key was always NULL -> every index landed on an arbitrary partition,
    # destroying ordering.
    assert F.extract_key('{"indexNumber":5,"index":91.43}') == "5"


def test_key_is_none_when_nothing_matches():
    assert F.extract_key('{"foo":1}') is None


def test_reads_real_timeout_announced_by_server():
    # The docs say ouranos is 15s; live probing observed 30s -> read it from the frame.
    assert F.parse_config_timeout("d|33|30") == 30.0
    assert F.parse_config_timeout("s|6|{}") is None
