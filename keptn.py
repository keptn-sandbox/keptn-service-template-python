import os
import base64
import json
import time

import requests
from flask import Flask, request
from requests import api
from cloudevents.http import from_http, CloudEvent, to_structured


SERVICENAME = "keptn-service-template-python"

KEPTN_EVENT_ENDPOINT = "http://127.0.0.1:8081/event"

STATUS_SUCCEEDED = "succeeded"
STATUS_ERRORED = "errored"
STATUS_UNKNOWN = "unknown"

ALLOWED_STATUS = [STATUS_SUCCEEDED, STATUS_ERRORED, STATUS_UNKNOWN]

RESULT_PASS = "pass"
RESULT_WARNING = "warning"
RESULT_FAIL = "fail"

ALLOWED_RESULTS = [RESULT_PASS, RESULT_WARNING, RESULT_FAIL]


class Keptn:

    event_registry = {}

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
        Keptn.event_registry[keptn_event_type] = func

    def _post_cloud_event(self, body, headers):
        resp = requests.post(KEPTN_EVENT_ENDPOINT, data=body, headers=headers)
        print(resp)

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
        config_service = os.environ["CONFIGURATION_SERVICE"]
        if project and not service and not stage:
            # get project resource
            api_endpoint = f"{config_service}/v1/project/{project}/resource/{resource_name}"
        elif project and stage and not service:
            # get stage resource
            api_endpoint = f"{config_service}/v1/project/{project}/stage/{stage}/resource/{resource_name}"
        else:
            # get service resource
            api_endpoint = f"{config_service}/v1/project/{project}/stage/{stage}/service/{service}/resource/{resource_name}"

        response = requests.get(api_endpoint)

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
