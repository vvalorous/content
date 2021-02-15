"""
    FraudWatch - Unit Tests file
"""
import io
import json
from typing import *

import pytest
import pytz

from CommonServerPython import DemistoException, datetime, CommandResults
from FraudWatch import get_and_validate_positive_int_argument, get_time_parameter, Client, \
    fraud_watch_incidents_list_command, fraud_watch_incident_get_by_identifier_command, \
    fraud_watch_incident_forensic_get_command, fraud_watch_incident_contact_emails_list_command, \
    fraud_watch_brands_list_command, fraud_watch_incident_report_command, fraud_watch_incident_update_command, \
    fraud_watch_incident_messages_add_command, fraud_watch_incident_urls_add_command, BASE_URL, MINIMUM_POSITIVE_VALUE

client = Client(
    api_key='api_key',
    base_url=BASE_URL,
    verify=False,
    proxy=False
)


def util_load_json(path):
    with io.open(path, mode='r', encoding='utf-8') as f:
        return json.loads(f.read())


command_tests_data = util_load_json('test_data/commands_data.json')


@pytest.mark.parametrize('args, argument_name, expected',
                         [
                             ({'page': 3}, 'limit', None),
                             ({'limit': 4}, 'limit', 4),
                             ({'limit': 1}, 'limit', 1)
                         ])
def test_get_and_validate_positive_int_argument_valid_arguments(args, argument_name, expected):
    """
    Given:
     - Demisto arguments.
     - Argument name to extract from Demisto arguments as number.

    When:
     - Case a: Argument does not exist.
     - Case b: Argument exist and is above minimum.
     - Case c: Argument exist and equals minimum.

    Then:
     - Case a: Ensure that None is returned (limit argument does not exist).
     - Case b: Ensure that limit is returned (4).
     - Case c: Ensure that limit is returned (1).
    """
    assert (get_and_validate_positive_int_argument(args, argument_name)) == expected


def test_get_and_validate_positive_int_argument_invalid_arguments():
    """
    Given:
     - Demisto arguments.
     - Argument name to extract from Demisto arguments as number.

    When:
     - Argument exists and is not positive.

    Then:
     - Ensure that DemistoException is thrown with error message which indicates that value is not positive.
    """
    with pytest.raises(DemistoException, match=f'limit should be equal or higher than {MINIMUM_POSITIVE_VALUE}'):
        get_and_validate_positive_int_argument({'limit': -3}, 'limit')


@pytest.mark.parametrize('arg, parse_format, expected',
                         [('2020-11-22T16:31:14-02:00', False, datetime(2020, 11, 22, 18, 31, 14, tzinfo=pytz.utc)),
                          (None, False, None),
                          (None, True, None), ('2020-12-12', True, '2020-12-12'),
                          ('2020-12-12T10:11:22', True, '2020-12-12'), ('2020-12-12T22:11:22-03:00', True, '2020-12-13')
                          ])
def test_get_optional_time_parameter_valid_time_argument(arg, parse_format, expected):
    """
    Given:
     - Demisto arguments.
     - Argument of type time to extract from Demisto arguments as epoch time.

    When:
     - Case a: Argument exists, has expected date format, parse format was not asked,.
     - Case b: Argument does not exist, parse format was not asked.
     - Case c: Argument does not exist, parse format was asked.
     - Case d: Argument exist and has ISO format, parse format was asked.
     - Case e: Argument exist and has ISO format, parse format was asked.

    Then:
     - Case a: Ensure that the corresponding epoch time is returned.
     - Case b: Ensure that None is returned.
     - Case c: Ensure that None is returned.
     - Case d: Ensure that correct FraudWatch format is returned.
     - Case e: Ensure that correct FraudWatch format is returned.
    """
    assert (get_time_parameter(arg, parse_format)) == expected


@pytest.mark.parametrize('command_function, args, url_suffix, response, expected',
                         [(fraud_watch_incidents_list_command,
                           command_tests_data['fraudwatch-incidents-list']['args'],
                           command_tests_data['fraudwatch-incidents-list']['suffix'],
                           command_tests_data['fraudwatch-incidents-list']['response'],
                           command_tests_data['fraudwatch-incidents-list']['expected']),

                          (fraud_watch_incident_get_by_identifier_command,
                           command_tests_data['fraudwatch-incident-get-by-identifier']['reference_id_args'],
                           command_tests_data['fraudwatch-incident-get-by-identifier']['reference_id_suffix'],
                           command_tests_data['fraudwatch-incident-get-by-identifier']['response'],
                           command_tests_data['fraudwatch-incident-get-by-identifier']['expected']),

                          (fraud_watch_incident_get_by_identifier_command,
                           command_tests_data['fraudwatch-incident-get-by-identifier']['incident_id_args'],
                           command_tests_data['fraudwatch-incident-get-by-identifier']['incident_id_suffix'],
                           command_tests_data['fraudwatch-incident-get-by-identifier']['response'],
                           command_tests_data['fraudwatch-incident-get-by-identifier']['expected']),

                          (fraud_watch_incident_forensic_get_command,
                           command_tests_data['fraudwatch-incident-forensic-get']['args'],
                           command_tests_data['fraudwatch-incident-forensic-get']['suffix'],
                           command_tests_data['fraudwatch-incident-forensic-get']['response'],
                           command_tests_data['fraudwatch-incident-forensic-get']['expected']),

                          (fraud_watch_incident_contact_emails_list_command,
                           command_tests_data['fraudwatch-incident-contact-emails-list']['args'],
                           command_tests_data['fraudwatch-incident-contact-emails-list']['suffix'],
                           command_tests_data['fraudwatch-incident-contact-emails-list']['response'],
                           command_tests_data['fraudwatch-incident-contact-emails-list']['expected']),

                          (fraud_watch_brands_list_command,
                           command_tests_data['fraudwatch-brands-list']['args'],
                           command_tests_data['fraudwatch-brands-list']['suffix'],
                           command_tests_data['fraudwatch-brands-list']['response'],
                           command_tests_data['fraudwatch-brands-list']['expected'])
                          ])
def test_commands_get_methods(requests_mock, command_function: Callable[[Client, Dict], CommandResults], args: Dict,
                              url_suffix: str, response: Dict, expected: Dict):
    """
    Given:
     - command function.
     - Demisto arguments.
     - url suffix of the Nutanix service endpoint that the command function will use (needed to mock the request).
     - response returned from Nutanix.
     - expected CommandResults object to be returned from the command function.

    When:
     - Executing a command

    Then:
     - Ensure that the expected CommandResults object is returned by the command function.
    """
    requests_mock.get(
        f'{BASE_URL}{url_suffix}',
        json=response
    )
    expected_command_results = CommandResults(
        outputs_prefix=expected.get('outputs_prefix'),
        outputs_key_field=expected.get('outputs_key_field'),
        outputs=expected.get('outputs')
    )
    returned_command_results = command_function(client, args)

    assert returned_command_results.outputs_prefix == expected_command_results.outputs_prefix
    assert returned_command_results.outputs_key_field == expected_command_results.outputs_key_field
    assert returned_command_results.outputs == expected_command_results.outputs


@pytest.mark.parametrize('command_function, args, url_suffix, response, expected',
                         [(fraud_watch_incident_update_command,
                           command_tests_data['fraudwatch-incident-update']['args'],
                           command_tests_data['fraudwatch-incident-update']['suffix'],
                           command_tests_data['fraudwatch-incident-update']['response'],
                           command_tests_data['fraudwatch-incident-update']['expected']),

                          ])
def test_commands_put_methods(requests_mock, command_function: Callable[[Client, Dict], CommandResults], args: Dict,
                              url_suffix: str, response: Dict, expected: Dict):
    """
    Given:
     - command function.
     - Demisto arguments.
     - url suffix of the Nutanix service endpoint that the command function will use (needed to mock the request).
     - response returned from Nutanix.
     - expected CommandResults object to be returned from the command function.

    When:
     - Executing a command

    Then:
     - Ensure that the expected CommandResults object is returned by the command function.
    """
    requests_mock.put(
        f'{BASE_URL}{url_suffix}',
        json=response
    )
    expected_command_results = CommandResults(
        outputs_prefix=expected.get('outputs_prefix'),
        outputs_key_field=expected.get('outputs_key_field'),
        outputs=expected.get('outputs')
    )
    returned_command_results = command_function(client, args)

    assert returned_command_results.outputs_prefix == expected_command_results.outputs_prefix
    assert returned_command_results.outputs_key_field == expected_command_results.outputs_key_field
    assert returned_command_results.outputs == expected_command_results.outputs


@pytest.mark.parametrize('command_function, args, url_suffix, response, expected',
                         [(fraud_watch_incident_report_command,
                           command_tests_data['fraudwatch-incident-report']['args'],
                           command_tests_data['fraudwatch-incident-report']['suffix'],
                           command_tests_data['fraudwatch-incident-report']['response'],
                           command_tests_data['fraudwatch-incident-report']['expected']),

                          (fraud_watch_incident_messages_add_command,
                           command_tests_data['fraudwatch-incident-messages-add']['args'],
                           command_tests_data['fraudwatch-incident-messages-add']['suffix'],
                           command_tests_data['fraudwatch-incident-messages-add']['response'],
                           command_tests_data['fraudwatch-incident-messages-add']['expected']),

                          (fraud_watch_incident_urls_add_command,
                           command_tests_data['fraudwatch-incident-urls-add']['args'],
                           command_tests_data['fraudwatch-incident-urls-add']['suffix'],
                           command_tests_data['fraudwatch-incident-urls-add']['response'],
                           command_tests_data['fraudwatch-incident-urls-add']['expected'])
                          ])
def test_commands_post_methods(requests_mock, command_function: Callable[[Client, Dict], CommandResults], args: Dict,
                               url_suffix: str, response: Dict, expected: Dict):
    """
    Given:
     - Command function.
     - Demisto arguments.
     - URL suffix of the Nutanix service endpoint that the command function will use (needed to mock the request).
     - Response returned from Nutanix.
     - Expected CommandResults object to be returned from the command function.

    When:
     - Executing a command

    Then:
     - Ensure that the expected CommandResults object is returned by the command function.
    """
    requests_mock.post(
        f'{BASE_URL}{url_suffix}',
        json=response
    )
    expected_command_results = CommandResults(
        outputs_prefix=expected.get('outputs_prefix'),
        outputs_key_field=expected.get('outputs_key_field'),
        outputs=expected.get('outputs')
    )
    returned_command_results = command_function(client, args)

    assert returned_command_results.outputs_prefix == expected_command_results.outputs_prefix
    assert returned_command_results.outputs_key_field == expected_command_results.outputs_key_field
    assert returned_command_results.outputs == expected_command_results.outputs
