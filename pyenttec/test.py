"""Tests for offline DMX port."""
from nose.tools import assert_equal, assert_is, assert_raises, raises
from . import DMXConnectionOffline

def test_offline_port():
    univ_size = 24
    port = DMXConnectionOffline(univ_size=univ_size)

    assert_equal(univ_size, len(port.dmx_frame))
    assert all(chan == 0 for chan in port.dmx_frame)

    port.set_channel(0, 1)
    assert_equal(1, port.dmx_frame[0])

    assert_raises(IndexError, port.set_channel, univ_size, 0)

def test_port_item_accessors():
    univ_size = 24
    port = DMXConnectionOffline(univ_size=univ_size)

    for i in range(univ_size):
        port[i] = i
        assert_equal(i, port.dmx_frame[i])
        assert_equal(i, port[i])

def test_port_setitem_max_address():
    univ_size = 24
    port = DMXConnectionOffline(univ_size=univ_size)

    def assert_fail_set_index(i):
        with assert_raises(IndexError):
            port[i] = 0
    # assert_fail_set_index(-1)
    assert_fail_set_index(univ_size)
    assert_fail_set_index(univ_size + 1)

def test_dmx_value_range():
    univ_size = 24
    port = DMXConnectionOffline(univ_size=univ_size)

    assert_raises(ValueError, port.set_channel, 1, -1)

    def set_and_check(chan, val):
        port.set_channel(chan, val)
        assert_equal(val, port[chan])

    set_and_check(0, 0)
    set_and_check(0, 128)
    set_and_check(0, 255)

    assert_raises(ValueError, port.set_channel, 5, 256)

def test_blackout_keeps_array():
    univ_size = 24
    port = DMXConnectionOffline(univ_size=univ_size)

    old_frame = port.dmx_frame
    port.blackout()
    assert_is(port.dmx_frame, old_frame)

