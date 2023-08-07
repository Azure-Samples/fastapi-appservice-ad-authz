Feature: API Scenarios

  Scenario: call an-authenticated api
    When I hit the /unauthenticated/messages to get records
    Then The response status code should be 200
    And The response should have below attribute
      | attribute_name | value |
      | message        | Hello |

  Scenario: call protected api with invalid role
    Given I am part of below groups
      | group              |
      | system-dev-invalid |
    When I hit the /authenticated/messages to get records
    Then The response status code should be 403

  Scenario: call protected api with reader role
    Given I am part of below groups
      | group             |
      | system-dev-reader |
    When I hit the /authenticated/messages to get records
    Then The response status code should be 200

  Scenario: call protected post api with correct role
    Given I am part of below groups
      | group                  |
      | system-dev-contributor |
    When I hit the /authenticated/message/hello of type post with below data
    Then The response status code should be 200

  Scenario: call protected post api without correct role
    Given I am part of below groups
      | group             |
      | system-dev-reader |
    When I hit the /authenticated/message/hello of type post with below data
    Then The response status code should be 403


