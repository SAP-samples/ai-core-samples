# AIW Cloud Connector Demo

This example demonstrates how the connectivity service can be used from AI-Workbench in order to establish communication with external/on-premise systems.

## Build Docker Image

In order to build the docker image, make sure you have logged into the repository using `docker login aiwdemos.common.repositories.cloud.sap`. Afterwards use the following commands to build and push the image. Make sure you are pushing the correct version.

    cd images
    docker build . -f Dockerfile -t aiwdemos.common.repositories.cloud.sap/aiw-cc-demo:0.1
    docker push aiwdemos.common.repositories.cloud.sap/aiw-cc-demo:0.1

## Demo

Please check the notebook `demo.ipynb`.