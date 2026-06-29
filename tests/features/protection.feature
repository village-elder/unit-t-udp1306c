@device
Feature: OVP and OCP protection

  Background:
    Given the power supply is connected
    And the output is OFF

  Scenario: Enable OVP with threshold
    Given OVP is disabled
    When I enable OVP with threshold 13.00 V
    And I wait 1 seconds
    Then the status shows OVP is enabled
    And the OVP threshold reads 13.00 V within 0.05

  Scenario: Disable OVP
    Given OVP is enabled
    When I disable OVP
    And I wait 1 seconds
    Then the status shows OVP is disabled

  Scenario: Enable OCP with threshold
    Given OCP is disabled
    When I enable OCP with threshold 2.000 A
    And I wait 1 seconds
    Then the status shows OCP is enabled
    And the OCP threshold reads 2.000 A within 0.01

  Scenario: Disable OCP
    Given OCP is enabled
    When I disable OCP
    And I wait 1 seconds
    Then the status shows OCP is disabled
