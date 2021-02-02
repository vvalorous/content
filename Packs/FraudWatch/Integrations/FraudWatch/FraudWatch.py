import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401
from copy import deepcopy

import pytz

''' CONSTANTS '''
MINIMUM_PAGE_VALUE = 0
MINIMUM_LIMIT_INCIDENTS_VALUE = 1
MINIMUM_LIMIT_BRANDS_VALUE = 20
BASE_URL = 'http://www.phishportal.com/v1/'

FRAUD_WATCH_DATE_FORMAT = '%Y-%m-%d'

INCIDENT_LIST_MARKDOWN_HEADERS = ['identifier', 'reference_id', 'url', 'status', 'type', 'brand', 'client',
                                  'content_ip', 'host', 'host_country', 'host_timezone', 'created_by', 'discovered_by',
                                  'current_duration', 'active_duration', 'date_opened', 'date_closed',
                                  'additional_urls', 'link']

UTC_TIMEZONE = pytz.timezone('utc')
''' CLIENT CLASS '''


class Client(BaseClient):
    URL_ENCODED_HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}
    JSON_CONTENT_HEADER = {'Content-Type': 'application/json'}
    MULTIPART_DATA_HEADER = {'Content-Type': 'multipart/form-data'}

    def __init__(self, api_key: str, base_url: str, verify: bool, proxy: bool):
        self.api_key = api_key
        # bearer_token = self.get_bearer_token()
        self.base_headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        super().__init__(base_url=base_url, verify=verify, proxy=proxy, headers=self.base_headers)

    # def get_bearer_token(self):
    #     """
    #     Login using the credentials and store the cookie
    #     """
    #     integration_context = demisto.getIntegrationContext()
    #     bearer_token = integration_context.get('bearer_token', self.api_key)
    #     valid_until = get_time_parameter(integration_context.get('valid_until'))
    #     utc_time_now = datetime.now(timezone.utc)
    #
    #     if bearer_token and valid_until:
    #         if utc_time_now < valid_until:
    #             # Bearer Token is still valid - did not expire yet
    #             return bearer_token
    #
    #     response = self._http_request(method='POST', url_suffix='token/refresh')
    #     bearer_token = response.get('token')
    #     expiration_time = response.get('expiry')
    #
    #     new_integration_context = {
    #         'bearer_token': bearer_token,
    #         'valid_until': expiration_time
    #     }
    #     demisto.setIntegrationContext(new_integration_context)
    #
    #     return bearer_token

    def fraud_watch_incidents_list(self, brand: Optional[str], status: Optional[str], page: Optional[int],
                                   limit: Optional[int], from_date: Optional[str], to_date: Optional[str]):
        params = assign_params(
            brand=brand,
            status=status,
            page=page,
            limit=limit
        )

        # This is because 'to' and 'from' are reserved words so they can't be used as key argument in assign_params
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date

        return self._http_request(
            method='GET',
            url_suffix='incidents',
            params=params
        )

    def fraud_watch_incident_report(self, brand: str, incident_type: Optional[str], reference_id: Optional[str],
                                    primary_url: str, urls: Optional[List[str]], evidence: Optional[str],
                                    instructions: Optional[str]):
        return self._http_request(
            method='POST',
            url_suffix='incidents',
            data=assign_params(
                brand=brand,
                type=incident_type,
                reference_id=reference_id,
                primary_url=primary_url,
                urls=urls,
                evidence=evidence,
                instructions=instructions
            ),
            headers={**self.base_headers, **self.URL_ENCODED_HEADER}
        )

    def fraud_watch_incident_update(self, incident_id: str, brand: Optional[str], reference_id: Optional[str],
                                    instructions: Optional[str]):
        return self._http_request(
            method='PUT',
            url_suffix=f'incident/{incident_id}',
            data=assign_params(
                brand=brand,
                reference_id=reference_id,
                instructions=instructions
            ),
            headers={**self.base_headers, **self.URL_ENCODED_HEADER}
        )

    def fraud_watch_incident_list_by_id(self, incident_id: Optional[str]):
        return self._http_request(
            method='GET',
            url_suffix=f'incident/{incident_id}'
        )

    def fraud_watch_incident_get_by_reference(self, reference_id: Optional[str]):
        return self._http_request(
            method='GET',
            url_suffix=f'incident/reference/{reference_id}'
        )

    def fraud_watch_incident_forensic_get(self, incident_id: Optional[str]):
        return self._http_request(
            method='GET',
            url_suffix=f'incident/{incident_id}/forensic'
        )

    def fraud_watch_incident_contact_emails_list(self, incident_id: Optional[str], page: Optional[int], limit: Optional[int]):
        return self._http_request(
            method='GET',
            url_suffix=f'incident/{incident_id}/message',
            params=assign_params(
                page=page,
                limit=limit
            )
        )

    def fraud_watch_incident_messages_add(self, incident_id: Optional[str], message_content: Any):
        return self._http_request(
            method='POST',
            url_suffix=f'incident/{incident_id}/message/add',
            data=message_content,
            headers={**self.base_headers, **self.JSON_CONTENT_HEADER}
        )

    def fraud_watch_incident_urls_add(self, incident_id: Optional[str], urls: Dict[str, List[str]]):
        return self._http_request(
            method='POST',
            url_suffix=f'incident/{incident_id}/urls/add',
            data=urls,
            headers={**self.base_headers, **self.URL_ENCODED_HEADER}
        )

    def fraud_watch_attachment_upload_command(self, incident_id: Optional[str], file: Any):
        return self._http_request(
            method='POST',
            url_suffix=f'incident/{incident_id}/upload',
            files=file
        )

    def fraud_watch_brands_list(self, page: Optional[int], limit: Optional[int]):
        return self._http_request(
            method='GET',
            url_suffix='account/brands',
            params=assign_params(
                page=page,
                limit=limit
            )
        )


''' HELPER FUNCTIONS '''


def get_and_validate_int_argument(args: Dict, argument_name: str, minimum: int) -> Optional[int]:
    """
    Extracts int argument from Demisto arguments, and in case argument exists,
    validates that:
    - min <= argument.

    Args:
        args (Dict): Demisto arguments.
        argument_name (str): The name of the argument to extract.
        minimum (int): the minimum value the argument can have.

    Returns:
        - If argument exists and is equal or higher than min, returns argument.
        - If argument exists and is lower than min, raises DemistoException.
    """
    argument_value = arg_to_number(args.get(argument_name), arg_name=argument_name)

    if argument_value is None:
        return None

    if not minimum <= argument_value:
        raise DemistoException(f'{argument_name} should be equal or higher than {minimum}')

    return argument_value


def get_time_parameter(arg: Optional[str]):
    """
    Returns date time object with aware time zone if 'arg' exists.
    If no time zone is given, sets timezone to UTC.
    Args:
        arg (str): The argument to turn into aware date time.

    Returns:
        - If 'arg' is None, returns None.
        - If 'arg' is exists returns date time.
    """
    maybe_unaware_date = arg_to_datetime(arg, is_utc=True)
    if not maybe_unaware_date:
        return None

    aware_time_date = maybe_unaware_date if maybe_unaware_date.tzinfo else UTC_TIMEZONE.localize(
        maybe_unaware_date)
    return aware_time_date


''' COMMAND FUNCTIONS '''


def fetch_incidents_command(client: Client, params: Dict):
    """
    Retrieves new incidents from FraudWatch.
    Uses Demisto last run parameters in the following way:
    - 'last_fetch_day' - The latest day fetching was done. Used in 'from_date' to the API call
       to fetch only incidents from the relevant day and forward, as any date before 'last_fetch_day'
       have already been fetched or skipped intentionally and there is no need to fetch incidents
       before 'last_fetch_day'.
    - 'last_fetch_date_time' - The latest time fetching was done. Because FraudWatch API 'from_date' is accurate
       per day, and fetching incidents usually happens more than once a day, this is needed to make sure that
       same incident is not fetched more than once.

    Args:
        client (Client): FraudWatch client to perform API call to fetch incidents.
        params (Dict): Demisto params.

    Returns:
        A tuple of Incidents that have been fetched, and the new run parameters.
    """
    last_run = demisto.getLastRun()
    brand = params.get('brand')
    status = params.get('status')
    limit = params.get('max_fetch')

    a = datetime.now(timezone.utc)
    b = a.isoformat()
    c = arg_to_datetime(b)
    d = a == c

    fetch_time_string = params.get('first_fetch', '5 days').strip()
    first_fetch_time = get_time_parameter(fetch_time_string)
    from_date = last_run.get('last_fetch_day', first_fetch_time.strftime(FRAUD_WATCH_DATE_FORMAT))
    to_date = datetime.now(timezone.utc).strftime(FRAUD_WATCH_DATE_FORMAT)
    last_fetch_time = arg_to_datetime(last_run.get('last_fetch_date_time', first_fetch_time.isoformat()))

    raw_response = client.fraud_watch_incidents_list(brand=brand, status=status, page=None, limit=limit,
                                                     from_date=from_date, to_date=to_date)

    if raw_response.get('error'):
        raise DemistoException(f'''Error occurred during the call to FraudWatch: {raw_response.get('error')}''')

    incidents = raw_response.get('incidents')

    incidents_obj_list: List[Dict[str, Any]] = []
    for incident in incidents:
        try:
            incident_date_opened = get_time_parameter(incident.get('date_opened'))
            if incident_date_opened < last_fetch_time:
                continue
        except Exception as e:
            raise e

        incident_obj = {
            'name': f'''{incident.get('brand')}:{incident.get('identifier')}''',
            'type': 'FraudWatch Incident',
            'occurred': incident.get('date_opened'),
            'rawJSON': json.dumps(incident)
        }

        incidents_obj_list.append(incident_obj)

    current_time = datetime.now(timezone.utc)
    return incidents_obj_list, {
        'last_fetch_day': current_time.strftime(FRAUD_WATCH_DATE_FORMAT),
        'last_fetch_date_time': current_time.isoformat()
    }


def test_module(client: Client, params: Dict) -> str:
    """
    Tests API connectivity and authentication'

    Returning 'ok' indicates that the integration works like it is supposed to.
    Connection to the service is successful.
    Raises exceptions if something goes wrong.

    Args:
        client (Client): FraudWatch client to perform the API call.
        params (Dict): Demisto params.

    Returns:
        'ok' if test passed, anything else will fail the test.
    """
    message = 'ok'
    try:
        fetch_incidents_command(client, params)
    except DemistoException as e:
        if 'Forbidden' in str(e) or 'Authorization' in str(e):  # TODO CAPTURE ERRORS
            message = 'Authorization Error: make sure API Key is correctly set'
        else:
            raise e
    return message


def fraud_watch_incidents_list_command(client: Client, args: Dict) -> CommandResults:
    """
    Gets a list of incidents from FraudWatch service with the possible filters:
    - Brand: Retrieve incidents which corresponds to the given brand. throws Exception if brand does not exist.
    - Status: Retrieve incidents which corresponds to the given status. Unknown status will return empty incident list.
    - Limit: Total number of Incidents in a page. The default limit is 20 and the maximum number is 200.
    - Page: Retrieve incidents by the given page number.
    - From Date: Retrieve only alerts that their date_opened is higher than 'From Date' value. has format of yyyy-mm-dd.
        - If 'To Date' argument is not given, and 'From Date' was given, we set 'To Date' to current time.
    - To Date: Retrieve only alerts that their date_opened is lower than 'To Date' value. has format of yyyy-mm-dd.
        - If 'From Date' argument is not given, and 'To Date' was given, 'From Date' default to 12 months before
          'To Date' by FraudWatch service.

    Known possible errors that could cause error to be returned by FraudWatch service:
    - Unknown brand.
    - Invalid 'to_date' or 'from_date' values.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    brand = args.get('brand')
    status = args.get('status')
    page = get_and_validate_int_argument(args, 'page', minimum=MINIMUM_PAGE_VALUE)
    limit = get_and_validate_int_argument(args, 'limit', minimum=MINIMUM_LIMIT_INCIDENTS_VALUE)
    from_date = args.get('from')
    to_date = args.get('to')
    if from_date and not to_date:
        to_date = datetime.now(timezone.utc).strftime(FRAUD_WATCH_DATE_FORMAT)

    raw_response = client.fraud_watch_incidents_list(brand, status, page, limit, from_date, to_date)
    if raw_response.get('error'):
        raise DemistoException(f'''Error occurred during the call to FraudWatch: {raw_response.get('error')}''')
    outputs = raw_response.get('incidents')

    return CommandResults(
        outputs_prefix='FraudWatch.Incident',
        outputs=outputs,
        outputs_key_field='identifier',
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Incidents", outputs, INCIDENT_LIST_MARKDOWN_HEADERS,
                                        removeNull=True)
    )


def fraud_watch_incident_report_command(client: Client, args: Dict) -> CommandResults:
    """
    Report an incident to FraudWatch service:
    - Brand(Required): The brand associated to the reported incident.
    - Incident Type(Required): The type of the incident to be associated to the reported incident.
         - possible values: ['phishing' => Phishing,
                           'vishing' => Vishing,
                           'brand_abuse' => Brand Abuse,
                           'malware' => Malware,
                           'social_media_brand_abuse' => Social Media,
                           'mobile_app_unauthorized' => Mobile App,
                           'pac_file' => PAC File,
                           'pharming' => Pharming,
                           'messaging' => Messaging,
                           'dmarc_email_server' => DMARC]
           left side is the parameter to be sent, right side is the way it will be shown in FraudWatch service.
    - Reference ID: Reference ID to be associated to the reported incident. Should be unique.
                    Reference ID can be used later to retrieve specific incident by its reference id.
    - Primary URL(Required): Primary URL of the reported incident.
    - Urls: Additional urls to be added to the reported incident.
    - Evidence: Evidence to be added (such as logs, etc...) to the reported incident.
    - Instructions: Additional instructions to be added for FraudWatch Security Team.

    Known possible errors that could cause error to be returned by FraudWatch service:
    - Not given or unknown brand.
    - Not given or unknown incident type.
    - Not given primary url.
    - No data given.
    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    brand = args.get('brand', 'Brand not found')
    incident_type = args.get('type', 'Type not found')
    reference_id = args.get('reference_id')
    primary_url = args.get('primary_url', '')
    urls = args.get('urls')
    evidence = args.get('evidence')
    instructions = args.get('instructions')

    raw_response = client.fraud_watch_incident_report(brand, incident_type, reference_id, primary_url, urls,
                                                      evidence, instructions)

    return CommandResults(
        outputs_prefix='FraudWatch.Incident',
        outputs=raw_response,
        outputs_key_field='identifier',
        raw_response=raw_response,
        readable_output=tableToMarkdown("Created FraudWatch Incident", raw_response, removeNull=True)
    )


def fraud_watch_incident_update_command(client: Client, args: Dict) -> CommandResults:
    """
    Updates the incident ID corresponding to the given incident_id with given arguments values:
    - Incident ID(Required): The ID of the incident to be updated.
    - Brand: Updates this to be the brand associated to the incident which corresponds to given incident id.
    - Reference ID: Reference ID to be associated to the incident which corresponds to given incident id.
                    Should be unique. Reference ID can be used later to retrieve specific incident by its reference id.
    - Instructions: Add Additional instructions to be added for FraudWatch Security
                    Team to the incident which corresponds to given incident id.

    At least one of 'Brand', 'Reference ID', 'Instructions' must be given.

    Known possible errors that could cause error to be returned by FraudWatch service:
    - Unknown incident id.
    - Not given or unknown brand.
    - No data given.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id', 'Incident ID is missing')
    brand = args.get('brand')
    reference_id = args.get('reference_id')
    instructions = args.get('instructions')

    if all(argument is None for argument in [brand, reference_id, instructions]):
        raise DemistoException(f'No data was given to update for incident id: ({incident_id})')

    raw_response = client.fraud_watch_incident_update(incident_id, brand, reference_id, instructions)

    return CommandResults(
        raw_response=raw_response,
        readable_output=f'### Incident with ID {incident_id} was updated successfully'
    )


def fraud_watch_incident_get_by_identifier_command(client: Client, args: Dict) -> CommandResults:
    """
    Gets an incident from FraudWatch service by its reference ID or incident ID:
    - Incident ID: The ID of the incident to be retrieved.
    - Reference ID: Reference id of the incident to be retrieved.
                    In case more than one incident has the corresponding reference id, FraudWatch service
                    returns the incident with the latest 'date_opened' field.

    Exactly one of 'Incident ID', 'Reference ID' should be given, else DemistoException will be raised.

    Known possible errors that could cause error to be returned by FraudWatch service:
    - Unknown incident id.
    - Unknown reference_id id.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')
    reference_id = args.get('reference_id')

    if (incident_id and reference_id) or (not incident_id and not reference_id):
        raise DemistoException('Exactly one of reference id or incident id must be given.')

    if incident_id:
        raw_response = client.fraud_watch_incident_list_by_id(incident_id)
    else:
        raw_response = client.fraud_watch_incident_get_by_reference(reference_id)

    return CommandResults(
        outputs_prefix='FraudWatch.Incident',
        outputs=raw_response,
        outputs_key_field='identifier',
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Incident", raw_response, removeNull=True)
    )


def fraud_watch_incident_forensic_get_command(client: Client, args: Dict) -> CommandResults:
    """
    Gets forensic data of an incident which corresponds to the given incident ID:
    - Incident ID (Required): The ID of the incident to have its forensic data retrieved.

    Known possible errors that could cause error to be returned by FraudWatch service:
    - Unknown incident id.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')

    raw_response = client.fraud_watch_incident_forensic_get(incident_id)

    outputs = deepcopy(raw_response)
    outputs['identifier'] = incident_id

    if remove_empty_elements(raw_response):
        human_readable = tableToMarkdown("FraudWatch Incident Forensic Data", remove_empty_elements(outputs),
                                         removeNull=True)
    else:
        human_readable = f'### Incident id {incident_id} has empty forensic data'

    return CommandResults(
        outputs_prefix='FraudWatch.IncidentForensicData',
        outputs=outputs,
        outputs_key_field='identifier',
        raw_response=raw_response,
        readable_output=human_readable
    )


def fraud_watch_incident_contact_emails_list_command(client: Client, args: Dict) -> CommandResults:
    """
    Provides contact emails for the incident which corresponds to the given incident ID:
    - Incident ID (Required): The ID of the incident to have its email contacts data retrieved.
    - Limit: Total number of contact emails in a page. The default limit is 20 and the maximum number is 200.
    - Page: Retrieve contact emails by the given page number.

    Known possible errors that could cause error to be returned by FraudWatch service:
    - Unknown incident id.
    - Page index out of bounds

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')
    page = get_and_validate_int_argument(args, 'page', minimum=MINIMUM_PAGE_VALUE)
    limit = get_and_validate_int_argument(args, 'limit', minimum=MINIMUM_LIMIT_INCIDENTS_VALUE)

    try:
        raw_response = client.fraud_watch_incident_contact_emails_list(incident_id, page, limit)
    except DemistoException as e:
        if 'Error occurred. Make sure arguments are correct' in str(e):
            page_error_msg = f'''Make sure page index: ({page}) is within bounds.''' if page else ''
            unknown_incident_msg = f'''Make sure incident id: ({incident_id}) is correct.'''
            raise DemistoException(f'''Error occurred. {page_error_msg} {unknown_incident_msg}''')
        raise e

    return CommandResults(
        outputs_prefix='FraudWatch.IncidentContacts',
        outputs=raw_response,
        outputs_key_field='noteId',
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Incident Contacts Data", raw_response,
                                        ['noteId', 'subject', 'creator', 'content', 'date'], removeNull=True)
    )


def fraud_watch_incident_messages_add_command(client: Client, args: Dict):
    """
    Add a new message to be associated to the incident which corresponds to the given incident ID:
    - Incident ID (Required): The ID of the incident to add a message to its email contacts.
    - Message Content (Required): Content of the message.

    Known possible errors that could cause error to be returned by FraudWatch service:
    - Unknown incident id.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')
    message_content = args.get('message_content')

    raw_response = client.fraud_watch_incident_messages_add(incident_id, message_content)

    human_readable = f'### Message for incident id {incident_id} was added successfully.'

    return CommandResults(
        raw_response=raw_response,
        readable_output=human_readable
    )


def fraud_watch_incident_urls_add_command(client: Client, args: Dict) -> CommandResults:
    """
    Adds additional urls to the incident which corresponds to the given incident ID:
    - Incident ID (Required): The ID of the incident to add additional urls to.
    - Urls: Additional urls to be added to the incident that matches 'Incident ID'.

    Known possible errors that could cause error to be returned by FraudWatch service:
    - Unknown incident id.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')
    raw_urls = argToList(args.get('urls'))

    urls: Dict[str, List[str]] = {
        'urls[]': []
    }
    for raw_url in raw_urls:
        urls['urls[]'].append(raw_url)

    raw_response = client.fraud_watch_incident_urls_add(incident_id, urls)

    return CommandResults(
        outputs_prefix='FraudWatch.IncidentUrls',
        outputs=raw_response,
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Incident Urls", raw_response, removeNull=True)
    )


def fraud_watch_attachment_upload_command(client: Client, args: Dict):
    """
    Adds a new file attachment to the incident which corresponds to the given incident ID.
    - Incident ID (Required): The ID of the incident to add additional urls to.
    - File Attachment: Entry id of the attachment to be added to the incident which corresponds to Incident ID.

    Known possible errors that could cause error to be returned by FraudWatch service:
    - Unknown incident id.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')
    entry_id = args.get('attachment')

    try:
        # entry id of uploaded file to war room
        file_info = demisto.getFilePath(entry_id)
        file = open(file_info['path'], 'rb')
    except Exception:
        raise DemistoException(F"Entry {entry_id} does not contain a file.")

    files = [
        ('incident_attachment',
         (file_info['name'], file))
    ]
    raw_response = client.fraud_watch_attachment_upload_command(incident_id, files)

    return CommandResults(
        raw_response=raw_response,
        readable_output=f'### File entry {entry_id} was uploaded successfully to incident with incident id '
                        f'{incident_id}'
    )


def fraud_watch_brands_list_command(client: Client, args: Dict) -> CommandResults:
    """
    Gets a list of brands from FraudWatch service:
    - Limit: Total number of brands in a page. The default limit is 20 and the maximum number is 100.
    - Page: Retrieve brands by the given page number.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    page = get_and_validate_int_argument(args, 'page', minimum=MINIMUM_PAGE_VALUE)
    limit = get_and_validate_int_argument(args, 'limit', minimum=MINIMUM_LIMIT_BRANDS_VALUE)
    raw_response = client.fraud_watch_brands_list(page, limit)

    outputs = raw_response.get('brands')

    return CommandResults(
        outputs_prefix='FraudWatch.Brand',
        outputs=outputs,
        outputs_key_field='name',
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Brands", outputs, ['name', 'active', 'client'], removeNull=True)
    )


''' MAIN FUNCTION '''


def main() -> None:
    """
        Main function, parses params and runs command functions.
    """
    command = demisto.command()
    params = demisto.params()
    args = demisto.args()

    verify_certificate = not params.get('insecure', False)
    proxy = params.get('proxy', False)
    api_key = params.get('api_key')

    demisto.debug(f'Command being called is {command}')
    try:

        client = Client(
            api_key=api_key,
            base_url=BASE_URL,
            verify=verify_certificate,
            proxy=proxy)

        if command == 'test-module':
            result = test_module(client, params)
            return_results(result)

        elif command == 'fetch-incidents':
            incidents, next_run = fetch_incidents_command(client, params)
            demisto.setLastRun(next_run)
            demisto.incidents(incidents)

        elif command == 'fraudwatch-incidents-list':
            return_results(fraud_watch_incidents_list_command(client, args))

        elif command == 'fraudwatch-incident-report':
            return_results(fraud_watch_incident_report_command(client, args))

        elif command == 'fraudwatch-incident-update':
            return_results(fraud_watch_incident_update_command(client, args))

        elif command == 'fraudwatch-incident-get-by-identifier':
            return_results(fraud_watch_incident_get_by_identifier_command(client, args))

        elif command == 'fraudwatch-incident-forensic-get':
            return_results(fraud_watch_incident_forensic_get_command(client, args))

        elif command == 'fraudwatch-incident-contact-emails-list':
            return_results(fraud_watch_incident_contact_emails_list_command(client, args))

        elif command == 'fraudwatch-incident-messages-add':
            return_results(fraud_watch_incident_messages_add_command(client, args))

        elif command == 'fraudwatch-incident-urls-add':
            return_results(fraud_watch_incident_urls_add_command(client, args))

        elif command == 'fraudwatch-incident-attachment-upload':
            return_results(fraud_watch_attachment_upload_command(client, args))

        elif command == 'fraudwatch-brands-list':
            return_results(fraud_watch_brands_list_command(client, args))

        else:
            raise NotImplementedError(f'Command {command} is not implemented.')

    # Log exceptions and return errors
    except Exception as e:
        demisto.error(traceback.format_exc())  # print the traceback
        return_error(f'Failed to execute {demisto.command()} command.\nError:\n{str(e)}')


''' ENTRY POINT '''

if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
