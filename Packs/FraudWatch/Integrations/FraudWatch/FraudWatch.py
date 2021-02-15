import pytz
import urllib3
import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401

# disable insecure warnings
urllib3.disable_warnings()

''' CONSTANTS '''
MINIMUM_POSITIVE_VALUE = 1
BASE_URL = 'https://www.phishportal.com/v1/'

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

    def __init__(self, api_key: str, base_url: str, verify: bool, proxy: bool):
        self.api_key = api_key
        self.base_headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        super().__init__(base_url=base_url, verify=verify, proxy=proxy, headers=self.base_headers)

    def http_request(self, method: str, url_suffix: str, params: Optional[Dict] = None, data: Optional[Dict] = None,
                     headers: Optional[Dict] = None, files: Optional[Dict] = None):
        """
        Wrapper for Base Client http request. Uses error handler to catch errors returned by FraudWatch and returning
        an exception with more precise description for the exception
        Args:
            method (str): The HTTP method to perform ('POST', 'GET', 'PUT').
            url_suffix (str): The url suffix of the API call.
            params (Optional[Dict]): Additional query params to be sent.
            data (Optional[Dict]): Additional data to be sent.
            headers (Optional[Dict]): Additional headers to be sent.
            files (Optional[Dict]): Additional files to be sent

        Returns:
            The HTTP response, or exception if exception occurred.
        """
        return self._http_request(
            method=method,
            url_suffix=url_suffix,
            params=params,
            data=data,
            headers=headers,
            files=files,
            error_handler=fraud_watch_error_handler
        )

    def incidents_list(self, brand: Optional[str], status: Optional[str], page: Optional[int],
                       limit: Optional[int], from_date: Optional[str], to_date: Optional[str]):
        params = assign_params(
            brand=brand,
            status=status,
            page=page,
            limit=limit,
            to=to_date
        )

        # This is because 'from' is reserved word so it can't be used as key argument in assign_params.
        if from_date:
            params['from'] = from_date

        return self.http_request(
            method='GET',
            url_suffix='incidents',
            params=params
        )

    def incident_report(self, brand: Optional[str], incident_type: Optional[str],
                        reference_id: Optional[str], primary_url: Optional[str], urls: Optional[List[str]],
                        evidence: Optional[str], instructions: Optional[str]):
        return self.http_request(
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

    def incident_update(self, incident_id: Optional[str], brand: Optional[str], reference_id: Optional[str],
                        evidence: Optional[str], instructions: Optional[str]):
        return self.http_request(
            method='PUT',
            url_suffix=f'incident/{incident_id}',
            data=assign_params(
                brand=brand,
                reference_id=reference_id,
                evidence=evidence,
                instructions=instructions
            ),
            headers={**self.base_headers, **self.URL_ENCODED_HEADER}
        )

    def incident_list_by_id(self, incident_id: Optional[str]):
        return self.http_request(
            method='GET',
            url_suffix=f'incident/{incident_id}'
        )

    def incident_get_by_reference(self, reference_id: Optional[str]):
        return self.http_request(
            method='GET',
            url_suffix=f'incident/reference/{reference_id}'
        )

    def incident_forensic_get(self, incident_id: Optional[str]):
        return self.http_request(
            method='GET',
            url_suffix=f'incident/{incident_id}/forensic'
        )

    def incident_contact_emails_list(self, incident_id: Optional[str], page: Optional[int],
                                     limit: Optional[int]):
        return self.http_request(
            method='GET',
            url_suffix=f'incident/{incident_id}/message',
            params=assign_params(
                page=page,
                limit=limit
            )
        )

    def incident_messages_add(self, incident_id: Optional[str], message_content: Any):
        return self.http_request(
            method='POST',
            url_suffix=f'incident/{incident_id}/message/add',
            data=message_content,
            headers={**self.base_headers, **self.JSON_CONTENT_HEADER}
        )

    def incident_urls_add(self, incident_id: Optional[str], urls: Dict[str, List[str]]):
        return self.http_request(
            method='POST',
            url_suffix=f'incident/{incident_id}/urls/add',
            data=urls,
            headers={**self.base_headers, **self.URL_ENCODED_HEADER}
        )

    def attachment_upload_command(self, incident_id: Optional[str], file: Any):
        return self.http_request(
            method='POST',
            url_suffix=f'incident/{incident_id}/upload',
            files=file
        )

    def brands_list(self, page: Optional[int], limit: Optional[int]):
        return self.http_request(
            method='GET',
            url_suffix='account/brands',
            params=assign_params(
                page=page,
                limit=limit
            )
        )


''' HELPER FUNCTIONS '''


def fraud_watch_error_handler(res: Any):
    """
    FraudWatch error handler for any error occurred during the API request.
    This function job is to translate the known exceptions returned by FraudWatch
    to human readable exception to help the user understand why the request have failed.
    If error returned is not in the expected error format, raises the exception as is.
    Args:
        res (Any): The error response returned by FraudWatch.

    Returns:
        - raises DemistoException.
    """
    err_msg = f'Error in API call [{res.status_code}] - {res.reason}'
    try:
        # Try to parse json error response
        error_entry = res.json()
        message = error_entry.get('message')
        errors = error_entry.get('errors')
        if res.status_code == 403:
            err_msg += '\nMake sure your API token is valid and up-to-date'
        elif not message and not errors:
            err_msg += '\n{}'.format(json.dumps(error_entry))
        else:
            if message and errors:
                fraud_watch_error_reason = f'{message}: {errors}'
            else:
                fraud_watch_error_reason = message if message else errors
            err_msg += f'\n{fraud_watch_error_reason}'
        raise DemistoException(err_msg, res=res)
    except ValueError:
        err_msg += '\n{}'.format(res.text)
        raise DemistoException(err_msg, res=res)


def get_optional_time_parameter_as_fraud_watch_date_format(arg: Optional[str]) -> Optional[str]:
    """
    Receives arg, expects that the time argument will be either:
    - Iso time.
    - Time Range.
    Args:
        arg (str): The argument to turn into FraudWatch date format.

    Returns:
        - (None): If 'arg' is None, returns None.
        - (str): If 'arg' exists and is epoch time or iso time, returns string representing the date format expected
          by FraudWatch service.
        - (Exception): If 'arg' exists and is not time range or iso, throws DemistoException exception.

    """
    maybe_unaware_date = arg_to_datetime(arg, is_utc=True)
    if not maybe_unaware_date:
        return None

    aware_time_date = maybe_unaware_date if maybe_unaware_date.tzinfo else UTC_TIMEZONE.localize(
        maybe_unaware_date)
    return aware_time_date.strftime('%Y-%m-%d')


def get_and_validate_positive_int_argument(args: Dict, argument_name: str) -> Optional[int]:
    """
    Extracts int argument from Demisto arguments.
    If argument exists, validates that:
    - min <= argument's value.

    Args:
        args (Dict): Demisto arguments.
        argument_name (str): The name of the argument to extract.

    Returns:
        - (int): If argument exists and is equal or higher than min, returns argument.
        - (None): If argument does not exist, returns None.
        - (Exception): If argument exists and is lower than min, raises DemistoException.
    """
    argument_value = arg_to_number(args.get(argument_name), arg_name=argument_name)

    if argument_value and argument_value < MINIMUM_POSITIVE_VALUE:
        raise DemistoException(f'{argument_name} should be equal or higher than {MINIMUM_POSITIVE_VALUE}')

    return argument_value


def get_time_parameter(arg: Optional[str], parse_format: bool = False):
    """
    parses arg into date time object with aware time zone if 'arg' exists.
    If no time zone is given, sets timezone to UTC.
    Returns the date time object created or the expected format by FraudWatch.
    Args:
        arg (str): The argument to turn into aware date time.
        parse_format (bool): Should return date or the parsed format of the date.

    Returns:
        - (None) If 'arg' is None, returns None.
        - (datetime): If 'arg' is exists and parse_format is false, returns date time.
        - (str): If 'arg' is exists and parse_format is true, returns the FraudWatch date format of the date time object.
    """
    maybe_unaware_date = arg_to_datetime(arg, is_utc=True)
    if not maybe_unaware_date:
        return None

    aware_time_date = maybe_unaware_date if maybe_unaware_date.tzinfo else UTC_TIMEZONE.localize(
        maybe_unaware_date)

    if parse_format:
        return aware_time_date.strftime('%Y-%m-%d')
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
        (list, dict): A tuple of Incidents that have been fetched, and the new run parameters.
    """
    last_run = demisto.getLastRun()
    brand = params.get('brand')
    status = params.get('status')
    limit = params.get('max_fetch')

    fetch_time_string = params.get('first_fetch', '7 days').strip()
    first_fetch_time = get_time_parameter(fetch_time_string)
    from_date = last_run.get('last_fetch_day', first_fetch_time.strftime(FRAUD_WATCH_DATE_FORMAT))
    to_date = datetime.now(timezone.utc).strftime(FRAUD_WATCH_DATE_FORMAT)
    last_fetch_time = arg_to_datetime(last_run.get('last_fetch_date_time', first_fetch_time.isoformat()))

    raw_response = client.incidents_list(brand=brand, status=status, page=None, limit=limit,
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
    Tests API connectivity and authentication.
    Returning 'ok' indicates that the integration works like it is supposed to.
    Connection to the service is successful.
    Raises exceptions if something goes wrong.

    Args:
        client (Client): FraudWatch client to perform the API call.
        params (Dict): Demisto params.

    Returns:
        (str): 'ok' if test passed, anything else will fail the test.
    """
    try:
        fetch_incidents_command(client, params)
        return 'ok'
    except DemistoException as e:
        if 'Forbidden' in str(e) or 'Authorization' in str(e):
            message = 'Authorization Error: make sure API Key is correctly set'
            e = DemistoException(message)
        raise e


def fraud_watch_incidents_list_command(client: Client, args: Dict) -> CommandResults:
    """
    Gets a list of incidents from FraudWatch service with the possible filters:
    - Brand: Retrieve incidents which corresponds to the given brand. throws Exception if brand does not exist.
    - Status: Retrieve incidents which corresponds to the given status. Unknown status will return empty incident list.
    - Limit: Total number of Incidents in a page. The default limit is 20 and the maximum number is 200.
    - Page: Retrieve incidents by the given page number.
    - From Date: Retrieve alerts that their date opened is higher or equal to 'from' value.
                 Supports ISO and time range (<number> <time unit>, e.g., 12 hours, 7 days) formats.
                 If 'to' argument is not given, default value for 'to' is current day.
    - To Date: Retrieve alerts that their date opened is lower or equal to 'to' value.
               Supports ISO and time range (<number> <time unit>, e.g., 12 hours, 7 days) formats.
               If 'from' argument is not given, default value for 'from' is 12 months before 'to'.

    Known errors that causes error to be returned by FraudWatch service:
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
    page = get_and_validate_positive_int_argument(args, 'page')
    limit = get_and_validate_positive_int_argument(args, 'limit')
    from_date = get_time_parameter(args.get('from'), parse_format=True)
    to_date = get_time_parameter(args.get('to'), parse_format=True)
    if from_date and not to_date:
        to_date = datetime.now(timezone.utc).strftime(FRAUD_WATCH_DATE_FORMAT)

    raw_response = client.incidents_list(brand, status, page, limit, from_date, to_date)
    if raw_response.get('error'):
        raise DemistoException(f'''Error occurred during the call to FraudWatch: {raw_response.get('error')}''')
    outputs = raw_response.get('incidents')

    return CommandResults(
        outputs_prefix='FraudWatch.Incident',
        outputs=outputs,
        outputs_key_field='identifier',
        raw_response=raw_response,
        readable_output=tableToMarkdown('FraudWatch Incidents', outputs, INCIDENT_LIST_MARKDOWN_HEADERS,
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
           left side is the parameter to be sent, right side is the way it will be shown in FraudWatch User Interface.
    - Reference ID: Reference ID to be associated to the reported incident. Should be unique.
                    Reference ID can be used later to retrieve specific incident by its reference id.
    - Primary URL(Required): Primary URL of the reported incident.
    - Urls: Additional urls in addition to primary URL to be associated to the reported incident.
    - Evidence: Evidence to be added (such as logs, etc...) to the reported incident.
    - Instructions: Additional instructions to be added for FraudWatch Security Team.

    Known errors that causes error to be returned by FraudWatch service:
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
    brand = args.get('brand')
    incident_type = args.get('type')
    reference_id = args.get('reference_id')
    primary_url = args.get('primary_url')
    urls = args.get('urls')
    evidence = args.get('evidence')
    instructions = args.get('instructions')

    raw_response = client.incident_report(brand, incident_type, reference_id, primary_url, urls,
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
    - Evidence: Evidence to be added (such as logs, etc...) to the incident.
    - Instructions: Add Additional instructions to be added for FraudWatch Security
                    Team to the incident which corresponds to given incident id.

    At least one of 'Brand', 'Reference ID', 'Evidence', 'Instructions' must be given.

    Known errors that causes error to be returned by FraudWatch service:
    - Unknown incident id.
    - Not given or unknown brand.
    - No data given.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')
    brand = args.get('brand')
    reference_id = args.get('reference_id')
    evidence = args.get('evidence')
    instructions = args.get('instructions')

    if all(argument is None for argument in [brand, reference_id, evidence, instructions]):
        return CommandResults(readable_output=f'### Could not update incident: {incident_id} - No data was given.')

    raw_response = client.incident_update(incident_id, brand, reference_id, evidence, instructions)

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

    Known errors that causes error to be returned by FraudWatch service:
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
        raw_response = client.incident_list_by_id(incident_id)
    else:
        raw_response = client.incident_get_by_reference(reference_id)

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

    Known errors that causes error to be returned by FraudWatch service:
    - Unknown incident id.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')

    raw_response = client.incident_forensic_get(incident_id)
    outputs = remove_empty_elements(raw_response)
    if outputs:
        outputs['identifier'] = incident_id

    return CommandResults(
        outputs_prefix='FraudWatch.IncidentForensicData',
        outputs=outputs,
        outputs_key_field='identifier',
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Incident Forensic Data", outputs,
                                        removeNull=True)
    )


def fraud_watch_incident_contact_emails_list_command(client: Client, args: Dict) -> CommandResults:
    """
    Provides contact emails for the incident which corresponds to the given incident ID:
    - Incident ID (Required): The ID of the incident to have its email contacts data retrieved.
    - Limit: Total number of contact emails in a page. The default limit is 20 and the maximum number is 200.
    - Page: Retrieve contact emails by the given page number.

    Known errors that causes error to be returned by FraudWatch service:
    - Unknown incident id.
    - Page index out of bounds.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')
    page = get_and_validate_positive_int_argument(args, 'page')
    limit = get_and_validate_positive_int_argument(args, 'limit')

    try:
        raw_response = client.incident_contact_emails_list(incident_id, page, limit)
    except DemistoException as e:
        if 'Contact email not found' in str(e):
            page_error_msg = f'''Make sure page index: {page} is within bounds.''' if page else ''
            unknown_incident_msg = f'''Make sure incident id: {incident_id} is correct.'''
            raise DemistoException(
                f'''Error occurred in command 'fraudwatch-incident-contact-emails-list'. {page_error_msg}'''
                f' {unknown_incident_msg}')
        raise e

    outputs = [dict(output, identifier=incident_id) for output in raw_response]

    return CommandResults(
        outputs_prefix='FraudWatch.IncidentContacts',
        outputs=outputs,
        outputs_key_field='noteId',
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Incident Contacts Data", outputs,
                                        ['noteId', 'incident_id', 'subject', 'creator', 'content', 'date'],
                                        removeNull=True)
    )


def fraud_watch_incident_messages_add_command(client: Client, args: Dict):
    """
    Add a new message to be associated to the incident which corresponds to the given incident ID:
    - Incident ID (Required): The ID of the incident to add a message to its email contacts.
    - Message Content (Required): Content of the message.

    Known errors that causes error to be returned by FraudWatch service:
    - Unknown incident id.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')
    message_content = args.get('message_content')

    raw_response = client.incident_messages_add(incident_id, message_content)

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

    Known errors that causes error to be returned by FraudWatch service:
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
        'urls[]': [raw_url for raw_url in raw_urls]
    }

    raw_response = client.incident_urls_add(incident_id, urls)

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

    Known errors that causes error to be returned by FraudWatch service:
    - Unknown incident id.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id')
    entry_id = args.get('entry_id')

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
    raw_response = client.attachment_upload_command(incident_id, files)

    return CommandResults(
        raw_response=raw_response,
        # change to name and not entry ID
        readable_output=f'''### File {file_info['name']} was uploaded successfully to incident: {incident_id}'''
    )


def fraud_watch_brands_list_command(client: Client, args: Dict) -> CommandResults:
    """
    Gets a list of brands from FraudWatch service:
    - Limit: Total number of brands in a page. The default limit is 20, minimum number is also 20
             and the maximum number is 100.
    - Page: Retrieve brands by the given page number.

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    page = get_and_validate_positive_int_argument(args, 'page')
    limit = get_and_validate_positive_int_argument(args, 'limit')
    raw_response = client.brands_list(page, limit)

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
            return_results(test_module(client, params))

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
