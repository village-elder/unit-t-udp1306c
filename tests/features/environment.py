"""Behave hooks: connect/disconnect device around each @device scenario.

Tags:
  @device            — scenario/feature needs a physical device
  @continuous_output — device is connected once per feature, output stays ON
                       between scenarios (useful for sweep/simulation tests)
"""

import logging
import os
import threading
import time

from device import UDP1306C, find_port

log = logging.getLogger(__name__)

SCENARIO_TIMEOUT = int(os.environ.get("BDD_TIMEOUT", 60))


def before_all(context):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def before_feature(context, feature):
    if "continuous_output" not in feature.tags:
        return

    port = os.environ.get("UDP1306C_PORT") or find_port()
    if not port:
        context._continuous_error = (
            "No device found. Set UDP1306C_PORT or connect the PSU."
        )
        return

    try:
        context.device = UDP1306C(port)
        context.device.output(True)
        context._continuous_error = None
        log.info("Connected [continuous output] on %s for: %s", port, feature.name)
    except Exception as exc:
        context._continuous_error = str(exc)
        context.device = None


def after_feature(context, feature):
    if "continuous_output" not in feature.tags:
        return
    if not getattr(context, "device", None):
        return
    try:
        context.device.output(False)
    except Exception:
        log.warning("Could not turn off output after feature", exc_info=True)
    context.device.close()
    context.device = None


def before_scenario(context, scenario):
    context._timeout_hit = False
    context._t0 = time.monotonic()

    def _on_timeout():
        context._timeout_hit = True

    context._timer = threading.Timer(SCENARIO_TIMEOUT, _on_timeout)
    context._timer.daemon = True
    context._timer.start()

    # Device managed at feature level — just check for connection errors
    if "continuous_output" in scenario.feature.tags:
        error = getattr(context, "_continuous_error", None)
        if error:
            scenario.skip(error)
        return

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


def after_step(context, step):
    if context._timeout_hit:
        elapsed = time.monotonic() - context._t0
        context.scenario.skip(
            f"Scenario timeout: {elapsed:.1f}s exceeded {SCENARIO_TIMEOUT}s"
        )


def after_scenario(context, scenario):
    context._timer.cancel()

    # Output stays ON between scenarios — cleanup happens in after_feature
    if "continuous_output" in scenario.feature.tags:
        return

    if not context.device:
        return
    try:
        context.device.output(False)
    except Exception:
        log.warning("Could not turn off output after scenario", exc_info=True)
    context.device.close()
    context.device = None
