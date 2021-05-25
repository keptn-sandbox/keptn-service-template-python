# from https://github.com/cloudevents/sdk-python/blob/master/samples/http-json-cloudevents/json_sample_server.py
import os
import time

import requests
from flask import Flask, request
from cloudevents.http import from_http, CloudEvent, to_structured

from keptn import Keptn

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

    time.sleep(10)

    keptn.send_task_finished_cloudevent(message="Deployment finished")



if __name__ == "__main__":

    Keptn.on('deployment.triggered', deployment_triggered)

    print("Running on port", PORT, "on path", PATH)
    app.run(port=PORT)
    
