"""
Step definitions — OVP and OCP protection.

Available steps (Given / When / Then / And):

  OVP PRECONDITIONS
    Given   OVP is {enabled|disabled}
    Given   OVP threshold is {V} V         ← тільки задає поріг, не вмикає

  OVP ACTIONS
    When    I enable OVP
    When    I disable OVP
    When    I enable OVP with threshold {V} V    ← задає поріг і вмикає
    When    I set the OVP threshold to {V} V     ← тільки поріг, без enable/disable
    When    I set OVP to {V} V                   ← alias

  OVP ASSERTIONS
    Then    the status shows OVP is {enabled|disabled}   (також у connection_steps)
    Then    OVP is active
    Then    OVP is inactive
    Then    the OVP threshold reads {V} V within {tol}
    Then    the OVP threshold is {V} V            ← допуск ±0.05 за замовчуванням

  OCP PRECONDITIONS
    Given   OCP is {enabled|disabled}
    Given   OCP threshold is {A} A

  OCP ACTIONS
    When    I enable OCP
    When    I disable OCP
    When    I enable OCP with threshold {A} A
    When    I set the OCP threshold to {A} A
    When    I set OCP to {A} A                   ← alias

  OCP ASSERTIONS
    Then    the status shows OCP is {enabled|disabled}   (також у connection_steps)
    Then    OCP is active
    Then    OCP is inactive
    Then    the OCP threshold reads {A} A within {tol}
    Then    the OCP threshold is {A} A            ← допуск ±0.01 за замовчуванням
"""

import time

from behave import step

_V_TOL = 0.05
_A_TOL = 0.01


# ── OVP preconditions ─────────────────────────────────────────────────────────


@step("OVP is {state}")
def step_ovp_preset(context, state):
    context.device.ovp_enable(state.lower() == "enabled")
    time.sleep(0.2)


@step("OVP threshold is {volts:f} V")
def step_ovp_threshold_preset(context, volts):
    context.device.ovp_set(round(volts, 2))
    time.sleep(0.2)


# ── OVP actions ───────────────────────────────────────────────────────────────


@step("I enable OVP")
def step_enable_ovp(context):
    context.device.ovp_enable(True)
    time.sleep(0.2)


@step("I disable OVP")
def step_disable_ovp(context):
    context.device.ovp_enable(False)
    time.sleep(0.2)


@step("I enable OVP with threshold {volts:f} V")
def step_enable_ovp_threshold(context, volts):
    context.device.ovp_set(round(volts, 2))
    context.device.ovp_enable(True)
    time.sleep(0.2)


@step("I set the OVP threshold to {volts:f} V")
def step_set_ovp_threshold(context, volts):
    context.device.ovp_set(round(volts, 2))
    time.sleep(0.2)


@step("I set OVP to {volts:f} V")
def step_set_ovp_short(context, volts):
    context.device.ovp_set(round(volts, 2))
    time.sleep(0.2)


# ── OVP assertions ────────────────────────────────────────────────────────────


@step("the OVP threshold reads {expected:f} V within {tol:f}")
def step_check_ovp_tol(context, expected, tol):
    actual = context.device.ovp_get()
    assert (
        abs(actual - expected) <= tol
    ), f"OVP threshold: expected {expected} ± {tol} V, got {actual:.3f} V"


@step("the OVP threshold is {expected:f} V")
def step_check_ovp_default(context, expected):
    actual = context.device.ovp_get()
    assert (
        abs(actual - expected) <= _V_TOL
    ), f"OVP threshold: expected {expected} ± {_V_TOL} V, got {actual:.3f} V"


# ── OCP preconditions ─────────────────────────────────────────────────────────


@step("OCP is {state}")
def step_ocp_preset(context, state):
    context.device.ocp_enable(state.lower() == "enabled")
    time.sleep(0.2)


@step("OCP threshold is {amps:f} A")
def step_ocp_threshold_preset(context, amps):
    context.device.ocp_set(round(amps, 3))
    time.sleep(0.2)


# ── OCP actions ───────────────────────────────────────────────────────────────


@step("I enable OCP")
def step_enable_ocp(context):
    context.device.ocp_enable(True)
    time.sleep(0.2)


@step("I disable OCP")
def step_disable_ocp(context):
    context.device.ocp_enable(False)
    time.sleep(0.2)


@step("I enable OCP with threshold {amps:f} A")
def step_enable_ocp_threshold(context, amps):
    context.device.ocp_set(round(amps, 3))
    context.device.ocp_enable(True)
    time.sleep(0.2)


@step("I set the OCP threshold to {amps:f} A")
def step_set_ocp_threshold(context, amps):
    context.device.ocp_set(round(amps, 3))
    time.sleep(0.2)


@step("I set OCP to {amps:f} A")
def step_set_ocp_short(context, amps):
    context.device.ocp_set(round(amps, 3))
    time.sleep(0.2)


# ── OCP assertions ────────────────────────────────────────────────────────────


@step("the OCP threshold reads {expected:f} A within {tol:f}")
def step_check_ocp_tol(context, expected, tol):
    actual = context.device.ocp_get()
    assert (
        abs(actual - expected) <= tol
    ), f"OCP threshold: expected {expected} ± {tol} A, got {actual:.4f} A"


@step("the OCP threshold is {expected:f} A")
def step_check_ocp_default(context, expected):
    actual = context.device.ocp_get()
    assert (
        abs(actual - expected) <= _A_TOL
    ), f"OCP threshold: expected {expected} ± {_A_TOL} A, got {actual:.4f} A"
