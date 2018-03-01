from __future__ import print_function

import serial, sys
import os

_START_VAL = 0x7E
_END_VAL = 0xE7

_COM_BAUD = 57600
_COM_TIMEOUT = 1
_MIN_DMX_SIZE = 24
_MAX_DMX_SIZE = 512

_PACKET_END = chr(_END_VAL)

_port_directory = {'darwin': "/dev/",}
_port_basenames = {'darwin': ["tty.usbserial"],}

def _item_is_port(item, platform):
    basenames = _port_basenames[platform]
    for name in basenames:
        if name in item:
            return True
    return False

def available_ports():
    """Get a list of available port names.

    This function currently only supports Mac OS X and may require further
    customization for your system.
    """
    platform = sys.platform
    if platform not in _port_basenames.iterkeys():
        raise EnttecPortOpenError("Unsupported platform '{}'; automatic port "
                                  "selection only supports {}."
                                  .format(platform, _port_basenames.keys()))
    return _available_ports(platform)

def _available_ports(platform):
    return [item for item in os.listdir(_port_directory[platform])
            if _item_is_port(item, platform)]


def select_port(auto=True):
    """List the available Enttec ports, with auto selection option.

    If auto=True (default), port is automatically selected if there is only one
    available.

    This function currently only supports Mac OS X and may require further
    customization for your system.
    """
    platform = sys.platform
    if platform not in _port_basenames.iterkeys():
        raise EnttecPortOpenError("Unsupported platform '{}'; automatic port "
                                  "selection only supports {}."
                                  .format(platform, _port_basenames.keys()))
    print("Available enttec ports:")
    ports = _available_ports(platform)
    for i, port in enumerate(ports):
        print("{}: {}".format(i, port))

    # select an enttec:
    if len(ports) == 0:
        selection = raw_input("No enttec ports found; enter y to use a mock: ")
        if selection == 'y':
            return DMXConnectionOffline('offline port')
        raise EnttecPortOpenError("No enttec ports found.")
    elif len(ports) == 1 and auto:
        selection = 0
    else:
        selection = int(raw_input("Select a port by number:"))
    try:
        port_name = ports[selection]
    except IndexError:
        raise EnttecPortOpenError("Invalid port selection.")

    return DMXConnection(_port_directory[platform] + port_name)

class PortActions(object):
    """Not the complete set, and GetParameters and ReceiveDMXPacket are unused."""
    GetParameters = 3
    SetParameters = 4
    ReceiveDMXPacket = 5
    SendDMXPacket = 6

class EnttecProParams(object):
    """Envelope to hold the state of an enttec port."""
    def __init__(self):
        """New parameters object with defaults."""
        self._user_size_lsb = 0
        self._user_size_msb = 0
        self._break_time = 9
        self._mark_after_break_time = 1
        self.refresh_rate = 40

    def to_packet(self):
        """Format these parameters into a serial packet to send to the port."""
        payload = [self._user_size_lsb,
                   self._user_size_msb,
                   self._break_time,
                   self._mark_after_break_time,
                   self.refresh_rate]
        length = len(payload)
        packet = [_START_VAL,
                  PortActions.SetParameters,
                  length & 0xFF,
                  (length >> 8) & 0xFF]
        packet += payload
        packet.append(_END_VAL)
        return ''.join(chr(val) for val in packet)


class DMXConnection(object):
    def __init__(self, com_port=None, univ_size=_MAX_DMX_SIZE):
        """Initialize a new enttec port.

        Args:
            com_port: On Windows, this is a port number. On *nix, it's the path
                to the serial device.
                For example:
                    DMXConnection(4)              # Windows
                    DMXConnection('/dev/tty2')    # Linux
                    DMXConnection("/dev/ttyUSB0") # Linux
            univ_size (int, default=512): the universe size, by default a full
                512 channels.  The enttec can go faster with truncated universes,
                interesting for special-purpose control such as fast response time
                for strobe control.

        Raises:
            EnttecConfigError if the universe size is out of bounds.
            EnttecPortOpenError if there was an error opening the port.
        """
        if univ_size > _MAX_DMX_SIZE:
            raise EnttecConfigError("Illegal universe size {}; max is {}."
                                    .format(univ_size, _MAX_DMX_SIZE))
        if univ_size < _MIN_DMX_SIZE:
            raise EnttecConfigError("Illegal universe size {}; min is {}."
                                    .format(univ_size, _MIN_DMX_SIZE))

        self._port_params = EnttecProParams()
        self.dmx_frame = [0] * univ_size
        self._com_port = com_port

        self.com = None
        self._open_port()

        self._update_params()

    def _open_port(self):
        try:
            self.com = serial.Serial(
                self._com_port, baudrate=_COM_BAUD, timeout=_COM_TIMEOUT)
        except Exception:
            raise EnttecPortOpenError(
                "Could not open an enttec port at {}".format(self._com_port))

    def __str__(self):
        return "DMXConnection on port '{}'".format(self._com_port)

    def __repr__(self):
        return str(self)

    def set_refresh_rate(self, refresh_rate):
        """Set the port refresh rate in fps.

        refresh_rate is an int in the range [0,40].  The value 0 commands the port
        to send packets as fast as it can.
        """
        if refresh_rate < 0 or refresh_rate > 40:
            raise EnttecConfigError("Illegal framerate {}; must be in [0, 40]."
                                    .format(refresh_rate))
        self._port_params.refresh_rate = refresh_rate
        self._write_settings()

    def _update_params(self):
        """Recompute all of the port parameters and update the port settings."""
        univ_size = len(self.dmx_frame)

        # need to add a pad byte to the serial packet before the DMX payload
        packet_start = [_START_VAL,
                        PortActions.SendDMXPacket,
                        (univ_size + 1) & 0xFF,
                        ( (univ_size + 1) >> 8) & 0xFF,
                        0]
        self._packet_start = ''.join(chr(v) for v in packet_start)

        self._write_settings()

    def _write_settings(self):
        """Write the current settings to the port."""
        self.com.write(self._port_params.to_packet())

    def render(self):
        """Write the current DMX frame to the port."""

        dmx_payload = (chr(v) for v in self.dmx_frame)

        self.com.write(self._packet_start + ''.join(dmx_payload) + _PACKET_END)

    def set_channel(self, chan, val):
        """Set the value of a DMX channel, indexed from 0.

        Raises DMXAddressError for out of bounds address.
        """
        try:
            self.dmx_frame[chan] = val
        except IndexError:
            raise DMXAddressError("Channel index {} out of range. "
                                  "Universe size is {}."
                                  .format(chan, len(self.dmx_frame)))

    def blackout(self):
        """Zero all DMX values."""
        self.dmx_frame = [0] * len(self.dmx_frame)

    def close(self):
        """Close the port manually."""
        self.com.close()


class DMXConnectionOffline(DMXConnection):
    """Placeholder mock for when a real port is not available."""
    def _open_port(self):
        pass

    def _update_params(self):
        """Recompute all of the port parameters and update the port settings."""
        univ_size = len(self.dmx_frame)

        # need to add a pad byte to the serial packet before the DMX payload
        packet_start = [_START_VAL,
                        PortActions.SendDMXPacket,
                        (univ_size + 1) & 0xFF,
                        ( (univ_size + 1) >> 8) & 0xFF,
                        0]
        self._packet_start = ''.join(chr(v) for v in packet_start)

        self._write_settings()

    def _write_settings(self):
        pass

    def render(self):
        pass

    def close(self):
        pass


# --- Error handling ---
class EnttecPortOpenError(Exception):
    pass

class EnttecConfigError(Exception):
    pass

class DMXAddressError(Exception):
    pass