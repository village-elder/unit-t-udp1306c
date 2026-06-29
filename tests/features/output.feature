@device
Feature: Output enable/disable

  Background:
    Given the power supply is connected

  Scenario: Turn output ON
    Given the output is OFF
    When I turn the output ON
    And I wait 2 seconds
    Then the status shows output is ON

  Scenario: Turn output OFF
    Given the output is ON
    When I turn the output OFF
    And I wait 2 seconds
    Then the status shows output is OFF
