Manage incidents via the Fraudwatch API. FraudWatch International provides a fully managed Enterprise Digital Brand Protection Suite, including online brand management & monitoring as well as providing other brand protection solutions that protect organizations and their customers around the world against online brand-related abuse.
This integration was integrated and tested with version v1 of FraudWatch Phishportal
## Configure FraudWatch on Cortex XSOAR

1. Navigate to **Settings** > **Integrations** > **Servers & Services**.
2. Search for FraudWatch.
3. Click **Add instance** to create and configure a new integration instance.

    | **Parameter** | **Description** | **Required** |
    | --- | --- | --- |
    | API Key | The API Key to use for connection | True |
    | Protocol | The communication protocol. Possible values are: "http" and "https". | False |
    | Fetch incidents |  | False |
    | Incident type |  | False |
    | Incidents Fetch Interval |  | False |
    | First fetch timestamp | format: \(&amp;lt;number&amp;gt; &amp;lt;time unit&amp;gt;, e.g., 12 hours, 7 days\) | False |
    | Maximum Incidents To Fetch |  | False |
    | Trust any certificate (not secure) |  | False |
    | Use system proxy settings |  | False |

4. Click **Test** to validate the URLs, token, and connection.
## Commands
You can execute these commands from the Cortex XSOAR CLI, as part of an automation, or in a playbook.
After you successfully execute a command, a DBot message appears in the War Room with the command details.
### fraudwatch-incidents-list
***
Get list of incidents from FraudWatch service.


#### Base Command

`fraudwatch-incidents-list`
#### Input

| **Argument Name** | **Description** | **Required** |
| --- | --- | --- |
| brand | Retrieve incidents which corresponds to the given brand. Returns error if brand does not exist. | Optional | 
| status | Retrieve incidents which corresponds to the given status. Possible values are: active, new, monitor, reactive, onhold, closed, closedmonitor, rejected, duplicate. | Optional | 
| limit | Total number of Incidents in a page. Maximum number is 200. Default is 20. | Optional | 
| page | Retrieve incidents by the given page number. | Optional | 
| from | Retrieve alerts that their date opened day is higher or equal to 'from' value. Format is: yyyy-mm-dd. If 'to' argument is not given, default value for 'to' is current day. | Optional | 
| to | Retrieve alerts that their date opened day is lower or equal to 'to' value. Format is: yyyy-mm-dd. If 'from' argument is not given, default value for 'from' is 12 months before 'to'. | Optional | 


#### Context Output

| **Path** | **Type** | **Description** |
| --- | --- | --- |
| FraudWatch.Incident.identifier | String | Identifier of the incident. | 
| FraudWatch.Incident.reference_id | String | Reference ID of the incident. | 
| FraudWatch.Incident.url | String | Main URL associated to the incident. | 
| FraudWatch.Incident.status | String | Status of the incident. | 
| FraudWatch.Incident.type | String | Type of the incident. | 
| FraudWatch.Incident.brand | String | Brand of the incident. | 
| FraudWatch.Incident.client | String | Client. | 
| FraudWatch.Incident.content_ip | String | Content IP. | 
| FraudWatch.Incident.host | String | The incident's host. | 
| FraudWatch.Incident.host_country | String | The country of the host. | 
| FraudWatch.Incident.host_timezone | String | The timezone of the host. | 
| FraudWatch.Incident.created_by | String | Who created the incident. | 
| FraudWatch.Incident.discovered_by | String | Who discovered the incident. | 
| FraudWatch.Incident.current_duration | String | Current duration of the incident. | 
| FraudWatch.Incident.active_duration | Unknown | Current active duration of the incident. | 
| FraudWatch.Incident.date_opened | Date | The date incident was opened. | 
| FraudWatch.Incident.date_closed | Date | The date incident was closed. | 
| FraudWatch.Incident.additional_urls | String | Additional URLs associated to the incidents. | 
| FraudWatch.Incident.link | String | URL to the incident page in FraudWatch User Interface. | 


#### Command Example
```!fraudwatch-incidents-list brand="Testing Brand 1" from="2020-12-12" limit=3 status=monitor```

#### Context Example
```json
{
    "FraudWatch": {
        "Incident": [
            {
                "active_duration": null,
                "additional_urls": [],
                "brand": "Testing Brand 1",
                "client": "Investec - Palo Alto",
                "content_ip": null,
                "created_by": "Client",
                "current_duration": "173541",
                "date_closed": null,
                "date_opened": "2021-02-02T16:36:53.000Z",
                "discovered_by": "client",
                "host": null,
                "host_country": null,
                "host_timezone": null,
                "identifier": "JJJ-313924",
                "link": "http://www.phishportal.com/client/incident/JJJ-313924",
                "reference_id": null,
                "status": "monitor",
                "type": "Vishing",
                "url": "test.com"
            },
            {
                "active_duration": null,
                "additional_urls": [],
                "brand": "Testing Brand 1",
                "client": "Investec - Palo Alto",
                "content_ip": null,
                "created_by": "Client",
                "current_duration": "173544",
                "date_closed": null,
                "date_opened": "2021-02-02T16:36:50.000Z",
                "discovered_by": "client",
                "host": null,
                "host_country": null,
                "host_timezone": null,
                "identifier": "JJJ-168840",
                "link": "http://www.phishportal.com/client/incident/JJJ-168840",
                "reference_id": null,
                "status": "monitor",
                "type": "Vishing",
                "url": "test.com"
            },
            {
                "active_duration": null,
                "additional_urls": [],
                "brand": "Testing Brand 1",
                "client": "Investec - Palo Alto",
                "content_ip": null,
                "created_by": "Client",
                "current_duration": "173545",
                "date_closed": null,
                "date_opened": "2021-02-02T16:36:49.000Z",
                "discovered_by": "client",
                "host": null,
                "host_country": null,
                "host_timezone": null,
                "identifier": "JJJ-674271",
                "link": "http://www.phishportal.com/client/incident/JJJ-674271",
                "reference_id": null,
                "status": "monitor",
                "type": "Vishing",
                "url": "test.com"
            }
        ]
    }
}
```

#### Human Readable Output

>### FraudWatch Incidents
>|identifier|url|status|type|brand|client|created_by|discovered_by|current_duration|date_opened|link|
>|---|---|---|---|---|---|---|---|---|---|---|
>| JJJ-313924 | test.com | monitor | Vishing | Testing Brand 1 | Investec - Palo Alto | Client | client | 173541 | 2021-02-02T16:36:53.000Z | http://www.phishportal.com/client/incident/JJJ-313924 |
>| JJJ-168840 | test.com | monitor | Vishing | Testing Brand 1 | Investec - Palo Alto | Client | client | 173544 | 2021-02-02T16:36:50.000Z | http://www.phishportal.com/client/incident/JJJ-168840 |
>| JJJ-674271 | test.com | monitor | Vishing | Testing Brand 1 | Investec - Palo Alto | Client | client | 173545 | 2021-02-02T16:36:49.000Z | http://www.phishportal.com/client/incident/JJJ-674271 |


### fraudwatch-incident-report
***
Report an incident to FraudWatch service.


#### Base Command

`fraudwatch-incident-report`
#### Input

| **Argument Name** | **Description** | **Required** |
| --- | --- | --- |
| brand | The brand associated to the reported incident. | Required | 
| type | The type of the incident to be associated to the reported incident. Returns error if brand does not exist. Possible values are: phishing, vishing, brand_abuse, malware, social_media_brand_abuse, mobile_app_unauthorized, pac_file, pharming, messaging, dmarc_email_server. | Required | 
| reference_id | Reference ID to be associated to the reported incident. Should be unique. Reference ID can be used later to retrieve specific incident by its reference id. | Optional | 
| primary_url | Primary URL of the reported incident. | Required | 
| urls | Comma seperated list. Additional urls in addition to 'primary_url' to be associated with the reported incident. | Optional | 
| evidence | Evidence to be added (such as logs, etc...) to the reported incident. | Optional | 
| instructions | Additional instructions to be added for FraudWatch Security Team about the reported incident. | Optional | 


#### Context Output

| **Path** | **Type** | **Description** |
| --- | --- | --- |
| FraudWatch.Incident.identifier | String | Identifier of the new reported incident. | 
| FraudWatch.Incident.reference_id | String | Reference ID of the new reported incident. | 
| FraudWatch.Incident.url | String | Main URL associated to the new reported incident. | 
| FraudWatch.Incident.status | String | Status of the new reported incident. | 
| FraudWatch.Incident.type | String | Type of the new reported incident. | 
| FraudWatch.Incident.brand | String | Brand of the new reported incident. | 
| FraudWatch.Incident.client | String | Client. | 
| FraudWatch.Incident.content_ip | String | Content IP. | 
| FraudWatch.Incident.host | String | The new reported incident's host. | 
| FraudWatch.Incident.host_country | String | The country of the host. | 
| FraudWatch.Incident.host_timezone | String | The timezone of the host. | 
| FraudWatch.Incident.created_by | String | Who created the new reported incident. | 
| FraudWatch.Incident.discovered_by | String | Who discovered the new reported incident. | 
| FraudWatch.Incident.current_duration | String | Current duration of the new reported incident. | 
| FraudWatch.Incident.active_duration | Unknown | Current active duration of the new reported incident. | 
| FraudWatch.Incident.date_opened | Date | The date the new reported incident was opened. Has value of the day incident was reported. | 
| FraudWatch.Incident.date_closed | Date | The date new reported incident was closed. Starts empty, as incident was just created. | 
| FraudWatch.Incident.additional_urls | String | Additional URLs associated to the new reported incident. | 
| FraudWatch.Incident.link | String | Link to the new reported incident page in FraudWatch User Interface. | 


#### Command Example
```!fraudwatch-incident-report brand="Testing Brand 2" primary_url="malicious.com" type=brand_abuse reference_id="malicious1" urls="abuse.com"```

#### Context Example
```json
{
    "FraudWatch": {
        "Incident": {
            "active_duration": null,
            "additional_urls": [
                "abuse.com"
            ],
            "brand": "Testing Brand 2",
            "client": "Investec - Palo Alto",
            "content_ip": null,
            "created_by": "FraudWatch",
            "current_duration": "0",
            "date_closed": null,
            "date_opened": "2021-02-04T16:49:16.000Z",
            "discovered_by": "client",
            "host": null,
            "host_country": null,
            "host_timezone": null,
            "identifier": "JJJ-302171",
            "link": "http://www.phishportal.com/client/incident/JJJ-302171",
            "reference_id": "malicious1",
            "status": "monitor",
            "type": "Brand Abuse",
            "url": "malicious.com"
        }
    }
}
```

#### Human Readable Output

>### Created FraudWatch Incident
>|additional_urls|brand|client|created_by|current_duration|date_opened|discovered_by|identifier|link|reference_id|status|type|url|
>|---|---|---|---|---|---|---|---|---|---|---|---|---|
>| abuse.com | Testing Brand 2 | Investec - Palo Alto | FraudWatch | 0 | 2021-02-04T16:49:16.000Z | client | JJJ-302171 | http://www.phishportal.com/client/incident/JJJ-302171 | malicious1 | monitor | Brand Abuse | malicious.com |


### fraudwatch-incident-update
***
Updates the incident associated to the 'incident_id' with given arguments values.


#### Base Command

`fraudwatch-incident-update`
#### Input

| **Argument Name** | **Description** | **Required** |
| --- | --- | --- |
| incident_id | The ID of the incident to be updated. Incident ID is the 'identifier' field returned by command 'fraudwatch-incidents-list'. | Required | 
| brand | Updates the incident associated to the 'incident_id' with brand given. | Optional | 
| reference_id | Updates the incident associated to the 'incident_id' with reference ID given. Reference ID should be unique, and can be used by command 'fraudwatch-incident-get-by-identifier' to retrieve specific incident's details by its reference id. | Optional | 
| instructions | Updates the incident associated to the 'incident_id' with additional instructions for FraudWatch Security Team. | Optional | 


#### Context Output

There is no context output for this command.

#### Command Example
```!fraudwatch-incident-update incident_id=JJJ-504830 brand="Testing Brand 2" reference_id="reference123"```

#### Human Readable Output

>### Incident with ID JJJ-504830 was updated successfully

### fraudwatch-incident-get-by-identifier
***
Gets an incident from FraudWatch service by its reference ID or incident ID. Exactly one argument of 'reference_id' and 'incident_id' should be given.


#### Base Command

`fraudwatch-incident-get-by-identifier`
#### Input

| **Argument Name** | **Description** | **Required** |
| --- | --- | --- |
| incident_id | The ID of the incident to be retrieve its details. Incident ID is the 'identifier' field returned by command 'fraudwatch-incidents-list'. | Optional | 
| reference_id | Reference id of the incident to be retrieve its details. If more than one incident is associated to 'reference_id',returns the details of the incident with the latest date opened. Reference ID is the 'reference_id' field returned by command 'fraudwatch-incidents-list'. | Optional | 


#### Context Output

| **Path** | **Type** | **Description** |
| --- | --- | --- |
| FraudWatch.Incident.identifier | String | Identifier of the incident. | 
| FraudWatch.Incident.reference_id | String | Reference ID of the incident. | 
| FraudWatch.Incident.url | String | Main URL associated to the incident. | 
| FraudWatch.Incident.status | String | Status of the incident. | 
| FraudWatch.Incident.type | String | Type of the incident. | 
| FraudWatch.Incident.brand | String | Brand of the incident. | 
| FraudWatch.Incident.client | String | Client. | 
| FraudWatch.Incident.content_ip | String | Content IP. | 
| FraudWatch.Incident.host | String | The incident's host. | 
| FraudWatch.Incident.host_country | String | The country of the host. | 
| FraudWatch.Incident.host_timezone | String | The timezone of the host. | 
| FraudWatch.Incident.created_by | String | Who created the incident. | 
| FraudWatch.Incident.discovered_by | String | Who discovered the incident. | 
| FraudWatch.Incident.current_duration | String | Current duration of the incident. | 
| FraudWatch.Incident.active_duration | Unknown | Current active duration of the incident. | 
| FraudWatch.Incident.date_opened | Date | The date incident was opened. | 
| FraudWatch.Incident.date_closed | Date | The date incident was closed. | 
| FraudWatch.Incident.additional_urls | String | Additional URLs associated to the incident. | 
| FraudWatch.Incident.link | String | Link to the incident page in FraudWatch User Interface. | 


#### Command Example
```!fraudwatch-incident-get-by-identifier incident_id=JJJ-168840```

#### Context Example
```json
{
    "FraudWatch": {
        "Incident": {
            "active_duration": null,
            "additional_urls": [],
            "brand": "Testing Brand 1",
            "client": "Investec - Palo Alto",
            "content_ip": null,
            "created_by": "Client",
            "current_duration": "173551",
            "date_closed": null,
            "date_opened": "2021-02-02T16:36:50.000Z",
            "discovered_by": "client",
            "host": null,
            "host_country": null,
            "host_timezone": null,
            "identifier": "JJJ-168840",
            "link": "http://www.phishportal.com/client/incident/JJJ-168840",
            "reference_id": null,
            "status": "monitor",
            "type": "Vishing",
            "url": "test.com"
        }
    }
}
```

#### Human Readable Output

>### FraudWatch Incident
>|brand|client|created_by|current_duration|date_opened|discovered_by|identifier|link|status|type|url|
>|---|---|---|---|---|---|---|---|---|---|---|
>| Testing Brand 1 | Investec - Palo Alto | Client | 173551 | 2021-02-02T16:36:50.000Z | client | JJJ-168840 | http://www.phishportal.com/client/incident/JJJ-168840 | monitor | Vishing | test.com |


### fraudwatch-incident-forensic-get
***
Gets forensic data of an incident associated to the given incident ID.


#### Base Command

`fraudwatch-incident-forensic-get`
#### Input

| **Argument Name** | **Description** | **Required** |
| --- | --- | --- |
| incident_id | The ID of the incident to retrieve its forensic data. Incident ID is the 'identifier' field returned by command 'fraudwatch-incidents-list'. | Required | 


#### Context Output

| **Path** | **Type** | **Description** |
| --- | --- | --- |
| FraudWatch.IncidentForensicData.host_provider.name | String | Name of the host provider. | 
| FraudWatch.IncidentForensicData.host_provider.country | String | Country of the host provider. | 
| FraudWatch.IncidentForensicData.host_nameservers | String | Name of the host servers. | 
| FraudWatch.IncidentForensicData.host_domain_registrar.name | String | Host domain registrar name. | 
| FraudWatch.IncidentForensicData.host_domain_registrar.email | String | Host domain registrar email. | 
| FraudWatch.IncidentForensicData.host_domain_registrar.country | String | Host domain registrar country. | 
| FraudWatch.IncidentForensicData.identifier | String | Identifier of the incident. | 


#### Command Example
```!fraudwatch-incident-forensic-get incident_id=JJJ-397266```

#### Context Example
```json
{
    "FraudWatch": {
        "IncidentForensicData": {
            "host_domain_admin": [],
            "host_domain_registrar": {
                "country": "abuse@moniker.com",
                "email": "http://www.moniker.com",
                "name": "Moniker Online Services LLC"
            },
            "host_ip_providier": [],
            "host_nameservers": [
                "NS1.IRAN.COM",
                "NS2.IRAN.COM"
            ],
            "host_provider": {
                "country": null,
                "name": null
            },
            "host_site_admin": [],
            "host_site_owner": [],
            "identifier": "JJJ-397266"
        }
    }
}
```

#### Human Readable Output

>### FraudWatch Incident Forensic Data
>|host_domain_registrar|host_nameservers|host_provider|identifier|
>|---|---|---|---|
>| name: Moniker Online Services LLC<br/>email: http://www.moniker.com<br/>country: abuse@moniker.com | NS1.IRAN.COM,<br/>NS2.IRAN.COM | name: null<br/>country: null | JJJ-397266 |


### fraudwatch-incident-contact-emails-list
***
Provides contact emails for the incident associated to the given incident ID.


#### Base Command

`fraudwatch-incident-contact-emails-list`
#### Input

| **Argument Name** | **Description** | **Required** |
| --- | --- | --- |
| incident_id | The ID of the incident to retrieve its email contacts data. Incident ID is the 'identifier' field returned by command 'fraudwatch-incidents-list'. | Required | 
| limit | Maximum number of contact emails in a page. Maximum number is 200. Default is 20. | Optional | 
| page | Retrieve contact emails by the given page number. | Optional | 


#### Context Output

| **Path** | **Type** | **Description** |
| --- | --- | --- |
| FraudWatch.IncidentContacts.noteId | String | Note ID of the email. | 
| FraudWatch.IncidentContacts.subject | String | Subject of the email. | 
| FraudWatch.IncidentContacts.creator | String | The creator of the email. | 
| FraudWatch.IncidentContacts.content | String | The content of the email. | 
| FraudWatch.IncidentContacts.date | Date | The date of the email. | 


#### Command Example
```!fraudwatch-incident-contact-emails-list incident_id=JJJ-898410 limit=2```

#### Context Example
```json
{
    "FraudWatch": {
        "IncidentContacts": [
            {
                "content": "This incident is very malicious, please monitor it\r\n",
                "creator": "Client",
                "date": "2021-02-04T16:43:11.000Z",
                "noteId": "11052619",
                "subject": "Client Reply"
            },
            {
                "content": "Dear Investec - Palo Alto\r\n\r\nA new Vishing incident has been created with the following details:\r\n\r\nContent: test .com\r\nBrand Targeted: Testing Brand 1\r\nOur Reference: Incident#JJJ-898410 \r\n\r\n\r\n*********************************************\r\n*************** IMPORTANT ****************\r\n*********************************************\r\nThis incident is only being monitored.\r\n\r\nTo request a Take Down, please log in, or reply to this email clearly requesting a Take Down.\r\n*********************************************\r\n\r\nYou can view details of this incident by logging into PhishPortal (https://www.phishportal.com).\r\n\r\nRegards,\r\nSecurity Operations\r\nFraudWatch International\r\nTel USA: +1-415-449-8800 Ext 200\r\nTel AUS: +613 9887 6777\r\nFax: +613 8660 2688\r\nEmail: security@fraudwatchinternational.com\r\nhttp://www.fraudwatchinternational.com\r\n",
                "creator": "FraudWatch",
                "date": "2021-02-02T14:26:35.000Z",
                "noteId": "11027360",
                "subject": "Outgoing email recorded"
            }
        ]
    }
}
```

#### Human Readable Output

>### FraudWatch Incident Contacts Data
>|noteId|subject|creator|content|date|
>|---|---|---|---|---|
>| 11052619 | Client Reply | Client | This incident is very malicious, please monitor it<br/> | 2021-02-04T16:43:11.000Z |
>| 11027360 | Outgoing email recorded | FraudWatch | Dear Investec - Palo Alto<br/><br/>A new Vishing incident has been created with the following details:<br/><br/>Content: test .com<br/>Brand Targeted: Testing Brand 1<br/>Our Reference: Incident#JJJ-898410 <br/><br/><br/>*********************************************<br/>*************** IMPORTANT ****************<br/>*********************************************<br/>This incident is only being monitored.<br/><br/>To request a Take Down, please log in, or reply to this email clearly requesting a Take Down.<br/>*********************************************<br/><br/>You can view details of this incident by logging into PhishPortal (https://www.phishportal.com).<br/><br/>Regards,<br/>Security Operations<br/>FraudWatch International<br/>Tel USA: +1-415-449-8800 Ext 200<br/>Tel AUS: +613 9887 6777<br/>Fax: +613 8660 2688<br/>Email: security@fraudwatchinternational.com<br/>http://www.fraudwatchinternational.com<br/> | 2021-02-02T14:26:35.000Z |


### fraudwatch-incident-messages-add
***
Add a new message to be associated to the incident associated to the given incident ID.


#### Base Command

`fraudwatch-incident-messages-add`
#### Input

| **Argument Name** | **Description** | **Required** |
| --- | --- | --- |
| incident_id | The ID of the incident to add a message to its email contacts. Incident ID is the 'identifier' field returned by command 'fraudwatch-incidents-list'. | Required | 
| message_content | Content of the message. | Required | 


#### Context Output

There is no context output for this command.

#### Command Example
```!fraudwatch-incident-messages-add incident_id=JJJ-898410 message_content="This incident is very malicious, please monitor it"```

#### Human Readable Output

>### Message for incident id JJJ-898410 was added successfully.

### fraudwatch-incident-urls-add
***
Adds additional URLs to the incident associated to the given incident ID. Fails if one of the urls given already exists.


#### Base Command

`fraudwatch-incident-urls-add`
#### Input

| **Argument Name** | **Description** | **Required** |
| --- | --- | --- |
| incident_id | The ID of the incident to add additional urls to. Incident ID is the 'identifier' field returned by command 'fraudwatch-incidents-list'. | Required | 
| urls | Comma separated list. Additional URLs to be added to the incident associated to 'incident_id'. | Required | 


#### Context Output

| **Path** | **Type** | **Description** |
| --- | --- | --- |
| FraudWatch.IncidentUrls.success | String | Whether the URLs were added successfully. | 
| FraudWatch.IncidentUrls.new_urls | String | The new URLs that have been added. | 


#### Command Example
```!fraudwatch-incident-urls-add incident_id=JJJ-674271 urls=malicious1.com,malicious2.com```

#### Context Example
```json
{
    "FraudWatch": {
        "IncidentUrls": {
            "new_urls": [
                "http://malicious1.com",
                "http://malicious2.com"
            ],
            "success": "Add additional urls successfully"
        }
    }
}
```

#### Human Readable Output

>### FraudWatch Incident Urls
>|new_urls|success|
>|---|---|
>| http://malicious1.com,<br/>http://malicious2.com | Add additional urls successfully |


### fraudwatch-incident-attachment-upload
***
Adds a new file attachment to the incident associated to the given incident ID.


#### Base Command

`fraudwatch-incident-attachment-upload`
#### Input

| **Argument Name** | **Description** | **Required** |
| --- | --- | --- |
| incident_id | The ID of the incident to add a file attachment to. Incident ID is the 'identifier' field returned by command 'fraudwatch-incidents-list'. | Required | 
| attachment | Entry id in Demisto of the attachment to be added to the incident. | Required | 


#### Context Output

There is no context output for this command.

#### Command Example
```!fraudwatch-incident-attachment-upload attachment=zPXrMZSsNhH5g6rrxBLkhA@ea874720-782f-4095-8d76-595e9c41f3ce incident_id=JJJ-604206```

#### Human Readable Output

>### File entry zPXrMZSsNhH5g6rrxBLkhA@ea874720-782f-4095-8d76-595e9c41f3ce was uploaded successfully to incident with incident id JJJ-604206

### fraudwatch-brands-list
***
Gets a list of brands from FraudWatch service.


#### Base Command

`fraudwatch-brands-list`
#### Input

| **Argument Name** | **Description** | **Required** |
| --- | --- | --- |
| limit | Total number of brands in a page. Maximum number is 100. Default is 20. | Optional | 
| page | Retrieve brands by the given page number. | Optional | 


#### Context Output

| **Path** | **Type** | **Description** |
| --- | --- | --- |
| FraudWatch.Brand.client | String | The client. | 
| FraudWatch.Brand.alternate business name | String | Alternative business name. | 
| FraudWatch.Brand.name | String | The name of the brand. | 
| FraudWatch.Brand.active | Boolean | Wether brand is active or not. | 
| FraudWatch.Brand.services.name | String | The name of the service. | 
| FraudWatch.Brand.services.action | String | The action of the service. | 


#### Command Example
```!fraudwatch-brands-list```

#### Context Example
```json
{
    "FraudWatch": {
        "Brand": [
            {
                "active": true,
                "alternate business name": "",
                "client": "Investec - Palo Alto",
                "name": "Testing Brand 1",
                "services": [
                    {
                        "action": "takedown",
                        "name": "Phishing"
                    },
                    {
                        "action": "monitor",
                        "name": "Vishing"
                    },
                    {
                        "action": "monitor",
                        "name": "Brand Abuse"
                    },
                    {
                        "action": "monitor",
                        "name": "Malware"
                    },
                    {
                        "action": "monitor",
                        "name": "Social Media Brand Abuse"
                    },
                    {
                        "action": "monitor",
                        "name": "Mobile App (Unauthorized)"
                    },
                    {
                        "action": "monitor",
                        "name": "PAC File"
                    },
                    {
                        "action": "monitor",
                        "name": "Messaging"
                    },
                    {
                        "action": "monitor",
                        "name": "DMARC Email Server"
                    }
                ]
            },
            {
                "active": true,
                "alternate business name": "",
                "client": "Investec - Palo Alto",
                "name": "Testing Brand 2",
                "services": [
                    {
                        "action": "takedown",
                        "name": "Phishing"
                    },
                    {
                        "action": "monitor",
                        "name": "Vishing"
                    },
                    {
                        "action": "monitor",
                        "name": "Brand Abuse"
                    },
                    {
                        "action": "monitor",
                        "name": "Malware"
                    },
                    {
                        "action": "monitor",
                        "name": "Social Media Brand Abuse"
                    },
                    {
                        "action": "monitor",
                        "name": "Mobile App (Unauthorized)"
                    },
                    {
                        "action": "monitor",
                        "name": "PAC File"
                    },
                    {
                        "action": "monitor",
                        "name": "Messaging"
                    },
                    {
                        "action": "monitor",
                        "name": "DMARC Email Server"
                    }
                ]
            }
        ]
    }
}
```

#### Human Readable Output

>### FraudWatch Brands
>|name|active|client|
>|---|---|---|
>| Testing Brand 1 | true | Investec - Palo Alto |
>| Testing Brand 2 | true | Investec - Palo Alto |

