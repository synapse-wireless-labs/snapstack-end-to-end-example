"""
An example of using SNAPstack + Tornado to build an HTTP API for RGB LED control

HTTP API:
GET /(snap_address)/rgb: Request state of RGB LEDs
PATCH /(snap_address)bridge/rgb: Set RGB LEDs

SNAP API:
get_rgb() -> int
set_rgb(int) -> int
"""

import argparse
import asyncio
import logging

import tornado

from snapstack.interface.serial_wrapper import SerialType
from snapstack.snap import Snap

LOG = logging.getLogger(__name__)


async def main(args):
    """Main application glue"""

    # Initialize the SNAP RGB Control instance
    rgb_control = RGBControl(args.device)
    await rgb_control.start()

    # Set up the Tornado application w/ RGBHandler
    app = tornado.web.Application(
        [
            (r"/([0-9a-fA-F]{6}|bridge)/rgb", RGBHandler, {"rgb_control": rgb_control}),
        ]
    )

    svr = app.listen(args.port)

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        svr.stop()
        await svr.close_all_connections()
        rgb_control.stop()


class RGBControl:
    """SNAP RGB Control

    Holds the SNAPstack instance and provides convenience functions for calling RPCs
    """

    def __init__(self, device):
        self.device = device
        self.snap = None
        self.bridge = None

    async def start(self):
        """Start the SNAPstack instance and discover the bridge node's address"""
        self.snap = Snap()
        self.snap.start()
        LOG.info(f"Opening serial port {self.device}")
        self.snap.open_serial(self.device, SerialType.PYSERIAL)
        self.bridge = await self.snap.get_serial_bridge_address(self.device)
        LOG.info(f"Found bridge address: {self.bridge}")

    def stop(self):
        """Stop the SNAPstack instance"""
        self.snap.stop()

    async def get_rgb(self, target):
        """Call target.get_rgb()"""
        target = self._normalize_target(target)

        responses = await self.snap.call_dmcast_rpc([target], b"get_rgb", ())
        result = responses.get(target)
        if result:
            return self._decode_result(result)
        else:
            return None

    async def set_rgb(self, target, vals):
        """Call target.set_rgb(vals)"""
        target = self._normalize_target(target)

        responses = await self.snap.call_dmcast_rpc(
            [target], b"set_rgb", (self._encode_rgb(vals),)
        )
        result = responses.get(target)
        if result:
            return self._decode_result(result)
        else:
            return None

    def _normalize_target(self, target):
        """Given a target address, encode it as 6 bytes.

        Also translate 'bridge' to the appropriate address.
        """
        target = target.encode()
        if target == b"bridge":
            target = self.bridge

        LOG.debug(f"Target address: {target}")
        return target

    def _encode_rgb(self, rgb):
        """Convert dict of discrete RGB 1/0 values to an encoded int"""
        return (rgb["r"] << 2) | (rgb["g"] << 1) | (rgb["b"] << 0)

    def _decode_result(self, result):
        """Convert the encoded int to a dict of RGB state"""
        rgb = result.args_as(int)[0]
        return {
            "r": (rgb >> 2) & 1,
            "g": (rgb >> 1) & 1,
            "b": rgb & 1,
        }


class RGBHandler(tornado.web.RequestHandler):
    """Handler for HTTP API

    Encodes RGB values as JSON objects w/ "r", "g", "b" keys.
    """

    def initialize(self, rgb_control):
        self.rgb_control = rgb_control

    async def get(self, target):
        result = await self.rgb_control.get_rgb(target)

        if result:
            self.set_status(200)
            self.write(result)
        else:
            self.set_status(500)

    async def post(self, target):

        rgb = tornado.escape.json_decode(self.request.body)

        result = await self.rgb_control.set_rgb(target, rgb)

        if result:
            self.set_status(200)
            self.write(result)
        else:
            self.set_status(500)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Example of SNAPstack RPCs")

    parser.add_argument(
        "device",
        help="""Serial device for SNAP bridge node, e.g.: COM3 (on Windows), /dev/snap1 (on an E12/E20 gateway), /dev/ttyUSB0 (on Linux), or /dev/tty.usbserial-A123456B (on macOS)""",
        default="/dev/snap1",
    )
    parser.add_argument("-p", "--port", help="Port on which to listen", default=8888)
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase verbosity of logs (-v for INFO, -vv for DEBUG)",
        action="count",
        default=0,
    )

    args = parser.parse_args()

    # Convert count of verbose flags to log level
    log_level = [logging.WARN, logging.INFO, logging.DEBUG][min(args.verbose, 2)]

    logging.basicConfig(level=log_level)

    asyncio.run(main(args))
