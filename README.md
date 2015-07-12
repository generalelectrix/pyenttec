# pyenttec
Python module for sending DMX using the Enttec Pro (or compatible) DMX port.

In general, this interface attempts to be as pythonic as possible.  Since rendering
DMX is a real-time operation, the interface is lightweight and does not attempt
to massage out of range inputs (such as DMX values greater than 255).  The client
is expected to supply proper values.

On OS X, use is very simple using the select_port function:
```python
from pyenttec import dmx
port = dmx.select_port()
port.dmx_frame[0] = 123
port.render()
```

Support is included for setting various port parameters such as refresh rate
and universe length.  For certain applications (very fast strobe control,
for exmaple) using a truncated universe with refresh_rate = 0 permits faster
control.

This module started as bug fixes to the pySimpleDMX package.
https://github.com/c0z3n/pySimpleDMX

It then mutated into a complete rewrite based on the Objective-C enttec implemention by Coil
https://github.com/coil-lighting
