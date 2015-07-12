from __future__ import print_function

import serial, sys
import os

START_VAL = 0x7E
END_VAL = 0xE7

COM_BAUD = 57600
COM_TIMEOUT = 1
COM_PORT = 7
MIN_DMX_SIZE = 24
MAX_DMX_SIZE = 512

PACKET_END = chr(END_VAL)

def select_port(auto=True, platform='OSX'):
    """List the available Enttec ports, with auto selection options.

    This function currently only supports Mac OS X and may require further
    customization for your system.
    """
    if platform != 'OSX':
        raise EnttecPortOpenError("The select_port function only supports the platform 'OSX'.")
    print("Available enttec ports:")
    ports = []
    n_port = 0
    for item in os.listdir('/dev/'):
        if "tty.usbserial" in item:
            print("{}: {}".format(n_port, item))
            n_port += 1
            ports.append(item)
    # select an enttec:
    if len(ports) == 0:
        raise EnttecPortOpenError("No enttec ports found.")
    elif len(ports) == 1 and auto:
        selection = 0
    else:
        selection = int(raw_input("Select a port by number:"))
    try:
        port_name = ports[selection]
    except IndexError:
        raise EnttecPortOpenError("Invalid port selection.")

    return DMXConnection('/dev/' + port_name)

class PortActions(object):
    """Not the complete set, and GetParameters and ReceiveDMXPacket are unused."""
    GetParameters = 3
    SetParameters = 4
    ReceiveDMXPacket = 5
    SendDMXPacket = 6

def clamp(value, min_val, max_val):
    """Ensure a numeric value falls inside a given range."""
    return max(min_val, min(value, max_val))

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
        packet = [START_VAL,
                  PortActions.SetParameters,
                  length & 0xFF,
                  (length >> 8) & 0xFF]
        packet += payload
        packet.append(END_VAL)
        return ''.join(chr(val) for val in packet)



class DMXConnection(object):
    def __init__(self, com_port = None, univ_size = MAX_DMX_SIZE):
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
        """
        if univ_size > MAX_DMX_SIZE:
            raise EnttecConfigError("Illegal universe size {}; max is {}."
                                    .format(univ_size, MAX_DMX_SIZE))
        if univ_size < MIN_DMX_SIZE:
            raise EnttecConfigError("Illegal universe size {}; min is {}."
                                    .format(univ_size, MIN_DMX_SIZE))

        self._port_params = EnttecProParams()
        self.dmx_frame = [0] * univ_size
        self._com_port = com_port

        try:
            self.com = serial.Serial(com_port, baudrate = COM_BAUD, timeout = COM_TIMEOUT)
        except Exception:
            raise EnttecPortOpenError("Could not open an enttec port at {}".format(com_port))

        self._update_params()

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
        # I believe this corresponds to the DMX break?  Maybe?
        packet_start = [START_VAL,
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

        self.com.write(self._packet_start + ''.join(dmx_payload) + PACKET_END)

    def blackout(self):
        """Zero all DMX values."""
        self.dmx_frame = [0] * len(self.dmx_frame)

    def close(self):
        """Close the port manually."""
        self.com.close()


# --- Error handling ---
class EnttecPortOpenError(Exception):
    pass

class EnttecConfigError(Exception):
    pass