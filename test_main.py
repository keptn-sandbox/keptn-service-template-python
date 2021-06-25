import pytest
import json
import requests
from cloudevents.http import from_http, CloudEvent, to_structured

from main import deployment_triggered
from keptn import KeptnUnitTestHelper


def test_deployment_triggered():
    KeptnUnitTestHelper.on('deployment.triggered', deployment_triggered)

    # load clouevent from file
    cloudevent = KeptnUnitTestHelper.load_cloudevent_from_file('test-events/deployment.triggered.json')
    
    keptn = KeptnUnitTestHelper(cloudevent)
    keptn.handle_cloud_event()

    assert len(keptn.cloud_events_sent) == 2, "2 CloudEvents have been sent"
    assert keptn.cloud_events_sent[0]['type'] == "sh.keptn.event.deployment.started"
    assert keptn.cloud_events_sent[1]['type'] == "sh.keptn.event.deployment.finished"
