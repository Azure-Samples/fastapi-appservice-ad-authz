Feature: RBAC Scenarios

  Scenario: RBAC for plat-dev-admin to be able to do reader on dev
    Given I am part of below groups
      | group          |
      | plat-dev-admin |
    And Role hierarchy is set up and auth framework is initialised
    When I have access and id token
    Then User has reader role against dev environment

  Scenario: RBAC for plat-dev-admin to be able to do contributor on dev
    Given I am part of below groups
      | group          |
      | plat-dev-admin |
    And Role hierarchy is set up and auth framework is initialised
    When I have access and id token
    Then User has contributor role against dev environment

  Scenario: RBAC for plat-dev-admin not able to do reader on prod
    Given I am part of below groups
      | group          |
      | plat-dev-admin |
    And Role hierarchy is set up and auth framework is initialised
    When I have access and id token
    Then User does not have reader role against prod environment

  Scenario: RBAC for app-dev-reader not able to do reader on prod
    Given I am part of below groups
      | group          |
      | app-dev-reader |
    And Role hierarchy is set up and auth framework is initialised
    When I have access and id token
    Then User does not have reader role against prod environment

  Scenario: RBAC for app-prod-contributor able to do contributor role on prod will return empty for invalid environment
    Given I am part of below groups
      | group                |
      | app-prod-contributor |
    And Role hierarchy is set up and auth framework is initialised
    When I have access and id token
    Then User has contributor role against prod environment

  Scenario: RBAC for app-prod-contributor able to do reader role on prod
    Given I am part of below groups
      | group                |
      | app-prod-contributor |
    And Role hierarchy is set up and auth framework is initialised
    When I have access and id token
    Then User has reader role against prod environment

  Scenario: RBAC for app-dev-reader not able to do contributor on prod will give 403 for invalid role
    Given I am part of below groups
      | group          |
      | app-dev-reader |
    And Role hierarchy is set up and auth framework is initialised
    When I have access and id token
    Then User does not have contributor role against prod environment