"""Tests for offline DMX port."""
from nose.tools import assert_equal, assert_raises
from . import DMXConnectionOffline, DMXAddressError, DMXOverflowError

def get_test_port(univ_size=24):
    return DMXConnectionOffline(univ_size=univ_size)

def test_offline_port():
    univ_size = 24
    port = get_test_port(univ_size)

    assert_equal(univ_size, len(port.dmx_frame))
    assert all(chan == 0 for chan in port.dmx_frame)

    port.set_channel(0, 1)
    assert_equal(1, port.dmx_frame[0])
    assert_equal(1, port[0])

    assert_raises(DMXAddressError, port.set_channel, univ_size, 0)
    assert_raises(DMXAddressError, lambda c, v: port[c] = v, univ_size, 0)

def test_dmx_value_range():
    port = get_test_port()

    assert_raises(DMXOverflowError, port.set_channel, 1, -1)

    port.set_channel(0, 0)
    assert_equal(0, port.dmx_frame[0])

    port.set_channel(0, 128)
    assert_equal(128, port.dmx_frame[0])

    port.set_channel(0, 255)
    assert_equal(255, port.dmx_frame[0])

    assert_raises(DMXOverflowError, port.set_channel, 5, 256)
