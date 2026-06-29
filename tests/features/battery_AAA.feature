@continuous_output
Feature: AAA battery charge level simulation

  Output is enabled once before the first scenario and stays ON throughout
  the entire feature — voltage transitions are seamless, no reconnection
  between charge levels.

  Background:
    Given the power supply is connected
    And I set current to 0.500 A

  Scenario Outline: Battery icon at <percent>% charge (<volts> V)
    When I set voltage to <volts> V
    And I wait 5 seconds
    Then the status shows output is ON

    Examples: AAA alkaline charge levels (0.90–1.65 V)
      | percent | volts |
      |     100 |  1.65 |
      |      80 |  1.50 |
      |      60 |  1.35 |
      |      40 |  1.20 |
      |      20 |  1.05 |
      |       0 |  0.90 |
