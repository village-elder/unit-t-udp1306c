@device
Feature: Memory slot save and recall

  Background:
    Given the power supply is connected
    And the output is OFF

  Scenario Outline: Save and recall a preset
    Given I set voltage to 10.00 V
    And I set current to 1.000 A
    When I save to memory slot <slot>
    And I wait 1 seconds
    And I set voltage to 0.00 V
    And I set current to 0.000 A
    And I recall memory slot <slot>
    And I wait 1 seconds
    Then the voltage setpoint reads 10.00 V within 0.05
    And the current setpoint reads 1.000 A within 0.01

    Examples:
      | slot |
      |    1 |
      |    3 |
      |    5 |
