# README

## :warning: This service is currently not maintained - please reach out to the Keptn community via https://slack.keptn.sh if you want to take ownership of this repository and update it to make it work with the latest version of Keptn :warning:

This is a POC of a Keptn Service Template written in Python. Follow the instructions below for writing your own Keptn integration.

Quick start:

1. In case you want to contribute your service to keptn-sandbox or keptn-contrib, make sure you have read and understood the [Contributing Guidelines](https://github.com/keptn-sandbox/contributing).
1. Click [Use this template](https://github.com/keptn-sandbox/keptn-service-template-python/generate) on top of the repository, or download the repo as a zip-file, extract it into a new folder named after the service you want to create (e.g., simple-service) 
1. Replace every occurrence of (docker) image names and tags from `keptnsandbox/keptn-service-template-python` to your docker organization and image name (e.g., `yourorganization/simple-service`)
1. Replace every occurrence of `keptn-service-template-python` with the name of your service (e.g., `simple-service`)
1. Optional (but recommended): Create a git repo (e.g., on `github.com/your-username/simple-service`)
1. Àdapt the [go.mod](go.mod) file and change `example.com/` to the actual package name (e.g., `github.com/your-username/simple-service`)
1. Add yourself to the [CODEOWNERS](CODEOWNERS) file
1. Initialize a git repository: 
  * `git init .`
  * `git add .`
  * `git commit -m "Initial Commit"`
1. Optional: Push your code an upstream git repo (e.g., GitHub) and adapt all links that contain `github.com` (e.g., to `github.com/your-username/simple-service`)
1. Figure out whether your Kubernetes Deployment requires [any RBAC rules or a different service-account](https://github.com/keptn-sandbox/contributing#rbac-guidelines), and adapt [deploy/service.yaml](deploy/service.yaml) accordingly (initial setup is `serviceAccountName: keptn-default`).
1. Last but not least: Remove this intro within the README file and make sure the README file properly states what this repository is about


# Example Usage


## Subscribe to a task

```python
def some_task_triggered(keptn: Keptn, shkeptncontext: str, event, data):
  # do something


Keptn.on('some_task.triggered', some_task_triggered)
```



## Subscribe to deployment triggered and send out started/finished events

```python



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
    
```

## Fetch a file from config-service

```python

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

    # do something with the files

    keptn.send_task_finished_cloudevent(message="Deployment finished")


```

---

# keptn-service-template-python
![GitHub release (latest by date)](https://img.shields.io/github/v/release/keptn-sandbox/keptn-service-template-python)
[![Go Report Card](https://goreportcard.com/badge/github.com/keptn-sandbox/keptn-service-template-python)](https://goreportcard.com/report/github.com/keptn-sandbox/keptn-service-template-python)

This implements a keptn-service-template-python for Keptn. If you want to learn more about Keptn visit us on [keptn.sh](https://keptn.sh)

## Compatibility Matrix

*Please fill in your versions accordingly*

| Keptn Version    | [keptn-service-template-python Docker Image](https://hub.docker.com/r/keptnsandbox/keptn-service-template-python/tags) |
|:----------------:|:----------------------------------------:|
|       0.6.1      | keptnsandbox/keptn-service-template-python:0.1.0 |
|       0.7.1      | keptnsandbox/keptn-service-template-python:0.1.1 |
|       0.7.2      | keptnsandbox/keptn-service-template-python:0.1.2 |

## Installation

The *keptn-service-template-python* can be installed as a part of [Keptn's uniform](https://keptn.sh).

### Deploy in your Kubernetes cluster

To deploy the current version of the *keptn-service-template-python* in your Keptn Kubernetes cluster, apply the [`deploy/service.yaml`](deploy/service.yaml) file:

```console
kubectl apply -f deploy/service.yaml
```

This should install the `keptn-service-template-python` together with a Keptn `distributor` into the `keptn` namespace, which you can verify using

```console
kubectl -n keptn get deployment keptn-service-template-python -o wide
kubectl -n keptn get pods -l run=keptn-service-template-python
```

### Up- or Downgrading

Adapt and use the following command in case you want to up- or downgrade your installed version (specified by the `$VERSION` placeholder):

```console
kubectl -n keptn set image deployment/keptn-service-template-python keptn-service-template-python=keptnsandbox/keptn-service-template-python:$VERSION --record
```

### Uninstall

To delete a deployed *keptn-service-template-python*, use the file `deploy/*.yaml` files from this repository and delete the Kubernetes resources:

```console
kubectl delete -f deploy/service.yaml
```

## Development

Development can be conducted using any GoLang compatible IDE/editor (e.g., Jetbrains GoLand, VSCode with Go plugins).

It is recommended to make use of branches as follows:

* `master`/`main` contains the latest potentially unstable version
* `release-*` contains a stable version of the service (e.g., `release-0.1.0` contains version 0.1.0)
* create a new branch for any changes that you are working on, e.g., `feature/my-cool-stuff` or `bug/overflow`
* once ready, create a pull request from that branch back to the `master` branch

When writing code, it is recommended to follow the coding style suggested by the [Golang community](https://github.com/golang/go/wiki/CodeReviewComments).

### Locally using Python

1. Install python3 and python3-venv (sometimes also called python3-virtualenv)
2. Create a virtual python environment: `virtualenv -p python3 venv`
3. Activate the virtual environment (you need to do this everytime before you start): `source venv/bin/ativate` (Note: the command might be different on Windows)
4. Install dependencies: `pip3 install -r requirements.txt`
5. Run :) `python3 main.py`

Example output:
```console
$ python3 main.py

Subscribing to deployment.triggered
Running on port 8080 on path /
 * Serving Flask app 'main' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
```

Note: This program is capable of running without the Keptn distributor. For this to work, you need to provide two environment variables:

```console
export KEPTN_ENDPOINT=http://1.2.3.4.nip.io/api
export KEPTN_API_TOKEN=<...>
```
See https://keptn.sh/docs/0.8.x/reference/cli/#authenticate-keptn-cli on how to get those.

Example output:
```console
$ python3 main.py

Subscribing to deployment.triggered
Found environment variables KEPTN_ENDPOINT and KEPTN_API_TOKEN, polling events from API
Starting to poll...
Exit using CTRL-C

Polling events for event type deployment.triggered
Polling events for event type deployment.triggered
Polling events for event type deployment.triggered
...
```

#### Common problems

**ModuleNotFoundError: No module named 'flask'**

You most likely forgot to create or activate the virtual environment or install dependencies.



### Using Docker

You can get started developing without installing Python, but using Docker:

```console
docker build . -t keptn-service-template-python:latest
docker run --rm -it -v "$(pwd)":"/app" keptn-service-template-python:latest bash
```

This spawns a new bash within a Python Container.

### Where to start

Your first entrypoint is [main.py](main.py). Within this file 
 you can add implementation for Keptn Cloud events.
 
To better understand all variants of Keptn CloudEvents, please look at the [Keptn Spec](https://github.com/keptn/spec).
 

### Common tasks

* Build the docker image: `docker build . -t keptnsandbox/keptn-service-template-python:dev` (Note: Ensure that you use the correct DockerHub account/organization)
* Run the docker image locally: `docker run --rm -it -p 8080:8080 keptnsandbox/keptn-service-template-python:dev`
* Push the docker image to DockerHub: `docker push keptnsandbox/keptn-service-template-python:dev` (Note: Ensure that you use the correct DockerHub account/organization)
* Deploy the service using `kubectl`: `kubectl apply -f deploy/`
* Delete/undeploy the service using `kubectl`: `kubectl delete -f deploy/`
* Watch the deployment using `kubectl`: `kubectl -n keptn get deployment keptn-service-template-python -o wide`
* Get logs using `kubectl`: `kubectl -n keptn logs deployment/keptn-service-template-python -f`
* Watch the deployed pods using `kubectl`: `kubectl -n keptn get pods -l run=keptn-service-template-python`
* Deploy the service using [Skaffold](https://skaffold.dev/): `skaffold run --default-repo=your-docker-registry --tail` (Note: Replace `your-docker-registry` with your DockerHub username; also make sure to adapt the image name in [skaffold.yaml](skaffold.yaml))


### Testing Cloud Events

We have dummy cloud-events in the form of [RFC 2616](https://ietf.org/rfc/rfc2616.txt) requests in the [test-events/](test-events/) directory. These can be easily executed using third party plugins such as the [Huachao Mao REST Client in VS Code](https://marketplace.visualstudio.com/items?itemName=humao.rest-client).

## Automation

### GitHub Actions: Automated Pull Request Review

This repo uses [reviewdog](https://github.com/reviewdog/reviewdog) for automated reviews of Pull Requests. 

You can find the details in [.github/workflows/reviewdog.yml](.github/workflows/reviewdog.yml).

### GitHub Actions: Unit Tests

This repo has automated unit tests for pull requests. 

You can find the details in [.github/workflows/tests.yml](.github/workflows/tests.yml).

### GH Actions/Workflow: Build Docker Images

This repo uses GH Actions and Workflows to test the code and automatically build docker images.

Docker Images are automatically pushed based on the configuration done in [.ci_env](.ci_env) and the two [GitHub Secrets](https://github.com/keptn-sandbox/keptn-service-template-python/settings/secrets/actions)
* `REGISTRY_USER` - your DockerHub username
* `REGISTRY_PASSWORD` - a DockerHub [access token](https://hub.docker.com/settings/security) (alternatively, your DockerHub password)

## How to release a new version of this service

It is assumed that the current development takes place in the master branch (either via Pull Requests or directly).

To make use of the built-in automation using GH Actions for releasing a new version of this service, you should

* branch away from master to a branch called `release-x.y.z` (where `x.y.z` is your version),
* write release notes in the [releasenotes/](releasenotes/) folder,
* check the output of GH Actions builds for the release branch, 
* verify that your image was built and pushed to DockerHub with the right tags,
* update the image tags in [deploy/service.yaml], and
* test your service against a working Keptn installation.

If any problems occur, fix them in the release branch and test them again.

Once you have confirmed that everything works and your version is ready to go, you should

* create a new release on the release branch using the [GitHub releases page](https://github.com/keptn-sandbox/keptn-service-template-python/releases), and
* merge any changes from the release branch back to the master branch.

## License

Please find more information in the [LICENSE](LICENSE) file.
