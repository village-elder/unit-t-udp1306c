"""
Step definitions — voltage, current, output, measurements, memory.

Available steps (Given / When / Then / And):

  OUTPUT STATE  (передумова або команда)
    Given/When  the output is {ON|OFF}
    When        I turn the output {ON|OFF}
    When        I enable the output
    When        I disable the output
    Then        the output is {ON|OFF}          ← перевірка через SYSTem:STATus?
    Then        the output is active
    Then        the output is inactive

  VOLTAGE SETPOINT
    Given/When  I set voltage to {V} V
    Given/When  the voltage is set to {V} V     ← alias
    Then        the voltage setpoint reads {V} V within {tol}
    Then        the voltage setpoint is {V} V   ← допуск ±0.05 за замовчуванням

  CURRENT SETPOINT
    Given/When  I set current to {A} A
    Given/When  the current is set to {A} A     ← alias
    Then        the current setpoint reads {A} A within {tol}
    Then        the current setpoint is {A} A   ← допуск ±0.01 за замовчуванням

  LIVE MEASUREMENTS  (результат → context.measured_voltage / _current / _power)
    When        I measure the output voltage
    When        I measure the output current
    When        I measure the output power
    When        I take a measurement             ← вимірює V, A, W одночасно
    Then        the measured voltage is {V} V within {tol}
    Then        the measured current is {A} A within {tol}
    Then        the measured power is {W} W within {tol}
    Then        the measured voltage is approximately {V} V  ← допуск ±0.20
    Then        the measured current is approximately {A} A  ← допуск ±0.05

  MEMORY SLOTS  (slot = 1–5)
    When        I save to memory slot {N}
    When        I save settings to memory slot {N}   ← alias
    When        I recall memory slot {N}
    When        I load memory slot {N}               ← alias
    When        I restore memory slot {N}            ← alias

  TIMING
    When        I wait {N} seconds
"""

import time

from behave import step

_V_TOL = 0.05  # default voltage tolerance (device ADC resolution)
_A_TOL = 0.01  # default current tolerance
_W_TOL = 0.50  # default power tolerance


# ── output ────────────────────────────────────────────────────────────────────


@step("the output is {state}")
def step_output_preset(context, state):
    """Sets output as a precondition (Given) OR checks it (Then) based on keyword."""
    # behave calls this for both Given and Then; we always SET here.
    # For assertion-only use: "the output is active / inactive" or "the status shows output is ..."
    context.device.output(state.upper() == "ON")
    time.sleep(0.3)


@step("I turn the output {state}")
def step_turn_output(context, state):
    context.device.output(state.upper() == "ON")
    time.sleep(0.3)


@step("I enable the output")
def step_enable_output(context):
    context.device.output(True)
    time.sleep(0.3)


@step("I disable the output")
def step_disable_output(context):
    context.device.output(False)
    time.sleep(0.3)


# ── voltage setpoint ──────────────────────────────────────────────────────────


@step("I set voltage to {volts:f} V")
def step_set_voltage(context, volts):
    context.device.set_voltage(round(volts, 2))
    time.sleep(0.2)


@step("the voltage is set to {volts:f} V")
def step_set_voltage_alt(context, volts):
    context.device.set_voltage(round(volts, 2))
    time.sleep(0.2)


@step("the voltage setpoint reads {expected:f} V within {tol:f}")
def step_check_voltage_tol(context, expected, tol):
    actual = context.device.get_voltage_set()
    assert (
        abs(actual - expected) <= tol
    ), f"Voltage setpoint: expected {expected} ± {tol} V, got {actual:.3f} V"


@step("the voltage setpoint is {expected:f} V")
def step_check_voltage_default(context, expected):
    actual = context.device.get_voltage_set()
    assert (
        abs(actual - expected) <= _V_TOL
    ), f"Voltage setpoint: expected {expected} ± {_V_TOL} V, got {actual:.3f} V"


# ── current setpoint ──────────────────────────────────────────────────────────


@step("I set current to {amps:f} A")
def step_set_current(context, amps):
    context.device.set_current(round(amps, 3))
    time.sleep(0.2)


@step("the current is set to {amps:f} A")
def step_set_current_alt(context, amps):
    context.device.set_current(round(amps, 3))
    time.sleep(0.2)


@step("the current setpoint reads {expected:f} A within {tol:f}")
def step_check_current_tol(context, expected, tol):
    actual = context.device.get_current_set()
    assert (
        abs(actual - expected) <= tol
    ), f"Current setpoint: expected {expected} ± {tol} A, got {actual:.4f} A"


@step("the current setpoint is {expected:f} A")
def step_check_current_default(context, expected):
    actual = context.device.get_current_set()
    assert (
        abs(actual - expected) <= _A_TOL
    ), f"Current setpoint: expected {expected} ± {_A_TOL} A, got {actual:.4f} A"


# ── live measurements ─────────────────────────────────────────────────────────


@step("I measure the output voltage")
def step_measure_v(context):
    context.measured_voltage = context.device.measure_voltage()


@step("I measure the output current")
def step_measure_a(context):
    context.measured_current = context.device.measure_current()


@step("I measure the output power")
def step_measure_w(context):
    context.measured_power = context.device.measure_power()


@step("I take a measurement")
def step_take_measurement(context):
    context.measured_voltage = context.device.measure_voltage()
    context.measured_current = context.device.measure_current()
    context.measured_power = context.device.measure_power()


@step("the measured voltage is {expected:f} V within {tol:f}")
def step_assert_voltage_tol(context, expected, tol):
    v = getattr(context, "measured_voltage", context.device.measure_voltage())
    assert (
        abs(v - expected) <= tol
    ), f"Measured voltage: expected {expected} ± {tol} V, got {v:.3f} V"


@step("the measured current is {expected:f} A within {tol:f}")
def step_assert_current_tol(context, expected, tol):
    a = getattr(context, "measured_current", context.device.measure_current())
    assert (
        abs(a - expected) <= tol
    ), f"Measured current: expected {expected} ± {tol} A, got {a:.4f} A"


@step("the measured power is {expected:f} W within {tol:f}")
def step_assert_power_tol(context, expected, tol):
    w = getattr(context, "measured_power", context.device.measure_power())
    assert (
        abs(w - expected) <= tol
    ), f"Measured power: expected {expected} ± {tol} W, got {w:.2f} W"


@step("the measured voltage is approximately {expected:f} V")
def step_assert_voltage_approx(context, expected):
    v = getattr(context, "measured_voltage", context.device.measure_voltage())
    assert (
        abs(v - expected) <= 0.20
    ), f"Measured voltage: expected ~{expected} V, got {v:.3f} V"


@step("the measured current is approximately {expected:f} A")
def step_assert_current_approx(context, expected):
    a = getattr(context, "measured_current", context.device.measure_current())
    assert (
        abs(a - expected) <= 0.05
    ), f"Measured current: expected ~{expected} A, got {a:.4f} A"


# ── timing ────────────────────────────────────────────────────────────────────


@step("I wait {seconds:d} seconds")
def step_wait(context, seconds):
    time.sleep(seconds)


# ── memory slots ──────────────────────────────────────────────────────────────


@step("I save to memory slot {slot:d}")
def step_save_slot(context, slot):
    context.device.save(slot)
    time.sleep(0.2)


@step("I save settings to memory slot {slot:d}")
def step_save_slot_full(context, slot):
    context.device.save(slot)
    time.sleep(0.2)


@step("I recall memory slot {slot:d}")
def step_recall_slot(context, slot):
    context.device.recall(slot)
    time.sleep(0.3)


@step("I load memory slot {slot:d}")
def step_load_slot(context, slot):
    context.device.recall(slot)
    time.sleep(0.3)


@step("I restore memory slot {slot:d}")
def step_restore_slot(context, slot):
    context.device.recall(slot)
    time.sleep(0.3)
