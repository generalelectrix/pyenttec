"""Tests for offline DMX port."""
from nose.tools import assert_equal, assert_raises, raises
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
    port[univ_size - 1] = 2
    assert_equal(2, port.dmx_frame[univ_size - 1])
    port[0] = 2
    assert_equal(2, port.dmx_frame[0])

@raises(IndexError)
def test_port_setitem_max_address():
    univ_size = 24
    port = DMXConnectionOffline(univ_size=univ_size)
    port[univ_size] = 2

def test_dmx_value_range():
    univ_size = 24
    port = DMXConnectionOffline(univ_size=univ_size)

    assert_raises(OverflowError, port.set_channel, 1, -1)

    def set_and_check(chan, val):
        port.set_channel(chan, val)
        assert_equal(val, port[chan])

    set_and_check(0, 0)
    set_and_check(0, 128)
    set_and_check(0, 255)

    assert_raises(OverflowError, port.set_channel, 5, 256)
