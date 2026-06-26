"""
Step definitions — device connection, identification, status.

Available steps (Given / When / Then / And):

  CONNECTION
    Given  the power supply is connected

  QUERIES  (результат → context.response)
    When   I query identification
    When   I query the firmware version
    When   I query the error status
    When   I read the device status

  RESPONSE ASSERTIONS
    Then   the response contains "TEXT"
    Then   the response equals "TEXT"
    Then   the response is not empty

  STATUS ASSERTIONS  (читають SYSTem:STATus? напряму)
    Then   the device is in CV mode
    Then   the device is in CC mode
    Then   the device mode is {CV|CC}
    Then   the status shows output is {ON|OFF}
    Then   the status shows OVP is {enabled|disabled}
    Then   the status shows OCP is {enabled|disabled}
"""

from behave import step


@step("the power supply is connected")
def step_connected(context):
    assert context.device is not None, "Device not connected (no port found?)"


# ── queries ───────────────────────────────────────────────────────────────────


@step("I query identification")
def step_idn(context):
    context.response = context.device.idn()


@step("I query the firmware version")
def step_version(context):
    context.response = context.device.version()


@step("I query the error status")
def step_error(context):
    context.response = context.device.error()


@step("I read the device status")
def step_read_status(context):
    context.status = context.device.status()
    context.response = context.status.get("raw", "")


# ── response assertions ───────────────────────────────────────────────────────


@step('the response contains "{text}"')
def step_response_contains(context, text):
    assert (
        text in context.response
    ), f"Expected {text!r} in response, got: {context.response!r}"


@step('the response equals "{text}"')
def step_response_equals(context, text):
    assert (
        context.response.strip() == text
    ), f"Expected {text!r}, got: {context.response!r}"


@step("the response is not empty")
def step_response_not_empty(context):
    assert context.response.strip(), "Response is empty"


# ── status assertions ─────────────────────────────────────────────────────────


def _status(context) -> dict:
    return context.device.status()


@step("the device is in CV mode")
def step_mode_cv(context):
    assert _status(context).get("mode") == "CV", "Expected CV mode"


@step("the device is in CC mode")
def step_mode_cc(context):
    assert _status(context).get("mode") == "CC", "Expected CC mode"


@step("the device mode is {mode}")
def step_mode(context, mode):
    actual = _status(context).get("mode")
    assert actual == mode.upper(), f"Expected {mode.upper()} mode, got {actual}"


@step("the status shows output is {state}")
def step_status_output(context, state):
    expected = state.upper() == "ON"
    actual = _status(context).get("output")
    assert actual == expected, f"Output: expected {expected}, got {actual}"


@step("the status shows OVP is {state}")
def step_status_ovp(context, state):
    expected = state.lower() == "enabled"
    actual = _status(context).get("ovp")
    assert actual == expected, f"OVP: expected {expected}, got {actual}"


@step("the status shows OCP is {state}")
def step_status_ocp(context, state):
    expected = state.lower() == "enabled"
    actual = _status(context).get("ocp")
    assert actual == expected, f"OCP: expected {expected}, got {actual}"
