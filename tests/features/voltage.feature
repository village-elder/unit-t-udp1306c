@device
Feature: Voltage setpoint control

  Background:
    Given the power supply is connected
    And the output is OFF

  Scenario Outline: Set output voltage
    When I set voltage to <volts> V
    Then the voltage setpoint reads <volts> V within 0.05

    Examples:
      | volts |
      |  0.00 |
      |  5.00 |
      | 12.00 |
      | 24.00 |
      | 32.00 |
