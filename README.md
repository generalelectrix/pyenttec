# pyenttec
Python module for sending DMX using the Enttec Pro (or compatible) DMX port.  Supports Python 2 and 3.

Available on PyPI:
https://pypi.org/project/pyenttec/

On OS X, use is very simple using the select_port function:

    import pyenttec as dmx
    port = dmx.select_port()
    port.dmx_frame[0] = 123
    port.render()

On windows or linux, the select_port function must be modified before use.  Windows uses
numbered com ports, and on linux your serial port directory and port name will
probably be different.  You can also just call the DMXConnection constructor
directly with the right argument.

Support is included for setting various port parameters such as refresh rate
and universe length.  For certain applications (very fast strobe control,
for example) using a truncated universe with refresh_rate = 0 permits faster
control.

This module started as bug fixes to the pySimpleDMX package.
https://github.com/c0z3n/pySimpleDMX

It then mutated into a complete rewrite based on the Objective-C enttec implemention by Coil
https://github.com/coil-lighting
