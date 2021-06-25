import os
import json
import time

import requests
from flask import Flask, request
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
    
    def send_task_started_cloudevent(self, data=None, message="", result=RESULT_PASS, status=STATUS_SUCCEEDED):
        return self._send_cloud_event(self.sh_keptn_context, "sh.keptn.event." + self.task_name + ".started", message, result, status, data)

    def send_task_finished_cloudevent(self, data=None, message="", result=RESULT_PASS, status=STATUS_SUCCEEDED):
        return self._send_cloud_event(self.sh_keptn_context, "sh.keptn.event." + self.task_name + ".finished", message, result, status, data)
    
    def send_task_status_changed_cloudevent(self, data=None, message="", result=RESULT_PASS, status=STATUS_SUCCEEDED):
        return self._send_cloud_event(self.sh_keptn_context, "sh.keptn.event." + self.task_name + ".status.changed", message, result, status, data)



"""
KeptnUnitTestHelper is a Keptn class specifically for unit testing Keptn integrations
"""
class KeptnUnitTestHelper(Keptn):

    def __init__(self, event):
        super().__init__(event)
        self.cloud_events_sent = []

    def _post_cloud_event(self, body, headers):
        self.cloud_events_sent.append(from_http(headers, body))

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
