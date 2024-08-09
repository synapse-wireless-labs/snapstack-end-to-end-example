"""
(c) Copyright 2023 Synapse Wireless, Inc.

Example script for use w/ SN220

Allows RPC control of the RGB LED
"""

# LED GPIO constants based on SN220 (paddleboard swaps red and blue)
RED_LED_PIN = 5
GREEN_LED_PIN = 6
BLUE_LED_PIN = 7

G_RED_LED_ON = 0
G_GREEN_LED_ON = 0
G_BLUE_LED_ON = 0


@setHook(HOOK_STARTUP)
def init():
    """On startup, configure our LED-controlling pins"""
    # Output = PinDir True
    setPinDir(RED_LED_PIN, True)
    setPinDir(GREEN_LED_PIN, True)
    setPinDir(BLUE_LED_PIN, True)

    # Turn off the LEDs on startup
    r(0)
    g(0)
    b(0)


def r(on):
    """Control the red LED"""
    global G_RED_LED_ON
    G_RED_LED_ON = on
    # LEDs are active-low, so to turn on we need to write 0/False.
    writePin(RED_LED_PIN, on == 0)


def g(on):
    """Control the green LED"""
    global G_GREEN_LED_ON
    G_GREEN_LED_ON = on
    # LEDs are active-low, so to turn on we need to write 0/False.
    writePin(GREEN_LED_PIN, on == 0)


def b(on):
    """Control the blue LED"""
    global G_BLUE_LED_ON
    G_BLUE_LED_ON = on
    # LEDs are active-low, so to turn on we need to write 0/False.
    writePin(BLUE_LED_PIN, on == 0)


def set_rgb(rgb):
    """Control the LEDs"""
    r((rgb >> 2) & 1)
    g((rgb >> 1) & 1)
    b(rgb & 1)
    return get_rgb()


def get_rgb():
    """Return the last known state of the LEDs, encoded as 3 bits:
    00000rgb
    """
    return (G_RED_LED_ON << 2) | (G_GREEN_LED_ON << 1) | G_BLUE_LED_ON
