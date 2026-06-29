@device
Feature: Current limit control

  Background:
    Given the power supply is connected
    And the output is OFF

  Scenario Outline: Set current limit
    When I set current to <amps> A
    And I wait 1 seconds
    Then the current setpoint reads <amps> A within 0.01

    Examples:
      | amps  |
      | 0.000 |
      | 0.500 |
      | 1.000 |
      | 3.000 |
      | 6.000 |
