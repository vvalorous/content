"""
    FraudWatch - Unit Tests file
"""
import io
import json

import pytest

from CommonServerPython import DemistoException
from FraudWatch import get_and_validate_int_argument


def util_load_json(path):
    with io.open(path, mode='r', encoding='utf-8') as f:
        return json.loads(f.read())


@pytest.mark.parametrize('args, argument_name, minimum, expected',
                         [
                             ({'page': 3}, 'limit', 4, None),
                             ({'limit': 4}, 'limit', 3, 4),
                             ({'limit': 2}, 'limit', 2, 2)
                         ])
def test_get_and_validate_int_argument_valid_arguments(args, argument_name, minimum, expected):
    """
    Given:
     - Demisto arguments.
     - Argument name to extract from Demisto arguments as number.
     - Minimum possible value for argument.

    When:
     - Case b: Argument does not exist.
     - Case c: Argument exist and is above minimum.
     - Case c: Argument exist and equals minimum.

    Then:
     - Case a: Ensure that None is returned (limit argument does not exist).
     - Case b: Ensure that limit is returned (4).
     - Case c: Ensure that limit is returned (2).
    """
    assert (get_and_validate_int_argument(args, argument_name, minimum)) == expected


@pytest.mark.parametrize('args, argument_name, minimum, maximum, default_value, expected_error_message',
                         [({'limit': 5}, 'limit', 6, None, None, 'limit should be equal or higher than 6'),
                          ({'limit': 5}, 'limit', None, 4, None, 'limit should be equal or less than 4'),
                          ({}, 'limit', 3, 4, 5, 'limit should be equal or less than 4')
                          ])
def test_get_and_validate_int_argument_invalid_arguments(args, argument_name, minimum, maximum, default_value,
                                                         expected_error_message):
    """
    Given:
     - Demisto arguments.
     - Argument name to extract from Demisto arguments as number.
     - Minimum value for argument.

    When:
     - Argument exists, minimum is higher than argument value.

    Then:
     - Ensure that DemistoException is thrown with error message which indicates that value is below minimum.
    """
    with pytest.raises(DemistoException, match='limit should be equal or higher than 2'):
        get_and_validate_int_argument({'limit': 3}, 'limit', 2)
