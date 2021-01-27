from copy import deepcopy

from CommonServerPython import *  # noqa # pylint: disable=unused-wildcard-import
from CommonServerUserPython import *  # noqa

''' CONSTANTS '''
MINIMUM_PAGE_VALUE = 0
MINIMUM_LIMIT_INCIDENTS_VALUE = 1
MINIMUM_LIMIT_BRANDS_VALUE = 20
BASE_URL = 'https://www.phishportal.com/v1/'
''' CLIENT CLASS '''


class Client(BaseClient):
    URL_ENCODED_HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}
    JSON_CONTENT_HEADER = {'Content-Type': 'application/json'}
    MULTIPART_DATA_HEADER = {'Content-Type: multipart/form-data'}

    def __init__(self, api_key: str, base_url: str, verify: bool, proxy: bool):
        super().__init__(base_url=base_url, verify=verify, proxy=proxy)
        self.api_key = api_key
        bearer_token = self.get_bearer_token()
        self.base_headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Accept': 'application/json'
        }

    def get_bearer_token(self):
        """
        Login using the credentials and store the cookie
        """
        integration_context = demisto.getIntegrationContext()
        bearer_token = integration_context.get('bearer_token', self.api_key)
        valid_until = integration_context.get('valid_until')
        utc_time_now = datetime.utcnow()
        if bearer_token and valid_until:
            date_valid_until = datetime.fromisoformat(valid_until)
            if utc_time_now < date_valid_until:
                # Bearer Token is still valid - did not expire yet
                return bearer_token
        response = self.refresh_token_request()
        bearer_token = response.get('token')
        expiration_time = response.get('expiry')
        if not bearer_token or not expiration_time:
            raise DemistoException(
                f'Unexpected response returned by FraudWatch when trying to refresh token: {response}')
        integration_context = {
            'bearer_token': bearer_token,
            'valid_until': expiration_time
        }
        demisto.setIntegrationContext(integration_context)
        return bearer_token

    def refresh_token_request(self):
        return self._http_request(
            method='POST',
            url_suffix='token/refresh',
            headers=self.base_headers
        )

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
            params=params,
            headers=self.base_headers
        )

    def fraud_watch_incident_list_by_id(self, incident_id: str):
        return self._http_request(
            method='GET',
            url_suffix=f'incident/{incident_id}',
            headers=self.base_headers
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

    def fraud_watch_incident_get_by_reference(self, reference_id: str):
        return self._http_request(
            method='GET',
            url_suffix=f'incident/reference/{reference_id}',
            headers=self.base_headers
        )

    def fraud_watch_incident_forensic_get(self, incident_id: str):
        return self._http_request(
            method='GET',
            url_suffix=f'incident/{incident_id}/forensic',
            headers=self.base_headers
        )

    def fraud_watch_incident_contact_emails_list(self, incident_id: str, page: Optional[int], limit: Optional[int]):
        return self._http_request(
            method='GET',
            url_suffix=f'incident/{incident_id}/message',
            params=assign_params(
                page=page,
                limit=limit
            ),
            headers=self.base_headers
        )

    def fraud_watch_incident_messages_add(self, incident_id: str, message_content: Dict):
        return self._http_request(
            method='POST',
            url_suffix=f'incident/{incident_id}/message/add',
            data=message_content,
            headers={**self.base_headers, **self.JSON_CONTENT_HEADER}
        )

    def fraud_watch_incident_urls_add(self, incident_id: str, urls: Dict[str, List[str]]):
        return self._http_request(
            method='POST',
            url_suffix=f'incident/{incident_id}/urls/add',
            data=urls,
            headers={**self.base_headers, **self.URL_ENCODED_HEADER}
        )

    def fraud_watch_attachment_upload_command(self, incident_id: str, attachment: Any):
        return self._http_request(
            method='POST',
            url_suffix=f'incident/{incident_id}/upload',
            data=attachment,
            headers={**self.base_headers, **self.MULTIPART_DATA_HEADER}
        )

    def fraud_watch_brands_list(self, page: Optional[int], limit: Optional[int]):
        return self._http_request(
            method='GET',
            url_suffix='account/brands',
            params=assign_params(
                page=page,
                limit=limit
            ),
            headers=self.base_headers
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


''' COMMAND FUNCTIONS '''


def test_module(client: Client) -> str:
    """
    Tests API connectivity and authentication'

    Returning 'ok' indicates that the integration works like it is supposed to.
    Connection to the service is successful.
    Raises exceptions if something goes wrong.

    Args:
        client (Client):

    Returns:
        'ok' if test passed, anything else will fail the test.
    """
    try:
        message = 'ok'
    except DemistoException as e:
        if 'Forbidden' in str(e) or 'Authorization' in str(e):  # TODO: make sure you capture authentication errors
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

    raw_response = client.fraud_watch_incidents_list(brand, status, page, limit, from_date, to_date)
    if raw_response.get('error'):
        raise DemistoException(f'''Error occurred during the call to FraudWatch: {raw_response.get('error')}''')
    outputs = raw_response.get('incidents')
    if outputs is None:
        raise DemistoException(f'Unexpected response returned by FraudWatch: {raw_response}')

    return CommandResults(
        outputs_prefix='FraudWatch.Incident',
        outputs=outputs,
        outputs_key_field='identifier',
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Incidents", outputs, removeNull=True)
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
    urls = argToList(args.get('urls', 'Incident ID is missing'))
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

    if not brand and not reference_id and not instructions:
        raise DemistoException(f'No data was given to update for incident id: ({incident_id})')

    try:
        raw_response = client.fraud_watch_incident_update(incident_id, brand, reference_id, instructions)
    except DemistoException as e:
        if 'Not Found' in str(e):
            raise DemistoException(f'Page not found. Make sure incident id: ({incident_id}) is correct')
        raise e

    if 'Updated sucessfully' not in raw_response:
        raise DemistoException(f'Unexpected response returned by FraudWatch: {raw_response}')

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
    incident_id = args.get('incident_id', '')
    reference_id = args.get('reference_id', '')

    if (incident_id and reference_id) or (not incident_id and not reference_id):
        raise DemistoException('Exactly one of reference id or incident id must be given.')

    if incident_id:
        try:
            raw_response = client.fraud_watch_incident_list_by_id(incident_id)
        except DemistoException as e:
            if 'Not Found' in str(e):
                raise DemistoException(f'Page not found. Make sure incident id: ({incident_id}) is correct')
            raise e
    else:
        try:
            raw_response = client.fraud_watch_incident_get_by_reference(reference_id)
        except DemistoException as e:
            if 'Not Found' in str(e):
                raise DemistoException(f'Page not found. Make sure reference id {reference_id} is correct')
            raise e

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
    incident_id = args.get('incident_id', 'Incident ID is missing')

    try:
        raw_response = client.fraud_watch_incident_forensic_get(incident_id)
    except DemistoException as e:
        if 'Not Found' in str(e):
            raise DemistoException(f'Error occurred. Make sure incident id: ({incident_id}) is correct')
        raise e

    outputs = deepcopy(raw_response)
    outputs['identifier'] = incident_id

    return CommandResults(
        outputs_prefix='FraudWatch.IncidentForensicData',
        outputs=outputs,
        outputs_key_field='identifier',
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Incident Forensic Data", outputs, removeNull=True)
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
    incident_id = args.get('incident_id', 'Incident ID is missing')
    page = get_and_validate_int_argument(args, 'page', minimum=MINIMUM_PAGE_VALUE)
    limit = get_and_validate_int_argument(args, 'limit', minimum=MINIMUM_LIMIT_INCIDENTS_VALUE)

    try:
        raw_response = client.fraud_watch_incident_contact_emails_list(incident_id, page, limit)
    except DemistoException as e:
        if 'Not Found' in str(e):
            page_error_msg = f'''Make sure page index: ({page}) is within bounds.''' if page else ''
            unknown_incident_msg = f'''Make sure incident id: ({incident_id}) is correct.'''
            raise DemistoException(f'''Error occurred. {page_error_msg} {unknown_incident_msg}''')
        raise e

    return CommandResults(
        outputs_prefix='FraudWatch.IncidentContacts',
        outputs=raw_response,
        outputs_key_field='noteId',
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Incident Contacts Data", raw_response, removeNull=True)
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
    incident_id = args.get('incident_id', 'Incident ID is missing')
    message_content = args.get('message_content')

    if not message_content:
        raise DemistoException('Message content cannot be empty.')

    try:
        raw_response = client.fraud_watch_incident_messages_add(incident_id, message_content)
    except DemistoException as e:
        if 'Not Found' in str(e):
            raise DemistoException(f'Error occurred. Make sure incident id: ({incident_id}) is correct')
        raise e

    if 'Message add sucessfully' not in raw_response:
        raise DemistoException(f'Unexpected response returned by FraudWatch: {raw_response}')

    human_readable = f'### Message for incident id {incident_id} with content {message_content} was added successfully.'

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
    incident_id = args.get('incident_id', 'Incident ID is missing')
    raw_urls = argToList(args.get('urls'))

    if not raw_urls:
        raise DemistoException('''No url to be added have been given for 'fraudwatch-incident-urls-add' command''')

    urls: Dict[str, List[str]] = {
        'urls[]': []
    }
    for raw_url in raw_urls:
        urls['urls[]'].append(raw_url)

    try:
        raw_response = client.fraud_watch_incident_urls_add(incident_id, urls)
    except DemistoException as e:
        if 'Not Found' in str(e):
            raise DemistoException(f'Error occurred. Make sure incident id: ({incident_id}) is correct')
        raise e

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
    - Unknown incident id. # TODO CHECK ON FILE ERROR TOO

    Args:
        client (Client): FraudWatch client to perform the API calls.
        args (Dict): Demisto arguments.

    Returns:
        CommandResults.
    """
    incident_id = args.get('incident_id', 'Incident ID is missing')
    entry_id = args.get('attachment')

    try:
        # entry id of uploaded file to war room
        file_info = demisto.getFilePath(entry_id)
        with open(file_info['path'], 'rb') as uploaded_file:
            raw_response = client.fraud_watch_attachment_upload_command(incident_id, uploaded_file)

            if 'Updated sucessfully' not in raw_response:
                raise DemistoException(f'Unexpected response returned by FraudWatch: {raw_response}')

            return CommandResults(
                raw_response=raw_response,
                readable_output=f'### File entry {entry_id} was uploaded successfully to incident with incident id '
                                f'{incident_id}'
            )
    except DemistoException as e:
        if 'Not Found' in str(e):
            raise DemistoException(f'Error occurred. Make sure incident id: ({incident_id}) is correct')
        raise e
    except Exception:
        raise DemistoException(F"Entry {entry_id} does not contain a file.")


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
    if outputs is None:
        raise DemistoException(f'Unexpected response returned by FraudWatch: {raw_response}')

    return CommandResults(
        outputs_prefix='FraudWatch.Brand',
        outputs=outputs,
        outputs_key_field='name',
        raw_response=raw_response,
        readable_output=tableToMarkdown("FraudWatch Brands", outputs, removeNull=True)
    )


''' MAIN FUNCTION '''


def main() -> None:
    """
        Main function, parses params and runs command functions.
    """
    command = demisto.command()
    params = demisto.params()

    commands = {
        'fraudwatch-incidents-list': fraud_watch_incidents_list_command,
        'fraudwatch-incident-report': fraud_watch_incident_report_command,
        'fraudwatch-incident-update': fraud_watch_incident_update_command,
        'fraudwatch-incident-get-by-identifier': fraud_watch_incident_get_by_identifier_command,
        'fraudwatch-incident-forensic-get': fraud_watch_incident_forensic_get_command,
        'fraudwatch-incident-contact-emails-list': fraud_watch_incident_contact_emails_list_command,
        'fraudwatch-incident-messages-add': fraud_watch_incident_messages_add_command,
        'fraudwatch-incident-urls-add': fraud_watch_incident_urls_add_command,
        'fraudwatch-incident-attachment-upload': fraud_watch_attachment_upload_command,
        'fraudwatch-brands-list': fraud_watch_brands_list_command
    }

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
            result = test_module(client)
            return_results(result)

        elif command in commands:
            return_results(commands[command](client, demisto.args()))

        else:
            raise NotImplementedError(f'Command {command} is not implemented.')

    # Log exceptions and return errors
    except Exception as e:
        demisto.error(traceback.format_exc())  # print the traceback
        return_error(f'Failed to execute {demisto.command()} command.\nError:\n{str(e)}')


''' ENTRY POINT '''

if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
