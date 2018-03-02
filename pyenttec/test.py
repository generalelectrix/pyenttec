"""Tests for offline DMX port."""
from nose.tools import assert_equal, assert_raises
from . import DMXConnectionOffline, DMXAddressError, DMXOverflowError

def test_offline_port():
    univ_size = 24
    port = DMXConnectionOffline(univ_size=univ_size)

    assert_equal(univ_size, len(port.dmx_frame))
    assert all(chan == 0 for chan in port.dmx_frame)

    port.set_channel(0, 1)
    assert_equal(1, port.dmx_frame[0])

    assert_raises(DMXAddressError, port.set_channel, univ_size, 0)

    assert_raises(DMXOverflowError, port.set_channel, 1, -1)

    assert_raises(DMXOverflowError, port.set_channel, 5, 256)
