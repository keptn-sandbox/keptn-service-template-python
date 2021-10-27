import sys
import base64
import json
import time
import threading
import requests

from cloudevents.http import from_http, CloudEvent, to_structured


SERVICENAME = "keptn-service-template-python"

KEPTN_DISTRIBUTOR = "http://127.0.0.1:8081"
KEPTN_API_EVENT_ENDPOINT = "/event" # will be set to /v1/event in case of authenticated handler
KEPTN_API_TRIGGERED_URL = "/controlPlane/v1/event/triggered/sh.keptn.event.{event_type}"
KEPTN_API_METADATA_URL = "/v1/metadata"

POLLING_TIME_SECONDS = 10

HTTP_DEFAULT_HEADERS = {
    'user-agent': "keptn-service-template-go",
    'accept': "application/json; charset=utf-8",
    'Content-Type': "application/json; charset=utf-8"            
}

STATUS_SUCCEEDED = "succeeded"
STATUS_ERRORED = "errored"
STATUS_UNKNOWN = "unknown"

ALLOWED_STATUS = [STATUS_SUCCEEDED, STATUS_ERRORED, STATUS_UNKNOWN]

RESULT_PASS = "pass"
RESULT_WARNING = "warning"
RESULT_FAIL = "fail"

ALLOWED_RESULTS = [RESULT_PASS, RESULT_WARNING, RESULT_FAIL]



class KeptnApiConnection:
    def get(url, headers=None):
        raise NotImplementedError
    
    def post(url, data=None, headers=None):
        raise NotImplementedError

class KeptnDistributorApiConnection(KeptnApiConnection):
    def get(url, headers=None):
        if headers is None:
            headers = {}
        headers = {**HTTP_DEFAULT_HEADERS, **headers}
        return requests.get(KEPTN_DISTRIBUTOR + url, headers=headers)

    def post(url, data=None, headers=None):
        if headers is None:
            headers = {}
        headers = {**HTTP_DEFAULT_HEADERS, **headers}
        return requests.post(KEPTN_DISTRIBUTOR + url, headers=headers, data=data)

class KeptnAuthenticatedApiConnection(KeptnApiConnection):
    keptn_api_endpoint = ""
    keptn_api_token = ""

    def get(url, headers=None):
        if headers is None:
            headers = {}
        headers = {**HTTP_DEFAULT_HEADERS, **headers, 'x-token': KeptnAuthenticatedApiConnection.keptn_api_token,}

        response = requests.get(KeptnAuthenticatedApiConnection.keptn_api_endpoint + url, headers=headers)

        if response.status_code >= 400:
            print("ERROR {}: {}".format(response.status_code, KeptnAuthenticatedApiConnection.keptn_api_endpoint + url))

        return response

    def post(url, data=None, headers=None):
        if headers is None:
            headers = {}
        
        headers = {**HTTP_DEFAULT_HEADERS, **headers, 'x-token': KeptnAuthenticatedApiConnection.keptn_api_token,}

        response = requests.post(KeptnAuthenticatedApiConnection.keptn_api_endpoint + url, headers=headers, data=data)

        if response.status_code >= 400:
            print("ERROR {}: {}".format(response.status_code, KeptnAuthenticatedApiConnection.keptn_api_endpoint + url))

        return response


KEPTN_API = KeptnDistributorApiConnection # will be overwritten below if certain environment variables are set


class Keptn:

    event_registry = {}
    api = KeptnDistributorApiConnection

    def __init__(self, event):
        self.sh_keptn_context = None
        self.triggered_id = None
        self.event_type = None
        self.keptn_event_type = None
        self.event = event
        self.event_data = event.data

        # extract keptn context
        if 'shkeptncontext' in event:
            self.sh_keptn_context = event['shkeptncontext']

        self.event_type = event['type']
        self.triggered_id = event['id']

        # check if this is a Keptn Event
        if self.event_type.startswith("sh.keptn.event."):
            self.keptn_event_type = self.event_type.replace("sh.keptn.event.", "")
            # extract task name
            if self.keptn_event_type.endswith(".triggered"):
                self.task_name = self.keptn_event_type.replace(".triggered", "")
            elif self.keptn_event_type.endswith(".started"):
                self.task_name = self.keptn_event_type.replace(".started", "")
            elif self.keptn_event_type.endswith(".finished"):
                self.task_name = self.keptn_event_type.replace(".finished", "")
            elif self.keptn_event_type.endswith(".status.changed"):
                self.task_name = self.keptn_event_type.replace(".status.changed", "")


    def handle_cloud_event(self):
        if not self.keptn_event_type:
            # Not a Keptn Cloud Event
            print("ERROR: Not a Keptn CloudEvent")
            return None

        # check if somebody has registered an event
        if self.keptn_event_type in self.event_registry:
            print("Found!")
            # call it
            func = self.event_registry[self.keptn_event_type]
            print("found ", func)
            func(self, self.sh_keptn_context, self.event, self.event_data)


    def on(keptn_event_type, func):
        print(f"Subscribing to {keptn_event_type}")
        Keptn.event_registry[keptn_event_type] = func

    def _post_cloud_event(self, body, headers):
        resp = KEPTN_API.post(KEPTN_API_EVENT_ENDPOINT, body, headers)

    def _send_cloud_event(self, shkeptncontext, cetype, message, result=None, status=None, data=None):
        # Create a CloudEvent
        # - The CloudEvent "id" is generated if omitted. "specversion" defaults to "1.0".
        attributes = {
            "type": cetype,
            "source": SERVICENAME,
            "shkeptnspecversion": "0.2.1",
            "shkeptncontext": self.sh_keptn_context,
            "triggeredid": self.triggered_id
        }

        if not data:
            data = {}

        data['project'] = self.event_data['project']
        data['service'] = self.event_data['service']
        data['stage'] = self.event_data['stage']
        if 'labels' in self.event_data:
            data['labels'] = self.event_data['labels']

        if result:
            data['result'] = result
        if status:
            data['status'] = status
        if message:
            data['message'] = message
        
   

        event = CloudEvent(attributes, data)

        # Creates the HTTP request representation of the CloudEvent in structured content mode
        headers, body = to_structured(event)

        # POST
        self._post_cloud_event(body, headers)

        return None

    
    def _decode_config_service_response(self, response):
        if response.status_code >= 200 and response.status_code < 300:
            # parse content
            data = response.json()
            base64ResourcEContent = data['resourceContent']

            return base64.b64decode(data['resourceContent'])

        return None

    def _get_resource_from_config_service(self, resource_name, project, service=None, stage=None):

        if project and not service and not stage:
            # get project resource
            api_endpoint = f"/configuration-service/v1/project/{project}/resource/{resource_name}"
        elif project and stage and not service:
            # get stage resource
            api_endpoint = f"/configuration-service/v1/project/{project}/stage/{stage}/resource/{resource_name}"
        else:
            # get service resource
            api_endpoint = f"/configuration-service/v1/project/{project}/stage/{stage}/service/{service}/resource/{resource_name}"

        response = KEPTN_API.get(api_endpoint)

        return self._decode_config_service_response(response)

    def get_project_resource(self, resource_name):
        return self._get_resource_from_config_service(resource_name, project=self.event_data['project'])

    def get_service_resource(self, resource_name):
        return self._get_resource_from_config_service(resource_name, project=self.event_data['project'], stage=self.event_data['stage'], service=self.event_data['service'])

    def get_stage_resource(self, resource_name):
        return self._get_resource_from_config_service(resource_name, project=self.event_data['project'], stage=self.event_data['stage'])


    def send_task_started_cloudevent(self, data=None, message="", result=RESULT_PASS, status=STATUS_SUCCEEDED):
        return self._send_cloud_event(self.sh_keptn_context, "sh.keptn.event." + self.task_name + ".started", message, result, status, data)

    def send_task_finished_cloudevent(self, data=None, message="", result=RESULT_PASS, status=STATUS_SUCCEEDED):
        return self._send_cloud_event(self.sh_keptn_context, "sh.keptn.event." + self.task_name + ".finished", message, result, status, data)
    
    def send_task_status_changed_cloudevent(self, data=None, message="", result=RESULT_PASS, status=STATUS_SUCCEEDED):
        return self._send_cloud_event(self.sh_keptn_context, "sh.keptn.event." + self.task_name + ".status.changed", message, result, status, data)




class StandaloneKeptn(Keptn):
    event_id_cache = []

    def poll():
        while True:
            for event_type in Keptn.event_registry:
                print("Polling events for event type " + event_type)
                response = KEPTN_API.get(KEPTN_API_TRIGGERED_URL.format(
                    event_type=event_type
                ))

                if response.status_code != 200:
                    print("ERROR: Failed to fetch CloudEvents of type " + event_type)
                    continue
                
                data = json.loads(response.content)

                if "totalCount" in data:
                    print("- Received {totalCount} CloudEvents".format(totalCount=data["totalCount"]))

                    if "events" in data:
                        cloud_events = data["events"]

                        for ce_json in cloud_events:
                            # convert json to cloudevent
                            ce = CloudEvent(ce_json, ce_json["data"])
                            assert ce.data != None

                            assert "shkeptncontext" in ce
                            assert "type" in ce
                            assert ce.data['project'] != None
                            assert ce.data['service'] != None
                            assert ce.data['stage'] != None

                            # verify CloudEvent has not been processed yet
                            if ce['id'] not in StandaloneKeptn.event_id_cache:
                                StandaloneKeptn.event_id_cache.append(ce['id'])
                                # create a new keptn instance and let it handle the event
                                keptn = StandaloneKeptn(ce)
                                handle_thread = threading.Thread(target=keptn.handle_cloud_event)
                                handle_thread.start()
                            else:
                                print(" - Skipping cloudevent with id {id} as it was already processed before".format(id=ce['id']))

            try:
                time.sleep(POLLING_TIME_SECONDS)
            except KeyboardInterrupt:
                return        
        


"""
KeptnUnitTestHelper is a Keptn class specifically for unit testing Keptn integrations

It overwrites
- _post_cloud_event such that cloudevents are stored in a local list rather than sent out to the network
- _get_resource_from_config_service such that it fetches files from the local filesystem (test_resources folder)
"""
class KeptnUnitTestHelper(Keptn):

    def __init__(self, event):
        super().__init__(event)
        self.cloud_events_sent = []

    def _post_cloud_event(self, body, headers):
        self.cloud_events_sent.append(from_http(headers, body))

    def _get_resource_from_config_service(self, resource_name, project, service=None, stage=None):
        if project and not service and not stage:
            file_name = f'test_resources/{project}/{resource_name}'
        elif project and stage and not service:
            file_name = f'test_resources/{project}/{stage}/{resource_name}'
        else:
            file_name = f'test_resources/{project}/{stage}/{service}/{resource_name}'

        try:
            with open(file_name) as f:
                return str(f.read())
        except:
            return None

    def load_cloudevent_from_file(filename):
        with open(filename) as json_file:
            json_data = str(json_file.read())
            ce = from_http({}, json_data)

            assert ce.data != None

            assert "shkeptncontext" in ce
            assert "type" in ce
            assert ce.data['project'] != None
            assert ce.data['service'] != None
            assert ce.data['stage'] != None

            return ce



def start_polling(keptn_api_endpoint, keptn_api_token):
    global KEPTN_API, KEPTN_API_EVENT_ENDPOINT

    # configure KEPTN_API to use the authenticated api connection
    KEPTN_API = KeptnAuthenticatedApiConnection
    KeptnAuthenticatedApiConnection.keptn_api_endpoint = keptn_api_endpoint
    KeptnAuthenticatedApiConnection.keptn_api_token = keptn_api_token

    # check if connection works
    response = KEPTN_API.get(KEPTN_API_METADATA_URL)

    if response.status_code != 200:
        print("Error: Could not reach API")
        print(response.content)
        return None

    # rewrite event endpoint, as /event only exists on distributor, but needs to be /v1/event for the real api
    KEPTN_API_EVENT_ENDPOINT = "/v1/event"
    
    print("Starting to poll...")
    x = threading.Thread(target=StandaloneKeptn.poll, daemon=True)
    x.start()

    return x
