@device
Feature: Device connection and identification

  Scenario: Identify the power supply
    Given the power supply is connected
    When I query identification
    Then the response contains "UDP1306C"

  Scenario: Read firmware version
    Given the power supply is connected
    When I query the firmware version
    Then the response is not empty
