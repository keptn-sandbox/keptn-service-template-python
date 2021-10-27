import os
import sys
import time

import requests
from flask import Flask, request
from cloudevents.http import from_http, CloudEvent, to_structured

from keptn import Keptn, start_polling

app = Flask(__name__)

# Port on which to listen for cloudevents
PORT = os.getenv('RCV_PORT', '8080')
#  Path to which cloudevents are sent
PATH = os.getenv('RCV_PATH', '/')


@app.route(PATH, methods=["POST"])
def gotevent():
    # create a CloudEvent
    event = from_http(request.headers, request.get_data())

    keptn = Keptn(event)
    keptn.handle_cloud_event()

    return "", 204


def deployment_triggered(keptn: Keptn, shkeptncontext: str, event, data):
    print("In deployment_triggered:")
    print("    ", shkeptncontext)
    print("    ", event)
    print("    ", data)

    keptn.send_task_started_cloudevent(message="Deployment Started")

    # keptn add-resource --project=XYZ --resource=project-resource.txt
    project_resource = keptn.get_project_resource('project-resource.txt')
    print("project_resource=", project_resource)


    # keptn add-resource --project=XYZ --stage=STAGE --resource=stage-resource.txt
    stage_resource = keptn.get_stage_resource('stage-resource.txt')
    print("stage_resource=", stage_resource)

    # keptn add-resource --project=XYZ --stage=STAGE --service=SERVICE --resource=service-resource.txt
    service_resource = keptn.get_service_resource('service-resource.txt')
    print("service_resource=", service_resource)

    time.sleep(5)

    keptn.send_task_finished_cloudevent(message="Deployment finished")


# register handler
Keptn.on('deployment.triggered', deployment_triggered)

if __name__ == "__main__":
    if "KEPTN_API_TOKEN" in os.environ and "KEPTN_ENDPOINT" in os.environ and os.environ["KEPTN_API_TOKEN"] and os.environ["KEPTN_ENDPOINT"]:
        print("Found environment variables KEPTN_ENDPOINT and KEPTN_API_TOKEN, polling events from API")
        thread = start_polling(os.environ["KEPTN_ENDPOINT"], os.environ["KEPTN_API_TOKEN"])

        if not thread:
            print("ERROR: Failed to start polling thread, exiting")
            sys.exit(1)

        print("Exit using CTRL-C")

        # wait til exit (e.g., using CTRL C)
        while True:
            try:
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("Exiting...")
                sys.exit(0)

    else:
        # run flask app with HTTP endpoint
        print("Running on port", PORT, "on path", PATH)
        app.run(host='0.0.0.0', port=PORT)
