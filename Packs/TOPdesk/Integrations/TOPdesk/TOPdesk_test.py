import pytest
import demistomock as demisto
import json
import io
from TOPdesk import Client, INTEGRATION_NAME, MAX_API_PAGE_SIZE, XSOAR_ENTRY_TYPE, \
    fetch_incidents, entry_types_command, call_types_command, categories_command, subcategories_command, \
    list_persons_command, list_operators_command, branches_command, get_incidents_list_command, \
    get_incidents_with_pagination, incident_do_command, incident_touch_command, attachment_upload_command, \
    escalation_reasons_command, deescalation_reasons_command, archiving_reasons_command


def util_load_json(path):
    with io.open(path, mode='r', encoding='utf-8') as f:
        return json.loads(f.read())


@pytest.mark.parametrize('command, command_api_url, mock_response, expected_results', [
    (entry_types_command,
     'https://test.com/api/v1/incidents/entry_types',
     [{"id": "1st-id", "name": "entry-type-1"}, {"id": "2st-id", "name": "entry-type-2"}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.entryType',
         'outputs_key_field': 'id'
     }),
    (call_types_command,
     'https://test.com/api/v1/incidents/call_types',
     [{"id": "1st-id", "name": "call-type-1"}, {"id": "2st-id", "name": "call-type-2"}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.callType',
         'outputs_key_field': 'id'
     }),
    (categories_command,
     'https://test.com/api/v1/incidents/categories',
     [{"id": "1st-id", "name": "category-1"}, {"id": "2st-id", "name": "category-2"}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.category',
         'outputs_key_field': 'id'
     }),
    (subcategories_command,
     'https://test.com/api/v1/incidents/subcategories',
     [{"id": "1st-id-sub", "name": "subcategory-1", "category": {"id": "1st-id", "name": "category-1"}},
      {"id": "2st-id-sub", "name": "subcategory-2", "category": {"id": "2st-id", "name": "category-2"}}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.subcategories',
         'outputs_key_field': 'id'
     }),
    (escalation_reasons_command,
     'https://test.com/api/v1/incidents/escalation-reasons',
     [{"id": "1st-id", "name": "escalation-name-1"}, {"id": "2st-id", "name": "escalation-name-2"}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.escalation_reason',
         'outputs_key_field': 'id'
     }),
    (deescalation_reasons_command,
     'https://test.com/api/v1/incidents/deescalation-reasons',
     [{"id": "1st-id", "name": "deescalation-name-1"}, {"id": "2st-id", "name": "deescalation-name-2"}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.deescalation_reason',
         'outputs_key_field': 'id'
     }),
    (archiving_reasons_command,
     'https://test.com/api/v1/archiving-reasons',
     [{"id": "1st-id", "name": "archiving-reason-1"}, {"id": "2st-id", "name": "archiving-reason-2"}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.archive_reason',
         'outputs_key_field': 'id'
     })
])
def test_list_command(requests_mock, command, command_api_url, mock_response, expected_results):
    """Unit test
    Given
        - command
    When
        - running the command
    Then
        - validate the entry context.
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=True
    )
    requests_mock.get(
        command_api_url, json=mock_response)
    command_results = command(client)
    assert command_results.outputs_prefix == expected_results['outputs_prefix']
    assert command_results.outputs_key_field == expected_results['outputs_key_field']
    assert command_results.outputs == mock_response


@pytest.mark.parametrize('command, command_api_url, mock_response_file, override_nodes, expected_results', [
    (list_persons_command,
     'https://test.com/api/v1/persons',
     'test_data/topdesk_person.json',
     [{'id': '1st-person-id'}, {'id': '2nd-person-id'}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.person',
         'outputs_key_field': 'id'
     }),
    (list_operators_command,
     'https://test.com/api/v1/operators',
     'test_data/topdesk_operator.json',
     [{'id': '1st-operator-id'}, {'id': '2nd-operator-id'}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.operator',
         'outputs_key_field': 'id'
     }),
    (branches_command,
     'https://test.com/api/v1/branches',
     'test_data/topdesk_branch.json',
     [{"id": "1st-branch-id"}, {"id": "2nd-branch-id"}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.branch',
         'outputs_key_field': 'id'
     }),
    (get_incidents_list_command,
     'https://test.com/api/v1/incidents',
     'test_data/topdesk_incident.json',
     [{"id": "1st-incident-id"}, {"id": "2nd-incident-id"}],
     {
         'outputs_prefix': f'{INTEGRATION_NAME}.incident',
         'outputs_key_field': 'id'
     })
])
def test_large_output_list_command(requests_mock,
                                   command,
                                   command_api_url,
                                   mock_response_file,
                                   override_nodes,
                                   expected_results):
    """Unit test
    Given
        - command
    When
        - running the command
    Then
        - validate the entry context.
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=True
    )
    mock_topdesk_node = util_load_json(mock_response_file)
    mock_topdesk_response = []
    for node_override in override_nodes:
        response_node = mock_topdesk_node.copy()
        response_node['id'] = node_override['id']
        mock_topdesk_response.append(response_node)

    requests_mock.get(
        command_api_url, json=mock_topdesk_response)
    command_results = command(client, {})
    assert command_results.outputs_prefix == expected_results['outputs_prefix']
    assert command_results.outputs_key_field == expected_results['outputs_key_field']
    assert command_results.outputs == mock_topdesk_response


@pytest.mark.parametrize('action, command_args, command_api_url, mock_response_file, override_node', [
    ("escalate",
     {"id": "incident_id", "escalate_reason_id": "some_reason"},
     'https://test.com/api/v1/incidents/id/incident_id/escalate',
     'test_data/topdesk_incident.json',
     {'id': 'incident_id'}),
    ("deescalate",
     {"id": "incident_id", "deescalate_reason_id": "some_reason"},
     'https://test.com/api/v1/incidents/id/incident_id/deescalate',
     'test_data/topdesk_incident.json',
     {'id': 'incident_id'}),
    ("archive",
     {"id": "incident_id", "archive_reason_id": "some_reason"},
     'https://test.com/api/v1/incidents/id/incident_id/archive',
     'test_data/topdesk_incident.json',
     {'id': 'incident_id'}),
    ("unarchive",
     {"id": "incident_id"},
     'https://test.com/api/v1/incidents/id/incident_id/unarchive',
     'test_data/topdesk_incident.json',
     {'id': 'incident_id'}),
    ("escalate",
     {"number": "incident_number", "escalate_reason_id": "some_reason"},
     'https://test.com/api/v1/incidents/number/incident_number/escalate',
     'test_data/topdesk_incident.json',
     {'number': 'incident_number'}),
    ("deescalate",
     {"number": "incident_number", "deescalate_reason_id": "some_reason"},
     'https://test.com/api/v1/incidents/number/incident_number/deescalate',
     'test_data/topdesk_incident.json',
     {'number': 'incident_number'}),
    ("archive",
     {"number": "incident_number", "archive_reason_id": "some_reason"},
     'https://test.com/api/v1/incidents/number/incident_number/archive',
     'test_data/topdesk_incident.json',
     {'number': 'incident_number'}),
    ("unarchive",
     {"number": "incident_number"},
     'https://test.com/api/v1/incidents/number/incident_number/unarchive',
     'test_data/topdesk_incident.json',
     {'number': 'incident_number'}),
    ("escalate",
     {"id": "incident_id", "number": "incident_number", "escalate_reason_id": "some_reason"},
     'https://test.com/api/v1/incidents/id/incident_id/escalate',
     'test_data/topdesk_incident.json',
     {'id': 'incident_id'}),
    ("deescalate",
     {"id": "incident_id", "number": "incident_number", "deescalate_reason_id": "some_reason"},
     'https://test.com/api/v1/incidents/id/incident_id/deescalate',
     'test_data/topdesk_incident.json',
     {'id': 'incident_id'}),
    ("archive",
     {"id": "incident_id", "number": "incident_number", "archive_reason_id": "some_reason"},
     'https://test.com/api/v1/incidents/id/incident_id/archive',
     'test_data/topdesk_incident.json',
     {'id': 'incident_id'}),
    ("unarchive",
     {"id": "incident_id", "number": "incident_number"},
     'https://test.com/api/v1/incidents/id/incident_id/unarchive',
     'test_data/topdesk_incident.json',
     {'id': 'incident_id'})
])
def test_incident_do_commands(requests_mock,
                              action,
                              command_args,
                              command_api_url,
                              mock_response_file,
                              override_node):
    """Unit test
    Given
        - action
        - command args
    When
        - running incident_do_command with the action
    Then
        - validate the correct request was called.
        - validate the entry context.
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=True
    )
    mock_topdesk_node = util_load_json(mock_response_file)
    response_incident = mock_topdesk_node.copy()
    if override_node.get('id', None):
        response_incident['id'] = override_node['id']
    elif override_node.get('number', None):
        response_incident['number'] = override_node['number']

    requests_mock.put(
        command_api_url, json=response_incident)

    command_results = incident_do_command(client=client,
                                          args=command_args,
                                          action=action)
    assert requests_mock.called
    if command_args.get(f"{action}_reason_id", None):
        assert requests_mock.last_request.json() == {'id': command_args.get(f"{action}_reason_id", None)}
    else:
        assert requests_mock.last_request.json() == {}

    assert command_results.outputs_prefix == f'{INTEGRATION_NAME}.incident'
    assert command_results.outputs_key_field == 'id'
    assert command_results.outputs == [response_incident]


@pytest.mark.parametrize('command_args, command_api_url, command_api_body', [
    ({"id": "incident_id", "file": "some_entry_id", "invisivle_for_caller": "false"},
     'https://test.com/api/v1/incidents/id/incident_id/attachments',
     {"invisivle_for_caller": "false"}),
    ({"id": "incident_id", "file": "some_entry_id", "description": "some description"},
     'https://test.com/api/v1/incidents/id/incident_id/attachments',
     {"description": "some description"}),
    ({"id": "incident_id", "file": "some_entry_id", "description": "some description", "invisivle_for_caller": "false"},
     'https://test.com/api/v1/incidents/id/incident_id/attachments',
     {"description": "some description", "invisivle_for_caller": "false"}),
    ({"id": "incident_id", "file": "some_entry_id"},
     'https://test.com/api/v1/incidents/id/incident_id/attachments',
     {})
])
def test_attachment_upload_command(mocker,
                                   requests_mock,
                                   command_args,
                                   command_api_url,
                                   command_api_body):
    """Unit test
    Given
        - command args
    When
        - running attachment_upload_command
    Then
        - validate the correct request was called.
        - validate the file is in the request.
        - validate the entry context.
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=True
    )

    mock_topdesk_node = util_load_json('test_data/topdesk_attachment.json')
    response_attachment = mock_topdesk_node.copy()

    requests_mock.post(
        command_api_url, json=response_attachment)

    mocker.patch.object(demisto, 'dt', return_value="made_up_file.txt")
    mocker.patch.object(demisto, 'getFilePath', return_value={'path': 'test_data/mock_upload_file.txt'})

    command_results = attachment_upload_command(client=client,
                                                args=command_args)

    assert requests_mock.called
    assert b'mock text file for attachment up' in requests_mock.last_request._request.body
    assert command_results.outputs_prefix == f'{INTEGRATION_NAME}.attachment'
    assert command_results.outputs_key_field == 'id'
    assert command_results.outputs == response_attachment


@pytest.mark.parametrize('create_func, command_args, command_api_url, mock_response_file,'
                         ' expected_last_request_body', [
                             (True,
                              {"caller": "some_caller"},
                              'https://test.com/api/v1/incidents/',
                              'test_data/topdesk_incident.json',
                              {'callerLookup': {'id': 'some_caller'}, 'entryType': {'name': XSOAR_ENTRY_TYPE}}),
                             (True,
                              {"caller": "some_caller", "description": "some_change"},
                              'https://test.com/api/v1/incidents/',
                              'test_data/topdesk_incident.json',
                              {'callerLookup': {'id': 'some_caller'}, 'entryType': {'name': XSOAR_ENTRY_TYPE},
                               'briefDescription': 'some_change'}),
                             (True,
                              {"caller": "some_caller", "description": "some_change", "category": "some_category_id"},
                              'https://test.com/api/v1/incidents/',
                              'test_data/topdesk_incident.json',
                              {'callerLookup': {'id': 'some_caller'}, 'entryType': {'name': XSOAR_ENTRY_TYPE},
                               'briefDescription': 'some_change', 'category': {'name': 'some_category_id'}}),
                             (False,
                              {"caller": "some_caller", "id": "incident_id"},
                              'https://test.com/api/v1/incidents/id/incident_id',
                              'test_data/topdesk_incident.json',
                              {'callerLookup': {'id': 'some_caller'}, 'entryType': {'name': XSOAR_ENTRY_TYPE}}),
                             (False,
                              {"caller": "some_caller", "number": "incident_number"},
                              'https://test.com/api/v1/incidents/number/incident_number',
                              'test_data/topdesk_incident.json',
                              {'callerLookup': {'id': 'some_caller'}, 'entryType': {'name': XSOAR_ENTRY_TYPE}}),
                             (False,
                              {"caller": "some_caller", "number": "incident_number", "description": "some_change"},
                              'https://test.com/api/v1/incidents/number/incident_number',
                              'test_data/topdesk_incident.json',
                              {'callerLookup': {'id': 'some_caller'}, 'entryType': {'name': XSOAR_ENTRY_TYPE},
                               'briefDescription': 'some_change'})
                         ])
def test_caller_lookup_incident_touch_commands(requests_mock,
                                               create_func,
                                               command_args,
                                               command_api_url,
                                               mock_response_file,
                                               expected_last_request_body):
    """Unit test
    Given
        - whether the command is Create or Update
        - command args
    When
        - running the command with a caller as a registered caller.
    Then
        - validate 1 request was called.
        - validate the correct request was called.
        - validate the entry context.
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=True
    )
    client_func = client.update_incident
    request_method = "put"
    action = "updating"
    if create_func:
        client_func = client.create_incident
        request_method = "post"
        action = "creating"
    mock_topdesk_node = util_load_json(mock_response_file)
    response_incident = mock_topdesk_node.copy()
    request_command = getattr(requests_mock, request_method)

    request_command(command_api_url, json=response_incident)

    command_results = incident_touch_command(args=command_args,
                                             client_func=client_func,
                                             action=action)
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == expected_last_request_body
    assert command_results.outputs_prefix == f'{INTEGRATION_NAME}.incident'
    assert command_results.outputs_key_field == 'id'
    assert command_results.outputs == [response_incident]


@pytest.mark.parametrize('create_func, command_args, command_api_url, mock_response_file,'
                         ' expected_last_request_body', [
                             (True,
                              {"caller": "some_caller"},
                              'https://test.com/api/v1/incidents/',
                              'test_data/topdesk_incident.json',
                              {'caller': {'dynamicName': 'some_caller'}, 'entryType': {'name': XSOAR_ENTRY_TYPE}}),
                             (False,
                              {"caller": "some_caller", "id": "incident_id"},
                              'https://test.com/api/v1/incidents/id/incident_id',
                              'test_data/topdesk_incident.json',
                              {'caller': {'dynamicName': 'some_caller'}, 'entryType': {'name': XSOAR_ENTRY_TYPE}}),
                             (False,
                              {"caller": "some_caller", "number": "incident_number"},
                              'https://test.com/api/v1/incidents/number/incident_number',
                              'test_data/topdesk_incident.json',
                              {'caller': {'dynamicName': 'some_caller'}, 'entryType': {'name': XSOAR_ENTRY_TYPE}}),
                         ])
def test_non_registered_caller_incident_touch_commands(requests_mock,
                                                       create_func,
                                                       command_args,
                                                       command_api_url,
                                                       mock_response_file,
                                                       expected_last_request_body):
    """Unit test
    Given
        - whether the command is Create or Update
        - command args
    When
        - running the command with a caller as a non registered caller.
    Then
        - validate 2 requests were called.
        - validate the entry context.
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=True
    )
    client_func = client.update_incident
    request_method = "put"
    action = "updating"
    if create_func:
        client_func = client.create_incident
        request_method = "post"
        action = "creating"
    mock_topdesk_node = util_load_json(mock_response_file)
    response_incident = mock_topdesk_node.copy()
    request_command = getattr(requests_mock, request_method)

    def callback_func(request, context):
        if 'callerLookup' in request.json():
            return {"message": "The value for the field 'callerLookup.id' cannot be parsed."}
        else:
            return response_incident

    request_command(command_api_url, json=callback_func)

    command_results = incident_touch_command(args=command_args,
                                             client_func=client_func,
                                             action=action)
    assert requests_mock.call_count == 2
    assert requests_mock.last_request.json() == expected_last_request_body
    assert command_results.outputs_prefix == f'{INTEGRATION_NAME}.incident'
    assert command_results.outputs_key_field == 'id'
    assert command_results.outputs == [response_incident]


@pytest.mark.parametrize('command, command_args, command_api_request', [
    (branches_command,
     {'page_size': 2},
     ('https://test.com/api/v1/branches?page_size=2', {})),
    (branches_command,
     {'start': 2},
     ('https://test.com/api/v1/branches?start=2', {})),
    (branches_command,
     {'query': 'id==1st-branch-id'},
     ('https://test.com/api/v1/branches?query=id==1st-branch-id', {})),
    (branches_command,
     {'page_size': 2, 'start': 2, 'query': 'id==1st-branch-id'},
     ('https://test.com/api/v1/branches?start=2&page_size=2&query=id==1st-branch-id', {})),
    (branches_command,
     {'page_size': 2, 'query': 'id==1st-branch-id'},
     ('https://test.com/api/v1/branches?page_size=2&query=id==1st-branch-id', {})),
    (list_operators_command,
     {'page_size': 2},
     ('https://test.com/api/v1/operators?page_size=2', {})),
    (list_operators_command,
     {'start': 2},
     ('https://test.com/api/v1/operators?start=2', {})),
    (list_operators_command,
     {'query': 'id==1st-operator-id'},
     ('https://test.com/api/v1/operators?query=id==1st-operator-id', {})),
    (list_operators_command,
     {'page_size': 2, 'start': 2, 'query': 'id==1st-operator-id'},
     ('https://test.com/api/v1/operators?start=2&page_size=2&query=id==1st-operator-id', {})),
    (list_operators_command,
     {'page_size': 2, 'query': 'id==1st-operator-id'},
     ('https://test.com/api/v1/operators?page_size=2&query=id==1st-operator-id', {})),
    (list_persons_command,
     {'page_size': 2},
     ('https://test.com/api/v1/persons?page_size=2', {})),
    (list_persons_command,
     {'start': 2},
     ('https://test.com/api/v1/persons?start=2', {})),
    (list_persons_command,
     {'query': 'id==1st-person-id'},
     ('https://test.com/api/v1/persons?query=id==1st-person-id', {})),
    (list_persons_command,
     {'page_size': 2, 'start': 2, 'query': 'id==1st-person-id'},
     ('https://test.com/api/v1/persons?start=2&page_size=2&query=id==1st-person-id', {})),
    (list_persons_command,
     {'page_size': 2, 'query': 'id==1st-person-id'},
     ('https://test.com/api/v1/persons?page_size=2&query=id==1st-person-id', {})),
    (get_incidents_list_command,
     {'page_size': 2},
     ('https://test.com/api/v1/incidents?page_size=2', {})),
    (get_incidents_list_command,
     {'start': 2},
     ('https://test.com/api/v1/incidents?start=2', {})),
    (get_incidents_list_command,
     {'query': 'id==1st-incident-id'},
     ('https://test.com/api/v1/incidents?query=id==1st-incident-id', {})),
    (get_incidents_list_command,
     {'page_size': 2, 'start': 2, 'query': 'id==1st-incident-id'},
     ('https://test.com/api/v1/incidents?start=2&page_size=2&query=id==1st-incident-id', {})),
    (get_incidents_list_command,
     {'page_size': 2, 'query': 'id==1st-incident-id'},
     ('https://test.com/api/v1/incidents?page_size=2&query=id==1st-incident-id', {})),
    (get_incidents_list_command,
     {'page_size': 2, 'category': 'some_category'},
     ('https://test.com/api/v1/incidents?page_size=2&query=category==some_category', {}))

])
def test_list_command_with_args(requests_mock,
                                command,
                                command_args,
                                command_api_request):
    """Unit test
    Given
        - command args
    When
        - running the command
    Then
        - validate the correct request was called.
        - validate the request body is as expected
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=True
    )
    requests_mock.get(
        command_api_request[0], json=[{}])
    command(client, command_args)

    assert requests_mock.called
    assert requests_mock.last_request.json() == command_api_request[1]


@pytest.mark.parametrize('command_args, command_api_request, call_count', [
    ({'max_fetch': 2,
      'modification_date_start': '2020-02-10T06:32:36Z',
      'modification_date_end': '2020-03-10T06:32:36Z',
      'query': 'id==1st-incident-id'},
     [('https://test.com/api/v1/incidents?page_size=2&query=id==1st-incident-id',
       {'modification_date_start': '2020-02-10T06:32:36Z',
        'modification_date_end': '2020-03-10T06:32:36Z'})], 1),
    ({'max_fetch': 2 * MAX_API_PAGE_SIZE,
      'modification_date_start': '2020-02-10T06:32:36Z',
      'modification_date_end': '2020-03-10T06:32:36Z',
      'query': 'id==1st-incident-id'},
     [(f'https://test.com/api/v1/incidents?page_size={MAX_API_PAGE_SIZE}&query=id==1st-incident-id',
       {'modification_date_start': '2020-02-10T06:32:36Z',
        'modification_date_end': '2020-03-10T06:32:36Z'}),
      (f'https://test.com/api/v1/incidents'
       f'?start={MAX_API_PAGE_SIZE}&page_size={MAX_API_PAGE_SIZE}&query=id==1st-incident-id',
       {'modification_date_start': '2020-02-10T06:32:36Z',
        'modification_date_end': '2020-03-10T06:32:36Z'})], 2)
])
def test_get_incidents_with_pagination(requests_mock,
                                       command_args,
                                       command_api_request,
                                       call_count):
    """Unit test
    Given
        - command args
    When
        - running get_incidents_with_pagination function
    Then
        - validate the correct parameters in the request.
        - validate the number of requests preformed.
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=True
    )
    for request in command_api_request:
        requests_mock.get(
            request[0], json=[{}])
    get_incidents_with_pagination(client=client,
                                  max_fetch=command_args.get('max_fetch', None),
                                  query=command_args.get('query', None),
                                  modification_date_start=command_args.get('modification_date_start', None),
                                  modification_date_end=command_args.get('modification_date_end', None))

    for called_request, mocked_request in zip(requests_mock._adapter.request_history, command_api_request):
        assert called_request._request.url == mocked_request[0]
        assert called_request.json() == mocked_request[1]
    assert requests_mock.call_count == call_count


@pytest.mark.parametrize('command, new_query, command_args, command_api_request', [
    (list_persons_command,
     False,
     {"query": "status==firstLine"},
     'https://test.com/api/v1/persons?query=status==firstLine'),
    (list_operators_command,
     False,
     {"query": "status==firstLine"},
     'https://test.com/api/v1/operators?query=status==firstLine'),
    (branches_command,
     False,
     {"query": "status==firstLine"},
     'https://test.com/api/v1/branches?query=status==firstLine'),
    (get_incidents_list_command,
     False,
     {"query": "status=firstLine"},
     'https://test.com/api/v1/incidents?status=firstLine'),
    (get_incidents_list_command,
     False,
     {"status": "firstLine"},
     'https://test.com/api/v1/incidents?status=firstLine'),
    (get_incidents_list_command,
     False,
     {"query": 'caller_id=some_caller', "status": "firstLine"},
     'https://test.com/api/v1/incidents?caller_id=some_caller&status=firstLine'),
    (get_incidents_list_command,
     False,
     {"query": 'caller_id=some_caller', "status": "firstLine", "branch_id": "some_branch"},
     'https://test.com/api/v1/incidents?caller_id=some_caller&status=firstLine&branch=some_branch'),
    (list_persons_command,
     True,
     {"query": "status==firstLine"},
     'https://test.com/api/v1/persons?query=status==firstLine'),
    (list_operators_command,
     True,
     {"query": "status==firstLine"},
     'https://test.com/api/v1/operators?query=status==firstLine'),
    (branches_command,
     True,
     {"query": "status==firstLine"},
     'https://test.com/api/v1/branches?query=status==firstLine'),
    (get_incidents_list_command,
     True,
     {"query": "status==firstLine"},
     'https://test.com/api/v1/incidents?query=status==firstLine'),
    (get_incidents_list_command,
     True,
     {"status": "firstLine"},
     'https://test.com/api/v1/incidents?query=status==firstLine'),
    (get_incidents_list_command,
     True,
     {"query": 'caller_id==some_caller', "status": "firstLine"},
     'https://test.com/api/v1/incidents?query=caller_id==some_caller&status==firstLine'),
    (get_incidents_list_command,
     True,
     {"query": 'status==firstLine', "caller_id": "some_caller_id", "branch_id": "some_branch"},
     'https://test.com/api/v1/incidents?query=status==firstLine&caller==some_caller_id&branch==some_branch')
])
def test_old_new_query(requests_mock,
                       command,
                       new_query,
                       command_args,
                       command_api_request):
    """Unit test
    Given
        - command args
        - which type of query is supported
    When
        - running the command
    Then
        - validate the correct request url was called.
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=new_query
    )
    requests_mock.get(command_api_request, json=[{}])
    command(client=client, args=command_args)

    assert requests_mock.called


@pytest.mark.parametrize('command_args', [
    ({"category": "blah"}), ({"subcategory": "blah"}), ({"call_type": "blah"}), ({"entry_type": "blah"})
])
def test_unsupported_old_query_param(command_args):
    """Unit test
    Given
        - get_incidents_list_command old query setting unsupported command args
    When
        - running the command with old query setting
    Then
        - validate KeyError is raised.
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=False
    )
    with pytest.raises(KeyError, match="is not supported with old query setting."):
        get_incidents_list_command(client=client, args=command_args)


@pytest.mark.parametrize('topdesk_incidents_override, last_fetch_time, updated_fetch_time', [
    ([{  # Last fetch is before incident creation
        'number': 'TEST-1',
        'creationDate': '2020-02-10T06:32:36Z',
        'will_be_fetched': True
    }], '2020-01-11T06:32:36.303+0000', '2020-02-10T06:32:36Z'),
    ([{  # Last fetch is after one incident creation and before other.
        'number': 'TEST-1',
        'creationDate': '2020-01-10T06:32:36Z',
        'will_be_fetched': False
    }, {
        'number': 'TEST-2',
        'creationDate': '2020-03-10T06:32:36Z',
        'will_be_fetched': True
    }], '2020-02-11T06:32:36.303+0000', '2020-03-10T06:32:36Z'),
    ([{  # Last fetch is at incident creation
        'number': 'TEST-1',
        'creationDate': '2020-02-10T06:32:36.303+0000',
        'will_be_fetched': False
    }], '2020-02-10T06:32:36Z', '2020-02-10T06:32:36Z'),
])
def test_fetch_incidents(requests_mock, topdesk_incidents_override, last_fetch_time, updated_fetch_time):
    """Unit test
    Given
        - fetch incidents args
    When
        - running fetch incidents command
    Then
        - validate The length of the results.
        - validate the entry context.
        - validate last_fetch is updated.
    """
    client = Client(
        base_url='https://test.com/api/v1',
        verify=False,
        headers={
            'Authentication': 'Basic some_encoded_credentials'
        },
        new_query=True
    )
    mock_topdesk_incident = util_load_json('test_data/topdesk_incident.json')
    mock_topdesk_response = []
    expected_incidents = []
    for incident_override in topdesk_incidents_override:
        response_incident = mock_topdesk_incident.copy()
        response_incident['number'] = incident_override['number']
        response_incident['creationDate'] = incident_override['creationDate']
        mock_topdesk_response.append(response_incident)
        if incident_override['will_be_fetched']:
            expected_incidents.append({
                'name': f"TOPdesk incident {incident_override['number']}",
                'details': json.dumps(response_incident),
                'occurred': incident_override['creationDate'],
                'rawJSON': json.dumps(response_incident),
            })

    requests_mock.get(
        'https://test.com/api/v1/incidents', json=mock_topdesk_response)

    last_run = {
        'last_fetch': last_fetch_time
    }
    last_fetch, incidents = fetch_incidents(client=client,
                                            last_run=last_run,
                                            demisto_params={})

    assert len(incidents) == len(expected_incidents)
    for incident, expected_incident in zip(incidents, expected_incidents):
        assert incident['name'] == expected_incident['name']
        assert incident['details'] == expected_incident['details']
        assert incident['occurred'] == expected_incident['occurred']
        assert incident['rawJSON'] == expected_incident['rawJSON']
    assert last_fetch == {'last_fetch': updated_fetch_time}
