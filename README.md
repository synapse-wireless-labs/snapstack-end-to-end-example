# SNAPstack End-to-End Example: LED Control

In this example we have an application which provides an HTTP API for
controlling the RGB LED on an SN220.

# Getting Started

To run `server.py` and `client.py` you'll need a Python environment with `SNAPstack` and `tornado` installed.

You'll need [SNAPtoolbelt](https://developer.synapse-wireless.com/snaptoolbelt/index.html) (to load scripts) and [SNAPcompiler](https://developer.synapse-wireless.com/snapcompiler/index.html) (to build scripts).

## server.py

This script is the SNAPstack+Tornado application.

Usage: `python server.py path-to-SNAP-bridge-node`

e.g. `python server.py /dev/snap1`

## client.py

This script uses the Tornado HTTPClient to talk to the server's API.

Usage: `python client.py`

## node.py / node.spy

This is the SNAPpy script to load on your SN220.

To build `node.spy`: `spyc node.py`

To load `node.spy` on your bridge node: `toolbelt node bridge script load node.spy`

# Design

## SNAP API

On and off for the RGB LED elements are encoded as the low 3 bits of a single int: 0b0rgb.

0b0100 (4) is "red on", 0b0010 (2) is "green on", 0b0001 (1) is "blue
on".  These values are bitwire OR'd together to get the combined value.

```
get_rgb() -> rgb:
set_rgb(rgb):
```

## HTTP API

This API represents RGB LED state as a JSON object: `{"r":1,"g":0,"b":1}`

The `snap_address` can be a 6-character SNAP MAC address or `bridge`, to use the bridge node.

GET /(snap_address)/rgb: Request state of RGB LEDs

POST /(snap_address)bridge/rgb: Set RGB LEDs to the given LED state
