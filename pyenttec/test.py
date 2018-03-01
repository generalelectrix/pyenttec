"""Tests for offline DMX port."""
from nose.tools import assert_equal, assert_raises
from . import DMXConnectionOffline, DMXAddressError

def test_offline_port():
    port = DMXConnectionOffline(univ_size=10)

    assert_equal(10, port.dmx_frame)
    assert all(chan == 0 for chan in port.dmx_frame)

    port.set_channel(0, 1)
    assert_equal(1, port.dmx_frame[0])

    assert_raises(DMXAddressError, port.set_channel, 11, 0)