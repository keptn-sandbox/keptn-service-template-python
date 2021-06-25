# Test Resources

This folder represents the config-repo hosted by Keptn's configuration-service. You can put any files into this folder for projects, stages and services. Here is an example structure (with the related commands that you would use in production):

* `test_resources` (current folder)
  * `${PROJECT_NAME}` # equiv. to keptn create project ${PROJECT_NAME}
    * `shipyard.yaml` # keptn add-resource --project=${PROJECT_NAME} --resource=shipyard.yaml
    * `File123.json` # keptn add-resource --project=${PROJECT_NAME} --resource=File123.json
    * `${STAGE_NAME}` # stage is defined in shipyard.yaml
      * `Something.xml` # keptn add-resource --project=${PROJECT_NAME} --stage=${STAGE_NAME} --resource=Something.xml
      * `${SERVICE_NAME}` # keptn create service --project=${PROJECT_NAME} ${SERVICE_NAME}
        * `helm` 
          * `some-helm-chart.tgz` # keptn add-resource --project=${PROJECT_NAME} --stage=${STAGE_NAME} --service=${SERVICE_NAME} --resource=some-helm-chart.tgz --resourceUri=helm/some-helm-chart.tgz
        * `jmeter`
          * `basiccheck.jmx` # keptn add-resource --project=${PROJECT_NAME} --stage=${STAGE_NAME} --service=${SERVICE_NAME} --resource=basiccheck.jmx --resourceUri=jmeter/basiccheck.jmx
