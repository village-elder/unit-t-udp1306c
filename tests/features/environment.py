"""Behave hooks: connect/disconnect device around each @device scenario."""

import logging
import os

from device import UDP1306C, find_port

log = logging.getLogger(__name__)


def before_all(context):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def before_scenario(context, scenario):
    context.device = None
    needs_device = "device" in scenario.tags or "device" in scenario.feature.tags
    if not needs_device:
        return

    port = os.environ.get("UDP1306C_PORT") or find_port()
    if not port:
        scenario.skip("No device found. Set UDP1306C_PORT env var or connect the PSU.")
        return

    try:
        context.device = UDP1306C(port)
        log.info("Connected to %s  [%s]", port, scenario.name)
    except Exception as exc:
        scenario.skip(f"Cannot open {port}: {exc}")


def after_scenario(context, scenario):
    if not context.device:
        return
    try:
        context.device.output(False)
    except Exception:
        log.warning("Could not turn off output after scenario", exc_info=True)
    context.device.close()
    context.device = None
