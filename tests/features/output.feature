@device
Feature: Output enable/disable

  Background:
    Given the power supply is connected

  Scenario: Turn output ON
    Given the output is OFF
    When I turn the output ON
    Then the status shows output is ON

  Scenario: Turn output OFF
    Given the output is ON
    When I turn the output OFF
    Then the status shows output is OFF
